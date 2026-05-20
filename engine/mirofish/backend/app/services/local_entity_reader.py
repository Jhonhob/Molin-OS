"""
本地实体读取与过滤服务
======================
替代原 zep_entity_reader.py（使用 LocalGraphStore 而非 Zep Cloud）

提供与 ZepEntityReader 完全相同的接口和数据类。
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field

from .local_graph_store import LocalGraphStore, EntityNode, FilteredEntities
from ..utils.logger import get_logger

logger = get_logger('mirofish.local_entity_reader')


class LocalEntityReader:
    """
    本地实体读取与过滤服务
    替代 ZepEntityReader，使用 SQLite 而非 Zep Cloud。

    主要功能：
    1. 从本地图谱读取所有节点
    2. 筛选符合类型的实体
    3. 获取每个实体的相关边和关联节点
    """

    def __init__(self, api_key: Optional[str] = None):
        # api_key 参数保留以兼容调用方，实际使用本地存储
        self.store = LocalGraphStore()
        logger.info("本地实体读取服务已初始化（SQLite替代Zep Cloud）")

    def get_all_nodes(self, graph_id: str) -> List[Dict[str, Any]]:
        """获取图谱的所有节点"""
        logger.info(f"获取图谱 {graph_id} 的所有节点...")
        nodes = self.store.get_all_nodes(graph_id)
        logger.info(f"共获取 {len(nodes)} 个节点")
        return nodes

    def get_all_edges(self, graph_id: str) -> List[Dict[str, Any]]:
        """获取图谱的所有边"""
        logger.info(f"获取图谱 {graph_id} 的所有边...")
        edges = self.store.get_all_edges(graph_id)
        logger.info(f"共获取 {len(edges)} 条边")
        return edges

    def get_node_edges(self, node_uuid: str) -> List[Dict[str, Any]]:
        """获取指定节点的所有相关边"""
        return self.store.get_node_edges(node_uuid)

    def filter_defined_entities(
        self,
        graph_id: str,
        defined_entity_types: Optional[List[str]] = None,
        enrich_with_edges: bool = True,
    ) -> FilteredEntities:
        """筛选出符合预定义实体类型的节点"""
        return self.store.filter_defined_entities(
            graph_id=graph_id,
            defined_entity_types=defined_entity_types,
            enrich_with_edges=enrich_with_edges,
        )

    def get_entity_with_context(
        self,
        graph_id: str,
        entity_uuid: str,
    ) -> Optional[EntityNode]:
        """获取单个实体及其完整上下文（边和关联节点）"""
        node = self.store.get_node_by_uuid(entity_uuid)
        if not node:
            return None

        edges = self.store.get_node_edges(entity_uuid)
        all_nodes = self.store.get_all_nodes(graph_id)
        node_map = {n["uuid"]: n for n in all_nodes}

        related_edges = []
        related_node_uuids: Set[str] = set()

        for edge in edges:
            if edge["source_node_uuid"] == entity_uuid:
                related_edges.append({
                    "direction": "outgoing",
                    "edge_name": edge["name"],
                    "fact": edge["fact"],
                    "target_node_uuid": edge["target_node_uuid"],
                })
                related_node_uuids.add(edge["target_node_uuid"])
            else:
                related_edges.append({
                    "direction": "incoming",
                    "edge_name": edge["name"],
                    "fact": edge["fact"],
                    "source_node_uuid": edge["source_node_uuid"],
                })
                related_node_uuids.add(edge["source_node_uuid"])

        related_nodes = []
        for ruid in related_node_uuids:
            if ruid in node_map:
                rn = node_map[ruid]
                related_nodes.append({
                    "uuid": rn["uuid"],
                    "name": rn["name"],
                    "labels": rn["labels"],
                    "summary": rn.get("summary", ""),
                })

        return EntityNode(
            uuid=node["uuid"],
            name=node["name"],
            labels=node["labels"],
            summary=node["summary"],
            attributes=node["attributes"],
            related_edges=related_edges,
            related_nodes=related_nodes,
        )

    def get_entities_by_type(
        self,
        graph_id: str,
        entity_type: str,
        enrich_with_edges: bool = True,
    ) -> List[EntityNode]:
        """获取指定类型的所有实体"""
        result = self.filter_defined_entities(
            graph_id=graph_id,
            defined_entity_types=[entity_type],
            enrich_with_edges=enrich_with_edges,
        )
        return result.entities
