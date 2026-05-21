"""墨译·本地化 Worker：多语言适配、文化本地化、繁简转换、本地化质量审核"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class LocalizationWorker(WorkerAgent):
    worker_id = "localization_worker"
    description = "墨译 Worker：多语言本地化、繁简转换、质量审核"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
