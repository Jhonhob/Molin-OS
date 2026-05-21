"""墨料·教育内容 Worker：招生文案、课程描述、案例包装、教育行业内容产出"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import ExecutionPlan, WorkerAgent


class EduContentWorker(WorkerAgent):
    worker_id = "edu_content_worker"
    description = "墨料 Worker：招生文案、课程包装、教育内容产出"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]) -> ExecutionPlan:
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
