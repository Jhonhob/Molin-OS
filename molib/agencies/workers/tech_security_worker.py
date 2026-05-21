"""墨卫·安全 Worker：纯技术安全审计、渗透测试、漏洞扫描、安全加固(非合规)"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class TechSecurityWorker(WorkerAgent):
    worker_id = "tech_security_worker"
    description = "墨卫 Worker：技术安全审计、渗透测试、漏洞扫描"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
