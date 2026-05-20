"""
本地图谱构建服务（替代Zep Cloud版）
====================================
使用LLM从文本中直接提取实体和关系，写入 LocalGraphStore。
替代原 graph_builder.py 的 Zep API 调用。

流程:
  种子文本 → LLM实体提取(结构化JSON) → 写入LocalGraphStore(SQLite) → OASIS模拟消费
"""

import os
import json
import uuid
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from ..config import Config
from ..models.task import TaskManager, TaskStatus
from .local_graph_store import LocalGraphStore
from .text_processor import TextProcessor
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from ..utils.locale import t, get_locale, set_locale

logger = get_logger('mirofish.local_graph_builder')


@dataclass
class GraphInfo:
    """图谱信息"""
    graph_id: str
    node_count: int
    edge_count: int
    entity_types: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "entity_types": self.entity_types,
        }


# ── LLM 实体提取 Prompt ──

ENTITY_EXTRACTION_PROMPT = """你是一个知识图谱实体提取专家。从以下文本中提取所有关键实体和它们之间的关系。

文本内容:
{text}

请按以下JSON格式输出（只输出JSON，不要其他内容）:
{{
  "entities": [
    {{"name": "实体名称", "type": "实体类型(person/organization/concept/event/product)", "summary": "一句话描述", "attributes": {{"key1": "value1"}}}}
  ],
  "edges": [
    {{"source_name": "源实体名称", "target_name": "目标实体名称", "type": "关系类型", "fact": "关系事实描述"}}
  ]
}}

要求:
1. 实体类型限于: person, organization, concept, event, product, technology, location
2. 关系类型尽量使用具体动词或介词短语（如: founded_by, invested_in, competitors, filed_lawsuit_against）
3. 每个实体提供简短的摘要(summary)
4. 属性(attributes)可以是任何有用信息（如职位、估值、时间等）
5. 如果文本中明显存在关系但没有显式写明，可以合理推断
6. 确保提取的实体和关系覆盖文本的主要信息
"""


class GraphBuilderService:
    """
    本地图谱构建服务
    使用LLM从文本中提取实体和关系，写入 LocalGraphStore。
    完全替代原 Zep Cloud 版的 graph_builder.py。
    """

    def __init__(self, api_key: Optional[str] = None):
        # api_key 保留以兼容调用方
        self.store = LocalGraphStore()
        self.llm = LLMClient()
        self.task_manager = TaskManager()
        logger.info("本地图谱构建服务已初始化（LLM实体提取+SQLite存储）")

    def build_graph_async(
        self,
        text: str,
        ontology: Optional[Dict[str, Any]] = None,
        graph_name: str = "MiroFish Graph",
        chunk_size: int = 3000,
        chunk_overlap: int = 200,
        batch_size: int = 3
    ) -> str:
        """异步构建图谱（接口与Zep版完全兼容）"""
        task_id = self.task_manager.create_task(
            task_type="graph_build",
            metadata={
                "graph_name": graph_name,
                "text_length": len(text),
            }
        )

        current_locale = get_locale()

        thread = threading.Thread(
            target=self._build_graph_worker,
            args=(task_id, text, graph_name, chunk_size, chunk_overlap, current_locale)
        )
        thread.daemon = True
        thread.start()

        return task_id

    def _build_graph_worker(
        self,
        task_id: str,
        text: str,
        graph_name: str,
        chunk_size: int,
        chunk_overlap: int,
        locale: str = 'zh'
    ):
        """图谱构建工作线程"""
        set_locale(locale)
        try:
            self.task_manager.update_task(
                task_id, status=TaskStatus.PROCESSING,
                progress=5, message=t('progress.startBuildingGraph')
            )

            # 1. 创建图谱ID
            graph_id = f"mirofish_{uuid.uuid4().hex[:16]}"
            self.task_manager.update_task(
                task_id, progress=10,
                message=f"创建图谱: {graph_id}"
            )

            # 2. 文本分块（如果文本太长）
            chunks = TextProcessor.split_text(text, chunk_size, chunk_overlap)
            total_chunks = len(chunks)
            self.task_manager.update_task(
                task_id, progress=15,
                message=t('progress.textSplit', count=total_chunks)
            )

            # 3. LLM实体提取
            all_entities = []
            all_edges = []

            for i, chunk in enumerate(chunks):
                progress = 15 + int((i + 1) / total_chunks * 50)  # 15-65%
                self.task_manager.update_task(
                    task_id, progress=progress,
                    message=f"LLM实体提取中: 第{i+1}/{total_chunks}块"
                )

                try:
                    prompt = ENTITY_EXTRACTION_PROMPT.format(text=chunk[:2500])
                    response = self.llm.chat(
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1,
                    )

                    result = self._parse_llm_response(response)
                    if result:
                        all_entities.extend(result.get("entities", []))
                        all_edges.extend(result.get("edges", []))
                except Exception as e:
                    logger.warning(f"第{i+1}块实体提取失败: {e}")
                    continue

                time.sleep(0.5)  # 避免API限流

            # 4. 去重实体（按名称）
            seen = set()
            unique_entities = []
            for e in all_entities:
                name = e["name"].strip()
                if name.lower() not in seen:
                    seen.add(name.lower())
                    unique_entities.append(e)

            self.task_manager.update_task(
                task_id, progress=70,
                message=f"实体提取完成: {len(unique_entities)}个实体, {len(all_edges)}条关系"
            )

            # 5. 写入 LocalGraphStore
            self.store.add_entities_batch(unique_entities, graph_id=graph_id)
            self.store.add_edges_batch(all_edges, graph_id=graph_id)

            self.task_manager.update_task(
                task_id, progress=80,
                message=t('progress.fetchingGraphInfo')
            )

            # 6. 获取图谱信息
            stats = self.store.get_stats(graph_id=graph_id)
            graph_info = GraphInfo(
                graph_id=graph_id,
                node_count=stats["node_count"],
                edge_count=stats["edge_count"],
                entity_types=stats["entity_types"],
            )

            # 完成
            self.task_manager.complete_task(task_id, {
                "graph_id": graph_id,
                "graph_info": graph_info.to_dict(),
                "chunks_processed": total_chunks,
                "entities_extracted": len(unique_entities),
                "edges_extracted": len(all_edges),
            })

        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.task_manager.fail_task(task_id, error_msg)

    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析LLM返回的JSON"""
        # 尝试提取JSON部分
        try:
            # 查找第一个 { 和最后一个 }
            start = response.find('{')
            end = response.rfind('}')
            if start >= 0 and end > start:
                json_str = response[start:end + 1]
                return json.loads(json_str)
        except (json.JSONDecodeError, KeyError):
            pass
        return None

    # ── 兼容原接口的方法 ──

    def create_graph(self, name: str) -> str:
        """创建图谱（兼容原Zep版接口）"""
        return f"mirofish_{uuid.uuid4().hex[:16]}"

    def set_ontology(self, graph_id: str, ontology: Dict[str, Any]):
        """设置本体（Zep版需要，本地版不需要）"""
        logger.info(f"本地存储无需设置ontology (graph={graph_id})")
        pass

    def add_text_batches(self, graph_id: str, chunks: List[str], batch_size: int = 3, progress_callback=None) -> List[str]:
        """添加文本（兼容原接口，使用LLM提取）"""
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            if progress_callback:
                progress_callback(f"LLM提取中 {i+1}/{total}", (i+1)/total)
            try:
                prompt = ENTITY_EXTRACTION_PROMPT.format(text=chunk[:2500])
                response = self.llm.chat_completion(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                result = self._parse_llm_response(response)
                if result:
                    self.store.add_entities_batch(result.get("entities", []), graph_id)
                    self.store.add_edges_batch(result.get("edges", []), graph_id)
            except Exception as e:
                logger.warning(f"第{i+1}块处理失败: {e}")
        return []

    def get_graph_data(self, graph_id: str) -> Dict[str, Any]:
        """获取完整图谱数据"""
        nodes = self.store.get_all_nodes(graph_id)
        edges = self.store.get_all_edges(graph_id)
        return {
            "graph_id": graph_id,
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
        }
