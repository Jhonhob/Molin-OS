"""墨策·策略 Worker：战略分析、产品决策、商业模式评估、增长飞轮设计"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import ExecutionPlan, WorkerAgent


class SoloStrategyWorker(WorkerAgent):
    worker_id = "solo_strategy_worker"
    description = "墨策 Worker：战略分析、产品决策、商业模式评估"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]) -> ExecutionPlan:
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
