"""墨数·数据 Worker：跨域数据汇总、BI报表、KPI看板、数据分析、效果追踪"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class SoloDataWorker(WorkerAgent):
    worker_id = "solo_data_worker"
    description = "墨数 Worker：跨域数据、BI报表、KPI看板、效果追踪"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
