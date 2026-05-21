"""墨播·直播运营 Worker：直播脚本、短视频策划、直播复盘、多平台分发(视频号/抖音/B站)"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class LiveOpsWorker(WorkerAgent):
    worker_id = "live_ops_worker"
    description = "墨播 Worker：直播运营、短视频策划、多平台分发"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
