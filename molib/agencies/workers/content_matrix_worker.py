"""墨笔·内容矩阵 Worker：个人IP全平台内容产出(公众号/小红书/知乎/B站)、品牌视觉、AI生图、配音、设计"""

from __future__ import annotations
from typing import Any, Dict
from molib.agencies.worker import WorkerAgent


class ContentMatrixWorker(WorkerAgent):
    worker_id = "content_matrix_worker"
    description = "墨笔 Worker：个人IP内容矩阵、全平台产出、品牌视觉、AI生图配音设计"
    available_tools = ["file_tool", "memory_tool", "web_tool"]
    deliverable_spec: Dict[str, Any] = {}

    async def build_plan(self, subtask: Dict[str, Any]):
        """LLM驱动的执行计划"""
        return await self._llm_build_plan(subtask)
