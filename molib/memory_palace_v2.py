"""
自适应记忆管理器 v2 (Memory Palace V2)
=========================================
借鉴 Mem0 (mem0ai/mem0) 的自进化记忆能力。
在感知到新信息时自动判断：
  - INSERT: 全新知识 → 新增
  - UPDATE: 对旧知识的修订 → 原地覆盖
  - MERGE:  与已有记忆可合并 → 融合
  - IGNORE: 重复信息 → 跳过

完全本地优先，基于 ChromaDB + SQLite，不依赖任何外部 API。

用法：
    from molib.memory_palace_v2 import AdaptiveMemoryManager
    mem = AdaptiveMemoryManager()
    action, memory_id, text = mem.ingest("元瑶", "用户偏好3C产品")
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Optional


class AdaptiveMemoryManager:
    """
    自进化长期记忆管理器 — 感知新信息时智能判断增删改。
    """

    def __init__(
        self,
        chroma_collection=None,
        similarity_threshold: float = 0.75,
        merge_threshold: float = 0.85,
    ):
        """
        Args:
            chroma_collection: ChromaDB collection 对象（可选，不传则仅用本地存储）
            similarity_threshold: 相似度阈值 —— 超过视为 UPDATE/MERGE
            merge_threshold: 合并阈值 —— 超过视为 UPDATE（覆盖），否则 MERGE（融合）
        """
        self.collection = chroma_collection
        self.similarity_threshold = similarity_threshold
        self.merge_threshold = merge_threshold

        # 本地 SQLite 索引（不依赖 ChromaDB）
        import sqlite3
        db_path = Path(__file__).parent.parent / "vault" / "memory_index.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        self._init_local_db()

    def _init_local_db(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_index (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding_hash TEXT,
                created_at REAL,
                updated_at REAL,
                access_count INTEGER DEFAULT 0
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_mem_agent
            ON memory_index(agent_id, updated_at)
        """)
        self._conn.commit()

    # ── 核心 API：智能摄入 ─────────────────────

    def ingest(
        self,
        agent_id: str,
        new_fact: str,
    ) -> tuple[str, Optional[str], str]:
        """
        感知新事实时的智能决策。

        Args:
            agent_id: Agent 标识（如 '元瑶', '紫灵'）
            new_fact: 新认知的事实

        Returns:
            (action, memory_id, final_text)
            action: "INSERT" | "UPDATE" | "MERGE" | "IGNORE"
            memory_id: 目标记忆 ID（UPDATE/MERGE 时），INSERT 时为 None
            final_text: 最终存储的文本
        """
        # 1. 检索该 Agent 已有相关记忆
        existing = self._find_similar(agent_id, new_fact)

        if not existing:
            # 全新知识 → INSERT
            mem_id = self._insert(agent_id, new_fact)
            print(f"🧠 [{agent_id}] INSERT 新记忆: {new_fact[:50]}...")
            return "INSERT", mem_id, new_fact

        best = existing[0]
        similarity = best["similarity"]

        if similarity >= 0.95:
            # 几乎完全相同 → IGNORE
            print(f"🧠 [{agent_id}] IGNORE 重复记忆 (相似度={similarity:.2f})")
            self._touch(best["id"])
            return "IGNORE", best["id"], best["content"]

        elif similarity >= self.merge_threshold:
            # 高度相似 → MERGE（融合）
            merged = f"【合并记忆 v2】{new_fact}\n(参考旧版: {best['content'][:100]}...)"
            self._update(best["id"], agent_id, merged)
            print(f"🧠 [{agent_id}] MERGE 融合记忆 (相似度={similarity:.2f}) → id={best['id']}")
            return "MERGE", best["id"], merged

        elif similarity >= self.similarity_threshold:
            # 中等相似 → UPDATE（覆盖）
            self._update(best["id"], agent_id, new_fact)
            print(f"🧠 [{agent_id}] UPDATE 覆盖记忆 (相似度={similarity:.2f}) → id={best['id']}")
            return "UPDATE", best["id"], new_fact

        else:
            # 低相似 → INSERT
            mem_id = self._insert(agent_id, new_fact)
            print(f"🧠 [{agent_id}] INSERT 新记忆 (相似度={similarity:.2f})")
            return "INSERT", mem_id, new_fact

    def ingest_batch(
        self,
        agent_id: str,
        facts: list[str],
    ) -> list[dict]:
        """
        批量摄入新事实。

        Returns:
            [{"action": "INSERT", "memory_id": "...", "text": "..."}, ...]
        """
        results = []
        for fact in facts:
            action, mem_id, text = self.ingest(agent_id, fact)
            results.append({"action": action, "memory_id": mem_id, "text": text})
        return results

    # ── 内部方法 ───────────────────────────────

    def _find_similar(self, agent_id: str, fact: str, top_k: int = 3) -> list[dict]:
        """检索与事实最相似的已有记忆"""
        results = []

        # 优先用 ChromaDB
        if self.collection is not None:
            try:
                chroma_results = self.collection.query(
                    query_texts=[fact],
                    n_results=top_k,
                    where={"agent_id": agent_id},
                )
                if chroma_results["ids"] and chroma_results["ids"][0]:
                    for i, mem_id in enumerate(chroma_results["ids"][0]):
                        dist = chroma_results["distances"][0][i] if chroma_results.get("distances") else 1.0
                        results.append({
                            "id": mem_id,
                            "content": chroma_results["documents"][0][i],
                            "similarity": 1.0 - min(dist, 1.0),
                            "source": "chromadb",
                        })
                    return sorted(results, key=lambda x: x["similarity"], reverse=True)
            except Exception:
                pass

        # 降级：SQLite + Levenshtein
        from molib.memory_compactor import LocalMemoryCompactor
        compactor = LocalMemoryCompactor()

        cursor = self._conn.execute(
            "SELECT id, content FROM memory_index WHERE agent_id=? ORDER BY updated_at DESC LIMIT ?",
            (agent_id, top_k * 3),
        )
        for row in cursor.fetchall():
            sim = compactor.calculate_similarity(row["content"], fact)
            results.append({
                "id": row["id"],
                "content": row["content"],
                "similarity": sim,
                "source": "sqlite",
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def _insert(self, agent_id: str, content: str) -> str:
        """插入新记忆"""
        mem_id = hashlib.md5(f"{agent_id}:{content}:{time.time()}".encode()).hexdigest()[:16]
        now = time.time()

        self._conn.execute(
            "INSERT INTO memory_index (id, agent_id, content, created_at, updated_at) VALUES (?,?,?,?,?)",
            (mem_id, agent_id, content, now, now),
        )
        self._conn.commit()

        if self.collection is not None:
            try:
                self.collection.add(
                    ids=[mem_id],
                    documents=[content],
                    metadatas=[{"agent_id": agent_id, "created_at": now}],
                )
            except Exception:
                pass

        return mem_id

    def _update(self, mem_id: str, agent_id: str, content: str):
        """更新已有记忆"""
        now = time.time()

        self._conn.execute(
            "UPDATE memory_index SET content=?, updated_at=?, access_count=access_count+1 WHERE id=?",
            (content, now, mem_id),
        )
        self._conn.commit()

        if self.collection is not None:
            try:
                self.collection.update(
                    ids=[mem_id],
                    documents=[content],
                    metadatas=[{"agent_id": agent_id, "updated_at": now}],
                )
            except Exception:
                pass

    def _touch(self, mem_id: str):
        """标记记忆被访问"""
        self._conn.execute(
            "UPDATE memory_index SET access_count=access_count+1, updated_at=? WHERE id=?",
            (time.time(), mem_id),
        )
        self._conn.commit()

    # ── 查询 API ───────────────────────────────

    def get_by_agent(self, agent_id: str, limit: int = 20) -> list[dict]:
        """获取某 Agent 的所有记忆"""
        cursor = self._conn.execute(
            "SELECT * FROM memory_index WHERE agent_id=? ORDER BY updated_at DESC LIMIT ?",
            (agent_id, limit),
        )
        return [dict(r) for r in cursor.fetchall()]

    def stats(self) -> dict:
        """记忆统计"""
        total = self._conn.execute("SELECT COUNT(*) FROM memory_index").fetchone()[0]
        by_agent = {}
        for row in self._conn.execute(
            "SELECT agent_id, COUNT(*) as cnt FROM memory_index GROUP BY agent_id"
        ):
            by_agent[row["agent_id"]] = row["cnt"]
        return {
            "total_memories": total,
            "by_agent": by_agent,
            "similarity_threshold": self.similarity_threshold,
            "merge_threshold": self.merge_threshold,
        }
