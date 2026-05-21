"""墨法·法务 Worker：合同审查、合规检查、风险评估、NDA生成、隐私合规(legal+secure合规合并)"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class SoloLegalWorker(WorkerAgent):
    worker_id = "solo_legal_worker"
    description = "墨法 Worker：合同审查、合规检查、风险评估(法务+安全合规)"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
