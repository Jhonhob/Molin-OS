"""墨测·AI评测 Worker：AI工具实测、功能对比、性价比评估、推荐榜单、测评报告"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class AiReviewWorker(WorkerAgent):
    worker_id = "ai_review_worker"
    description = "墨测 Worker：AI工具评测、功能对比、性价比评估"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
