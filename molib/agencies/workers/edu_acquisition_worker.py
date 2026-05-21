"""墨招·教育获客 Worker：广告投放策略、增长方案、招生线索获取、获客渠道管理"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import ExecutionPlan, WorkerAgent


class EduAcquisitionWorker(WorkerAgent):
    worker_id = "edu_acquisition_worker"
    description = "墨招 Worker：广告投放、增长策略、招生线索、获客渠道"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]) -> ExecutionPlan:
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
