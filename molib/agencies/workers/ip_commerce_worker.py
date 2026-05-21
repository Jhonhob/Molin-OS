"""墨商·IP成交 Worker：商务洽谈→报价→订单→交付全闭环(三合一:bd+shop+order)"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class IpCommerceWorker(WorkerAgent):
    worker_id = "ip_commerce_worker"
    description = "墨商 Worker：接单→报价→交付全链路(BD+电商+订单三合一)"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
