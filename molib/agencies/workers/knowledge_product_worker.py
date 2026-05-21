"""墨课·知识产品 Worker：知识付费课程设计、录播课程制作、训练营策划、知识产品定价"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import ExecutionPlan, WorkerAgent


class KnowledgeProductWorker(WorkerAgent):
    worker_id = "knowledge_product_worker"
    description = "墨课 Worker：知识付费产品、课程设计、训练营策划"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]) -> ExecutionPlan:
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
