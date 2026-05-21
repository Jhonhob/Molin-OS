"""墨化·教育转化 Worker：Leads跟进、转化漏斗优化、话术A/B测试、报名率提升"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class EduConversionWorker(WorkerAgent):
    worker_id = "edu_conversion_worker"
    description = "墨化 Worker：Leads转化、漏斗优化、话术测试、报名率"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
