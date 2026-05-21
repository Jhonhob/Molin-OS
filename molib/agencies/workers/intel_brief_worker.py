"""墨简·情报简报 Worker：周报生成、行业分析、竞品情报、趋势洞察、知识星球内容输出"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class IntelBriefWorker(WorkerAgent):
    worker_id = "intel_brief_worker"
    description = "墨简 Worker：情报周报、行业分析、竞品情报、知识星球"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
