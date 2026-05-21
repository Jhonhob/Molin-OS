"""墨技·技术 Worker：全栈开发、系统部署、DevOps运维、AI能力集成(dev+devops+ai三合一)"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class DevInfraWorker(WorkerAgent):
    worker_id = "dev_infra_worker"
    description = "墨技 Worker：全栈开发、系统部署、DevOps(dev+devops+ai合并)"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
