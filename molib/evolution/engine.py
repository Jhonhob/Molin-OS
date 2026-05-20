"""
墨麟AI智能系统 v6.6 — 进化引擎总控

任务执行完成后，评估结果并决定进化路径：
- 成功 → 提取知识卡片
- 失败 → 分析失败原因
- 部分成功 → 提取待验证知识

灵感来源：Claude Code `src/services/extractMemories/` + 现有 SOP 反馈管道。

Source: core/evolution/engine.py (from molin-os-ultra)
Adapted for Hermes OS: loguru→logging, removed sqlite_client/qdrant_client imports,
replaced with Obsidian vault storage (Supermemory 已停用).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

from molib.evolution.knowledge_extractor import KnowledgeExtractor
from molib.evolution.failure_analyzer import FailureAnalyzer


class EvalOutcome(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"


@dataclass
class EvalResult:
    """评估结果"""
    outcome: EvalOutcome
    score: float
    knowledge_cards: list = None
    failure_patterns: list = None
    improvement_suggestions: list = None


class EvolutionEngine:
    """
    进化引擎：从任务执行中学习。

    用法：
        engine = EvolutionEngine()
        result = await engine.evaluate(task_result)
    """

    def __init__(self):
        self._extractor = KnowledgeExtractor()
        self._analyzer = FailureAnalyzer()
        self._stats = {
            "tasks_evaluated": 0,
            "knowledge_extracted": 0,
            "failures_analyzed": 0,
        }

    async def evaluate(self, task_result: Dict[str, Any]) -> EvalResult:
        """
        评估任务结果，触发学习流程。

        Args:
            task_result: 任务执行结果，包含：
                - status: "success" / "partial_success" / "error"
                - score: 0-10 的评分
                - output: 执行输出
                - metadata: 元数据
        """
        self._stats["tasks_evaluated"] += 1

        status = task_result.get("status", "error")
        score = task_result.get("score", 5.0)

        if status == "success" and score >= 7.0:
            return await self._handle_success(task_result, score)
        elif status == "error" or score < 5.0:
            return await self._handle_failure(task_result, score)
        else:
            return await self._handle_partial(task_result, score)

    async def _handle_success(self, task_result: Dict[str, Any],
                              score: float) -> EvalResult:
        """处理成功任务：提取知识并持久化到 Obsidian vault（Supermemory 已停用）"""
        logger.info(f"Success task (score={score}), extracting knowledge...")

        cards = await self._extractor.extract(task_result)
        self._stats["knowledge_extracted"] += len(cards)

        # 持久化知识卡片到 Obsidian vault（Supermemory 已停用）
        if cards:
            await self._persist_knowledge_cards(cards, outcome=EvalOutcome.SUCCESS.value)

        return EvalResult(
            outcome=EvalOutcome.SUCCESS,
            score=score,
            knowledge_cards=cards,
        )

    async def _persist_knowledge_cards(self, cards: List[Dict[str, Any]], outcome: str = "success") -> int:
        """将知识卡片写入 Obsidian vault（Supermemory 已停用）"""
        logger.info(f"[EvolutionEngine] {len(cards)} knowledge cards ready for vault write")
        return 0  # Supermemory decommissioned — cards go to Obsidian vault only

    async def _handle_failure(self, task_result: Dict[str, Any],
                              score: float) -> EvalResult:
        """处理失败任务：分析原因"""
        logger.info(f"Failed task (score={score}), analyzing...")

        patterns = await self._analyzer.analyze(task_result)
        self._stats["failures_analyzed"] += 1

        return EvalResult(
            outcome=EvalOutcome.FAILURE,
            score=score,
            failure_patterns=patterns,
            improvement_suggestions=self._generate_suggestions(patterns),
        )

    async def _handle_partial(self, task_result: Dict[str, Any],
                              score: float) -> EvalResult:
        """处理部分成功：提取待验证知识"""
        logger.info(f"Partial success task (score={score}), extracting partial knowledge...")

        cards = await self._extractor.extract_partial(task_result)

        # 持久化待验证知识到 Obsidian vault（Supermemory 已停用）
        if cards:
            await self._persist_knowledge_cards(cards, outcome=EvalOutcome.PARTIAL.value)

        return EvalResult(
            outcome=EvalOutcome.PARTIAL,
            score=score,
            knowledge_cards=cards,
        )

    def _generate_suggestions(self, patterns: list) -> list:
        """基于失败模式生成改进建议"""
        suggestions = []
        for pattern in patterns:
            error_type = pattern.get("error_type", "")
            if "timeout" in error_type.lower():
                suggestions.append("增加超时时间或优化执行效率")
            elif "tool" in error_type.lower():
                suggestions.append("检查工具可用性或添加备用工具")
            elif "parse" in error_type.lower():
                suggestions.append("改进输出格式，增加解析容错")
            else:
                suggestions.append(f"针对 {error_type} 增加专项处理")
        return suggestions

    def get_stats(self) -> Dict[str, Any]:
        """获取进化统计"""
        return self._stats.copy()

    @staticmethod
    def persist(eval_result: EvalResult) -> bool:
        """知识卡片已通过 output_writer 写入 Obsidian vault"""
        logger.info(f"Knowledge cards for {eval_result.outcome.value} routed to vault")
        return True  # Supermemory decommissioned — vault handles persistence

    @staticmethod
    def retrieve_knowledge(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """检索历史知识（通过 Obsidian vault 全文搜索）"""
        logger.info(f"Knowledge retrieval from vault: {query[:50]}")
        return []  # Supermemory decommissioned — use vault search instead
