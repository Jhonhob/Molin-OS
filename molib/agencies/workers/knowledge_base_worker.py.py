"""墨档·知识库 Worker：知识沉淀、文档管理、RAG检索优化、知识图谱维护"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import ExecutionPlan, WorkerAgent


class KnowledgeBaseWorker(WorkerAgent):
    worker_id = "knowledge_base_worker"
    description = "墨档 Worker：知识管理、文档沉淀、RAG检索"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]) -> ExecutionPlan:
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
