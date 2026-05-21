#!/usr/bin/env python3
"""
记忆垃圾回收站 (Memory GC) — ChromaDB 知识蒸馏与物理清理
===========================================================
让 AI 学会「遗忘和总结」，保持向量数据库轻盈不膨胀。

工作原理：
1. 扫描 ChromaDB 中 N 天前的碎片记忆
2. 调用 LLM Summarize 浓缩为结构化知识点
3. 固化到 Obsidian Vault 作为永久冷存储
4. 从 ChromaDB 物理删除已浓缩的旧向量

运行方式：
    python scripts/memory_gc_job.py              # 默认 7 天阈值
    python scripts/memory_gc_job.py --days 14    # 14 天阈值
    python scripts/memory_gc_job.py --dry-run     # 仅预览，不执行

建议加入系统 crontab 每日凌晨执行：
    0 3 * * * cd /path/to/Molin-OS && python scripts/memory_gc_job.py >> vault/logs/gc.log 2>&1
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# 确保 molib 可导入
sys.path.insert(0, str(Path(__file__).parent.parent))


class MemoryGarbageCollector:
    """ChromaDB 记忆清理器 — 浓缩 + 固化 + 删除"""

    VAULT_OBSIDIAN_DIR = "consolidated_knowledge"
    CHROMA_PATH = "./vault/chroma_db"
    COLLECTION_NAME = "molin_memory"

    def __init__(self, chroma_path: Optional[str] = None, collection_name: Optional[str] = None):
        self.chroma_path = chroma_path or self.CHROMA_PATH
        self.collection_name = collection_name or self.COLLECTION_NAME
        self.obsidian_dir = Path("./vault/obsidian") / self.VAULT_OBSIDIAN_DIR
        self.obsidian_dir.mkdir(parents=True, exist_ok=True)

        self.chroma_client = None
        self.collection = None

    def _connect(self):
        """延迟连接 ChromaDB（仅在需要时）"""
        if self.chroma_client is not None:
            return

        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            self.collection = self.chroma_client.get_or_create_collection(self.collection_name)
        except ImportError:
            print("⚠️ chromadb 未安装，跳过 GC。pip install chromadb")
            self.chroma_client = False  # 标记为不可用
        except Exception as e:
            print(f"⚠️ ChromaDB 连接失败: {e}")
            self.chroma_client = False

    def run_consolidation(self, days_threshold: int = 7, dry_run: bool = False) -> dict:
        """
        执行记忆清理计划。

        Args:
            days_threshold: 清理多少天以前的记忆
            dry_run: 仅预览，不实际删除

        Returns:
            统计信息 dict
        """
        self._connect()
        if self.chroma_client is False:
            return {"status": "skipped", "reason": "chromadb unavailable"}

        print(f"🧹 记忆清理计划启动 (阈值: > {days_threshold} 天)\n")

        # 1. 获取所有记录
        try:
            all_docs = self.collection.get()
        except Exception as e:
            print(f"❌ 无法读取集合: {e}")
            return {"status": "error", "reason": str(e)}

        if not all_docs or not all_docs.get("ids"):
            print("📭 集合为空，无需清理。")
            return {"status": "ok", "deleted": 0, "consolidated": 0}

        # 2. 按时间戳过滤过期记录
        now = time.time()
        threshold_seconds = days_threshold * 86400
        old_ids = []
        old_texts = []
        kept_count = 0

        for doc_id, meta, text in zip(
            all_docs["ids"],
            all_docs.get("metadatas", [{}] * len(all_docs["ids"])),
            all_docs.get("documents", [""] * len(all_docs["ids"])),
        ):
            created_at = (meta or {}).get("created_at", 0)
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at).timestamp()
                except (ValueError, TypeError):
                    created_at = 0

            if created_at > 0 and (now - created_at) > threshold_seconds:
                old_ids.append(doc_id)
                old_texts.append(text)
            else:
                kept_count += 1

        if not old_ids:
            print(f"📭 无过期记忆（保留 {kept_count} 条在向量库中）。")
            return {"status": "ok", "deleted": 0, "consolidated": 0, "kept": kept_count}

        print(f"📊 发现 {len(old_ids)} 条过期记忆，{kept_count} 条保留。")

        # 3. 生成浓缩摘要
        summary = self._generate_summary(old_texts)

        # 4. 固化到 Obsidian
        date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
        file_path = self.obsidian_dir / f"knowledge_dump_{date_str}.md"

        if not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"---\ndate: {datetime.now().isoformat()}\ntype: 记忆沉淀\n"
                        f"source_count: {len(old_ids)}\ndays_threshold: {days_threshold}\n"
                        f"agent: xuanhu.autodream\ncategory: 知识\n---\n\n"
                        f"# {date_str} 记忆沉淀\n\n"
                        f"> 来源：{len(old_ids)} 条 {days_threshold} 天前的碎片记忆\n\n"
                        f"{summary}\n")
            print(f"📝 浓缩知识已写入: {file_path}")
        else:
            print(f"   [DRY RUN] 将写入: {file_path}")

        # 5. 从 ChromaDB 删除旧数据
        if not dry_run:
            try:
                self.collection.delete(ids=old_ids)
                print(f"🗑️ 已从 ChromaDB 物理删除 {len(old_ids)} 条旧记忆。")
            except Exception as e:
                print(f"❌ 删除失败: {e}")
                return {"status": "partial", "deleted": 0, "consolidated": len(old_ids), "error": str(e)}
        else:
            print(f"   [DRY RUN] 将删除 {len(old_ids)} 条记录。")

        return {
            "status": "ok",
            "deleted": len(old_ids),
            "consolidated": len(old_ids),
            "kept": kept_count,
            "output_file": str(file_path),
        }

    def _generate_summary(self, texts: list[str]) -> str:
        """生成浓缩摘要 — 优先用 LLM，不行则退化到简单拼接"""
        if not texts:
            return "（无内容）"

        combined = "\n\n---\n\n".join(texts)

        # 尝试调用 LLM 浓缩
        try:
            result = self._llm_summarize(combined)
            if result:
                return result
        except Exception as e:
            print(f"   ⚠️ LLM 浓缩失败，使用退化方案: {e}")

        # 退化方案：截取前 2000 字 + 统计信息
        preview = combined[:2000]
        return (
            f"## 知识碎片聚合\n\n"
            f"- 原始条目数: {len(texts)}\n"
            f"- 总字符数: {len(combined)}\n\n"
            f"## 原始内容摘要\n\n{preview}\n\n"
            f"> *注: LLM 浓缩未执行，此为原始数据拼接。*"
        )

    def _llm_summarize(self, text: str, max_chars: int = 8000) -> Optional[str]:
        """调用 LLM 进行知识浓缩"""
        # 优先使用阿里百炼 qwen3.6-plus
        for attempt in range(2):
            try:
                return self._summarize_via_qwen(text[:max_chars])
            except Exception:
                continue

        # 退化到 OpenAI 兼容接口
        try:
            return self._summarize_via_openai(text[:max_chars])
        except Exception:
            pass

        return None

    def _summarize_via_qwen(self, text: str) -> str:
        """阿里百炼 qwen3.6-plus 浓缩"""
        import os
        api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("DASHSCOPE_API_KEY", "")
        if not api_key:
            raise RuntimeError("无可用 API Key")

        import urllib.request
        import urllib.error

        data = json.dumps({
            "model": "qwen3.6-plus",
            "input": {
                "messages": [
                    {"role": "system", "content": "你是知识浓缩引擎。将多条碎片记忆提炼为结构化知识点。"},
                    {"role": "user", "content": f"请将以下记忆碎片浓缩为 3-5 个结构化知识点：\n\n{text}"},
                ]
            },
            "parameters": {"max_tokens": 1000},
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result["output"]["choices"][0]["message"]["content"]

    def _summarize_via_openai(self, text: str) -> str:
        """OpenAI 兼容接口浓缩"""
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

        if not api_key:
            raise RuntimeError("无可用 OpenAI API Key")

        import urllib.request
        import urllib.error

        data = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": "你是知识浓缩引擎。将多条碎片记忆提炼为结构化知识点。"},
                {"role": "user", "content": f"请将以下记忆碎片浓缩为 3-5 个结构化知识点：\n\n{text}"},
            ],
            "max_tokens": 1000,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]

    def get_db_stats(self) -> dict:
        """获取 ChromaDB 基本统计"""
        self._connect()
        if self.chroma_client is False:
            return {"status": "unavailable"}

        try:
            all_docs = self.collection.get()
            return {
                "status": "ok",
                "total_vectors": len(all_docs.get("ids", [])),
                "collection_name": self.collection_name,
                "chroma_path": self.chroma_path,
            }
        except Exception as e:
            return {"status": "error", "reason": str(e)}


# ── CLI 入口 ────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Molin-OS ChromaDB 记忆垃圾回收")
    parser.add_argument("--days", "-d", type=int, default=7, help="清理 N 天前的记忆（默认 7）")
    parser.add_argument("--dry-run", "-n", action="store_true", help="仅预览，不实际执行删除")
    parser.add_argument("--stats", action="store_true", help="仅显示 ChromaDB 统计信息")
    args = parser.parse_args()

    gc = MemoryGarbageCollector()

    if args.stats:
        stats = gc.get_db_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        sys.exit(0)

    result = gc.run_consolidation(days_threshold=args.days, dry_run=args.dry_run)

    if args.dry_run:
        print(f"\n[DRY RUN] 以上为预览。去掉 --dry-run 以实际执行。")

    print(f"\n结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
