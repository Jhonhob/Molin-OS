"""墨东·东南亚 Worker：马来西亚/新加坡市场探索、英文内容适配、东南亚Leads获取(低优先级占位)"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class SeaMarketWorker(WorkerAgent):
    worker_id = "sea_market_worker"
    description = "墨东 Worker：东南亚市场探索、英文适配(低优先级)"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
