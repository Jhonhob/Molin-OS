"""墨雷·GitHub雷达 Worker：AI开源项目监控、技术趋势扫描、竞品代码分析、Star趋势追踪"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class GithubRadarWorker(WorkerAgent):
    worker_id = "github_radar_worker"
    description = "墨雷 Worker：GitHub项目监控、技术趋势、竞品扫描"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
