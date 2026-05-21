"""墨留·教育留存 Worker：学员续费管理、社群运营、NPS追踪、流失预警(教育专属)"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import ExecutionPlan, WorkerAgent


class EduRetentionWorker(WorkerAgent):
    worker_id = "edu_retention_worker"
    description = "墨留 Worker：学员留存、续费管理、社群运营、流失预警"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]) -> ExecutionPlan:
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
