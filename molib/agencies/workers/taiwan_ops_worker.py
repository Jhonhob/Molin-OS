"""墨台·台湾运营 Worker：台湾市场内容运营、繁体适配、台区社媒矩阵、Leads转化"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class TaiwanOpsWorker(WorkerAgent):
    worker_id = "taiwan_ops_worker"
    description = "墨台 Worker：台湾市场运营、繁体适配、台区社媒"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
