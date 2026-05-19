"""
Molin-OS Memory Retriever — 统一记忆检索入口 (v2.0)

Agent 通过此模块检索历史知识做决策。
双源检索：
1. Obsidian（结构化知识）
2. Agentic Stack MemoryLayers（四层记忆: working/episodic/semantic/personal）

用法:
    from molib.memory.retriever import retrieve_context

    context = retrieve_context(
        query="转化率提升策略",
        agent_name="edu",
        top_k=5
    )
"""

from typing import Optional, List
import os

from .obsidian_reader import search_obsidian, search_section
from .ranker import rank_results, deduplicate, filter_by_type

# ── Hermes FTS5 集成 (本地免费全文检索，热路由) ─────────────────────

_HAS_HERMES_FTS5 = False
_HERMES_STATE_DB_PATH = os.path.expanduser("~/.hermes/state.db")


def _init_hermes_fts5() -> bool:
    """检查 Hermes FTS5 数据库是否可访问。"""
    global _HAS_HERMES_FTS5
    if _HAS_HERMES_FTS5:
        return True
    if os.path.isfile(_HERMES_STATE_DB_PATH):
        _HAS_HERMES_FTS5 = True
        return True
    _HAS_HERMES_FTS5 = False
    return False


def _search_hermes_fts5(query: str, limit: int = 20) -> list:
    """从 Hermes FTS5 (本地 SQLite 全文索引) 检索会话记录。

    热路由 - 零成本，优先使用。
    直接查询 ~/.hermes/state.db 的 FTS5 索引，无需加载 Hermes 模块。
    使用 SQLite FTS5 全文搜索语法。

    Returns:
        与 retriever 格式兼容的结果列表
    """
    if not _init_hermes_fts5():
        return []

    import sqlite3

    try:
        conn = sqlite3.connect(_HERMES_STATE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # FTS5 搜索：匹配消息内容，按 rank 排序
        cursor.execute("""
            SELECT
                m.rowid,
                m.session_id,
                m.role,
                m.content,
                m.timestamp,
                s.title AS session_title,
                rank
            FROM messages_fts AS f
            JOIN messages AS m ON f.rowid = m.rowid
            LEFT JOIN sessions AS s ON m.session_id = s.id
            WHERE messages_fts MATCH ?
            AND m.role NOT IN ('tool', 'function')
            ORDER BY rank
            LIMIT ?
        """, (query, limit))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            content = (row["content"] or "")[:500]
            session_title = row["session_title"] or ""
            session_id = row["session_id"] or ""
            rank_val = row["rank"] or 0

            from datetime import datetime

            ts = row["timestamp"]
            if ts and isinstance(ts, (int, float)):
                date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            else:
                date_str = str(ts or "")[:10]

            results.append({
                "source": "hermes_fts5",
                "agent": "system",
                "date": date_str,
                "title": "[FTS5] " + (session_title[:60] if session_title else "Session " + session_id[:8]),
                "content": content,
                "score": int(abs(rank_val) * 100) if rank_val else 10,
                "filepath": "hermes_session://" + session_id,
                "sections": [{"heading": "对话 (" + (session_title or "?"), "content": content}],
                "session_id": session_id,
            })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:limit]

    except Exception:
        return []


# ── Agentic Stack 集成 ─────────────────────────────────────────────

try:
    from molib.agentic_stack.memory import MemoryLayers as _MemoryLayers
    from molib.agentic_stack.lesson_lifecycle import LessonLifecycle as _LessonLifecycle
    from molib.agentic_stack.lesson_lifecycle import LessonStatus as _LessonStatus
    _HAS_AGENTIC_STACK = True
except ImportError:
    _HAS_AGENTIC_STACK = False


# ── AI 摘要生成 ────────────────────────────────────────────────────

def _call_llm_summarize(query: str, context_text: str) -> str:
    """
    调用 LLM 生成检索摘要。
    使用标准库 urllib 调用当前配置的 LLM API。
    """
    import json
    import os
    import urllib.request

    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return context_text[:800] if len(context_text) > 800 else context_text

    api_base = "https://api.deepseek.com" if "DEEPSEEK_API_KEY" in os.environ else "https://api.openai.com/v1"
    model = "deepseek-chat" if "DEEPSEEK_API_KEY" in os.environ else "gpt-4o-mini"

    prompt = (
        f"你是一个知识检索摘要助手。请根据查询和检索结果，生成简洁的摘要。\n\n"
        f"用户查询: {query}\n\n"
        f"检索结果:\n{context_text[:3000]}\n\n"
        f"要求:\n"
        f"1. 提取与查询最相关的3-5条关键信息\n"
        f"2. 每个信息附带来源\n"
        f"3. 用中文回复\n"
        f"4. 控制在300字以内"
    )

    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 600,
    })

    try:
        req = urllib.request.Request(
            f"{api_base}/chat/completions",
            data=payload.encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
    except Exception:
        return context_text[:800] if len(context_text) > 800 else context_text


# ── Agentic Stack MemoryLayers 查询 ─────────────────────────────────

def _query_agentic_memory(query: str, layer: Optional[str] = None,
                          top_k: int = 5) -> list:
    """
    从 Agentic Stack MemoryLayers 检索。

    Args:
        query: 检索查询
        layer: 指定层 (working/episodic/semantic/personal)，None=全部
        top_k: 返回上限

    Returns:
        与 retriever 格式兼容的结果列表
    """
    if not _HAS_AGENTIC_STACK:
        return []

    ml = _MemoryLayers()
    query_lower = query.lower()

    results = []
    layers_to_check = [layer] if layer else ["working", "episodic", "semantic", "personal"]

    for layer_name in layers_to_check:
        entries = ml.query(layer=layer_name)
        for entry in entries:
            # 简单关键词匹配评分
            score = 0
            content_lower = entry.content.lower()

            for word in query_lower.split():
                if word in content_lower:
                    score += 10

            # 加入显著性评分
            score += entry.significance * 5

            if score > 0:
                results.append({
                    "source": f"agentic_memory/{layer_name}",
                    "agent": entry.source or "system",
                    "date": entry.timestamp[:10] if entry.timestamp else "",
                    "title": f"[{layer_name}] {entry.content[:60]}...",
                    "content": entry.content,
                    "score": int(score),
                    "filepath": f"~/.hermes/agentic_memory/{layer_name}.jsonl",
                    "sections": [{"heading": f"Memory ({layer_name})", "content": entry.content}],
                })

    # Lessons 查询
    try:
        ll = _LessonLifecycle()
        graduated = [l for l in ll.list(status=_LessonStatus.GRADUATED) if query_lower in l.content.lower()]
        for lesson in graduated:
            results.append({
                "source": "agentic_memory/lessons",
                "agent": lesson.source or "system",
                "date": lesson.created_at[:10] if lesson.created_at else "",
                "title": f"[lesson] {lesson.content[:60]}...",
                "content": lesson.content,
                "score": int(lesson.significance * 50),
                "filepath": "~/.hermes/agentic_memory/lessons.jsonl",
                "sections": [{"heading": f"Lesson ({lesson.category})", "content": lesson.content}],
            })
    except Exception:
        pass

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]


# ── 统一检索入口 ────────────────────────────────────────────────────

def retrieve_context(
    query: str,
    agent_name: Optional[str] = None,
    top_k: int = 5,
    section_filter: Optional[list] = None,
    days_back: int = 30,
    use_llm_summary: bool = False,
    include_agentic_memory: bool = True,
) -> dict:
    """
    统一记忆检索入口 (v2.0 — 支持 Agentic Stack MemoryLayers)。

    Args:
        query: 检索问题
        agent_name: Agent ID (如 content, finance)，None = 全部
        top_k: 返回结果上限
        section_filter: 区块类型过滤 (如 ["洞察", "结论"])
        days_back: 回溯天数
        use_llm_summary: 是否用 LLM 生成摘要
        include_agentic_memory: 是否包含 Agentic 记忆

    Returns:
        {
            "query": str,
            "results": [{
                "source": "obsidian" | "agentic_memory/...",
                "agent": str,
                "date": str,
                "title": str,
                "content": str,
                "score": int,
                "filepath": str,
                "sections": [{"heading", "content"}]
            }],
            "summary": str,
            "total_found": int,
            "sources": ["obsidian", "agentic_memory"]  # v2.0 新增
        }
    """
    sources_used = []

    # 1. Hermes FTS5 热路由 (本地免费，优先使用)
    fts5_results = _search_hermes_fts5(query, limit=top_k * 2)
    if fts5_results:
        sources_used.append("hermes_fts5")

    # 2. Obsidian 检索 (结构化知识)
    obsidian_results = search_obsidian(
        query=query,
        agent_name=agent_name,
        days_back=days_back,
        top_k=top_k * 2,
    )
    if obsidian_results:
        sources_used.append("obsidian")

    # 3. Agentic Stack MemoryLayers 检索 (冷备份)
    agentic_results = []
    if include_agentic_memory and _HAS_AGENTIC_STACK:
        agentic_results = _query_agentic_memory(query, top_k=top_k)
        if agentic_results:
            sources_used.append("agentic_memory")

    # 4. 合并 + 去重
    all_results = rank_results(query, fts5_results + obsidian_results + agentic_results)
    all_results = deduplicate(all_results)

    # 4. 区块过滤
    if section_filter:
        all_results = filter_by_type(all_results, section_filter)

    # 5. 截断
    final_results = all_results[:top_k]

    # 6. 生成摘要
    if use_llm_summary and final_results:
        raw_text = "\n---\n".join(
            f"[{r['source']}] {r['title']}\n{r['content'][:300]}"
            for r in final_results[:3]
        )
        summary = _call_llm_summarize(query, raw_text)
    else:
        summary = _build_summary(query, final_results)

    return {
        "query": query,
        "agent": agent_name,
        "results": final_results,
        "summary": summary,
        "total_found": len(final_results),
        "sources": sources_used,  # v2.0 新增
    }


def retrieve_insights(
    topic: str,
    agent_name: Optional[str] = None,
    top_k: int = 3,
) -> dict:
    """
    只检索洞察/结论/可复用知识（Agent 决策专用）。

    相当于:
        retrieve_context(query, section_filter=["洞察", "结论", "可复用知识"])
    """
    return search_section(
        query=topic,
        agent_name=agent_name,
        section_type="洞察|结论|可复用知识|Key Learnings|insight",
    )


def _build_summary(query: str, results: list) -> str:
    """构建给 Agent 的上下文摘要"""
    if not results:
        return "未找到相关历史记录。"

    lines = [f"## 历史参考（检索: {query}）\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. {r['title']} ({r['source']}, {r['agent']}, {r['date']})")

        sections = r.get("matched_sections") or r.get("sections", [])
        for s in sections[:3]:
            heading = s.get("heading", "")
            content = s.get("content", "")[:300]
            lines.append(f"**{heading}**: {content.strip()[:100]}...")

        lines.append("")

    return "\n".join(lines)


def test():
    """简单自测"""
    print("=" * 50)
    print("Memory Retriever v2.0 自测")
    print("=" * 50)

    # 测试 Agentic Stack 集成
    if _HAS_AGENTIC_STACK:
        print("\n✅ Agentic Stack MemoryLayers 已集成")
        from molib.agentic_stack.memory import MemoryLayers
        ml = MemoryLayers()
        print(f"   记忆层: {list(ml._layers.keys())}")
        print(f"   条目数: {sum(len(v) for v in ml._layers.values())}")
    else:
        print("\n⚠️  Agentic Stack 未安装，只使用 Obsidian 检索")

    # 测试基本检索
    result = retrieve_context("财务", agent_name="finance", top_k=3)
    print(f"\n检索: {result['query']}")
    print(f"Agent: {result['agent']}")
    print(f"结果数: {result['total_found']}")
    print(f"数据源: {result['sources']}")
    if result['results']:
        first = result['results'][0]
        print(f"第一条: {first['title']} (score={first['score']})")

    print(f"\n摘要预览:\n{result['summary'][:500]}")


if __name__ == "__main__":
    test()
