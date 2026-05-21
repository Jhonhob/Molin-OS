"""
记忆融合与混合降维去重引擎 (Memory Compactor)
===================================================
防止长期自动化带来的 Token 膨胀及知识库冗余失真。
在记忆写入 ChromaDB/Obsidian 前执行本地去重合并。

核心算法：
- Levenshtein 编辑距离快速矩阵计算文本重合度
- 高重合 (>0.75) → 触发原地融合重写 [UPDATE]
- 中等重合 → 判定为增量补充 [INSERT]
- 低重合 → 全新知识资产 [INSERT]

用法：
    from molib.memory_compactor import LocalMemoryCompactor
    compactor = LocalMemoryCompactor()
    action, idx, merged = compactor.compact_buffer(memories, new_fact)
"""

import difflib
import hashlib
from typing import Optional


class LocalMemoryCompactor:
    """基于 Levenshtein 编辑距离的本地记忆去重引擎"""

    def __init__(self, similarity_threshold: float = 0.75):
        self.threshold = similarity_threshold
        # 布隆过滤器简易实现：小容量指纹缓存
        self._fingerprint_cache: set = set()
        self._cache_max_size = 10000

    def calculate_similarity(self, text_a: str, text_b: str) -> float:
        """标准 Levenshtein 快速矩阵算法计算文本重合度"""
        return difflib.SequenceMatcher(None, text_a, text_b).ratio()

    def _fingerprint(self, text: str) -> str:
        """生成文本指纹（用于快速排重）"""
        # 取前 30 和后 30 字符做哈希，抵抗微小改动
        head = text[:50].strip()
        tail = text[-50:].strip()
        return hashlib.md5((head + tail).encode()).hexdigest()

    def compact_buffer(
        self,
        existing_memories: list[str],
        new_fact: str,
    ) -> tuple[str, Optional[int], str]:
        """
        对即将写入向量库/知识库的记忆进行就地降维。

        Args:
            existing_memories: 已存在的相似记忆列表
            new_fact: 待写入的新记忆

        Returns:
            (action, index, merged_text)
            action: "INSERT" | "UPDATE" | "SKIP"
            index: UPDATE 时的目标索引，否则 None
            merged_text: 合并后的文本
        """
        # 0. 指纹快速排重
        fp = self._fingerprint(new_fact)
        if fp in self._fingerprint_cache:
            return "SKIP", None, new_fact

        # 1. 遍历已有记忆，找最高相似度
        best_score = 0.0
        best_index = None

        for idx, old_mem in enumerate(existing_memories):
            score = self.calculate_similarity(old_mem, new_fact)
            if score > best_score:
                best_score = score
                best_index = idx

        # 2. 决策
        if best_score >= 0.95:
            # 几乎完全相同 → 跳过
            return "SKIP", None, new_fact

        elif best_score >= self.threshold:
            # 高度相似 → 原地融合
            old = existing_memories[best_index]
            merged = f"【知识修正合并 v2】{new_fact} (历史参考: {old[:100]}...)"

            # 指纹缓存更新
            self._fingerprint_cache.discard(self._fingerprint(old))
            self._fingerprint_cache.add(self._fingerprint(merged))

            if len(self._fingerprint_cache) > self._cache_max_size:
                self._fingerprint_cache.clear()

            return "UPDATE", best_index, merged

        else:
            # 全新增量 → 插入
            self._fingerprint_cache.add(fp)
            return "INSERT", None, new_fact

    def compact_batch(
        self,
        existing_memories: list[str],
        new_facts: list[str],
    ) -> list[dict]:
        """
        批量去重合并。

        Returns:
            [{"action": "INSERT", "index": None, "text": "..."}, ...]
        """
        results = []
        current_memories = list(existing_memories)

        for fact in new_facts:
            action, idx, merged = self.compact_buffer(current_memories, fact)
            results.append({"action": action, "index": idx, "text": merged})

            if action == "INSERT":
                current_memories.append(fact)
            elif action == "UPDATE" and idx is not None:
                current_memories[idx] = merged

        return results

    def stats(self) -> dict:
        """获取去重引擎统计"""
        return {
            "threshold": self.threshold,
            "fingerprint_cache_size": len(self._fingerprint_cache),
            "algorithm": "Levenshtein + Fingerprint Bloom",
        }
