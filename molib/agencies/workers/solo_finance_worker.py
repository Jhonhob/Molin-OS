"""墨财·财务 Worker：流水记录、成本核算、API费用追踪、月报生成、预算控制"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import ExecutionPlan, WorkerAgent


class SoloFinanceWorker(WorkerAgent):
    worker_id = "solo_finance_worker"
    description = "墨财 Worker：流水记录、成本核算、API追踪、月报预算"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]) -> ExecutionPlan:
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
