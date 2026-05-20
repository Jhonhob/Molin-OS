"""
MiroFish 完整管线适配器 — 接入阿里百炼 qwen3.6-plus

全流程:
  last30days/blogwatcher → 种子材料 → LLM实体提取 → LocalGraphStore → OASIS模拟 → 报告
"""

import sys
import os
import json
import time

MIROFISH_BACKEND = os.path.expanduser("~/Molin-OS/engine/mirofish/backend")

def _ensure_env():
    """确保MiroFish引擎可导入"""
    for p in [MIROFISH_BACKEND, os.path.join(MIROFISH_BACKEND, "app")]:
        if p not in sys.path:
            sys.path.insert(0, p)
    
    # 阿里百炼 qwen3.6-plus 配置
    os.environ.setdefault("LLM_API_KEY", "sk-2d3ce929a91f433cac2d7acffc7b9707")
    os.environ.setdefault("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    os.environ.setdefault("LLM_MODEL_NAME", "qwen3.6-plus")
    os.environ.setdefault("ZEP_API_KEY", "")


def build_graph_from_seed(seed_text: str, graph_name: str = "prediction") -> dict:
    """
    从种子材料构建知识图谱。
    返回: {"graph_id": str, "nodes": int, "edges": int, "types": list}
    """
    _ensure_env()
    from app.utils.llm_client import LLMClient
    from app.services.local_graph_store import LocalGraphStore

    llm = LLMClient()
    store = LocalGraphStore()
    graph_id = f"mirofish_{graph_name}_{int(time.time())}"
    store.clear_graph(graph_id)

    # LLM实体提取
    prompt = f"""从以下文本中提取所有关键实体及关系。
只输出JSON，不要其他内容。

{seed_text}

{{{{
  "entities": [
    {{{{"name": "实体名", "type": "organization|person|product|technology|regulation|concept|event", "summary": "一句话描述"}}}}
  ],
  "edges": [
    {{{{"source_name": "源实体名", "target_name": "目标实体名", "type": "关系类型", "fact": "关系事实"}}}}
  ]
}}}}"""

    response = llm.chat([{"role": "user", "content": prompt}], temperature=0.1)
    
    start = response.find("{")
    end = response.rfind("}")
    if start < 0 or end <= start:
        return {"graph_id": graph_id, "nodes": 0, "edges": 0, "types": [], "error": "LLM返回格式错误"}
    
    data = json.loads(response[start:end+1])
    entities = data.get("entities", [])
    edges = data.get("edges", [])
    
    # 过滤掉数值类实体
    entities = [e for e in entities if not e["name"].replace("%", "").replace(".", "").isdigit()]
    
    if entities:
        store.add_entities_batch(entities, graph_id)
    if edges:
        store.add_edges_batch(edges, graph_id)
    
    stats = store.get_stats(graph_id)
    return {
        "graph_id": graph_id,
        "nodes": stats["node_count"],
        "edges": stats["edge_count"],
        "types": stats["entity_types"],
    }


def run_full_prediction(topic: str, context: str = "") -> dict:
    """完整预测管线: 种子材料 → 图谱 → (未来: OASIS模拟) → 报告"""
    _ensure_env()
    from app.utils.llm_client import LLMClient
    from app.services.local_graph_store import LocalGraphStore
    from app.services.zep_tools import ZepToolsService

    llm = LLMClient()
    
    # 1. 构建种子材料
    seed = f"预测主题: {topic}\n"
    if context:
        seed += f"背景信息: {context}\n"
    seed += "\n(系统将基于以上主题进行知识图谱构建和预测推演)"
    
    # 2. 构建知识图谱
    print(f"[MiroFish] 构建知识图谱: {topic[:30]}...")
    graph_result = build_graph_from_seed(seed)
    print(f"[MiroFish] 图谱完成: {graph_result['nodes']}节点, {graph_result['edges']}边")
    
    # 3. 使用检索工具生成深度分析
    store = LocalGraphStore()
    tools = ZepToolsService()
    
    # 获取图谱统计
    stats = store.get_stats(graph_result["graph_id"])
    
    # 列出关键实体
    entities = store.get_all_nodes(graph_result["graph_id"])
    entity_summary = "\n".join([f"- {e['name']} ({e['labels'][0] if e['labels'] else '?'})" for e in entities[:20]])
    
    # 4. LLM综合分析
    analysis_prompt = f"""你是一位首席分析师。基于以下知识图谱进行深度预测分析。

预测主题: {topic}
背景信息: {context or '无'}
    知识图谱: {stats['node_count']}个实体, {stats['edge_count']}条关系, 类型: {stats['entity_types']}

关键实体:
{entity_summary}

请输出完整的预测分析报告，包含:
1. 核心判断（1-2句话）
2. 关键实体分析（每个实体的角色和影响）
3. 关系网络推演（实体间的关键互动）
4. 情景预测（基准/乐观/悲观）
5. 行动建议
6. 不确定性提示"""

    report = llm.chat([{"role": "user", "content": analysis_prompt}], temperature=0.5)
    
    return {
        "topic": topic,
        "运行模式": "完整模式（LLM实体提取+知识图谱+深度分析）",
        "graph_id": graph_result["graph_id"],
        "实体数": stats["node_count"],
        "关系数": stats["edge_count"],
        "实体类型": stats["entity_types"],
        "final_report": report,
    }


# ── 替代 predictor.py 中的 predict() full mode ──

async def predict_full(topic: str, context: str = "") -> dict:
    """完整模式入口（供 predictor.py 调用）"""
    return run_full_prediction(topic, context)


if __name__ == "__main__":
    # 测试
    import json
    result = run_full_prediction("2026年下半年AI Agent竞争格局", 
                                  "OpenAI GPT-5发布, Anthropic Claude 4, DeepSeek R2开源")
    print(f"\n主题: {result['topic']}")
    print(f"图谱: {result['实体数']}实体 / {result['关系数']}关系")
    print(f"报告预览: {result['final_report'][:300]}...")
