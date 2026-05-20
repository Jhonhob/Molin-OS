"""
本地知识图谱存储（SQLite替代Zep Cloud）
========================================
完整实现 ZepEntityReader / ZepToolsService 所需的全部接口。

3张核心表:
  - entities: 实体节点 (人/组织/概念等)
  - edges:    实体间关系
  - entity_types: 实体类型索引

种子材料 → LLM实体提取 → 写入SQLite → OASIS模拟读取
"""

import sqlite3
import json
import uuid
import os
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Callable, TypeVar
from dataclasses import dataclass, field
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger('mirofish.local_graph_store')

T = TypeVar('T')

# ── 数据类（与 zep_entity_reader 完全相同） ──

@dataclass
class EntityNode:
    """实体节点数据结构"""
    uuid: str
    name: str
    labels: List[str]
    summary: str
    attributes: Dict[str, Any]
    related_edges: List[Dict[str, Any]] = field(default_factory=list)
    related_nodes: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "labels": self.labels,
            "summary": self.summary,
            "attributes": self.attributes,
            "related_edges": self.related_edges,
            "related_nodes": self.related_nodes,
        }

    def get_entity_type(self) -> Optional[str]:
        for label in self.labels:
            if label not in ["Entity", "Node"]:
                return label
        return None


@dataclass
class FilteredEntities:
    """过滤后的实体集合"""
    entities: List[EntityNode]
    entity_types: Set[str]
    total_count: int
    filtered_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": [e.to_dict() for e in self.entities],
            "entity_types": list(self.entity_types),
            "total_count": self.total_count,
            "filtered_count": self.filtered_count,
        }


# ── SQLite 存储引擎 ──

class LocalGraphStore:
    """
    本地知识图谱存储引擎（SQLite）
    完全替代 Zep Cloud 的图谱功能。

    用法:
        store = LocalGraphStore()
        store.add_entity(name="马斯克", type="person", summary="...")
        store.add_edge("马斯克", "OpenAI", type="lawsuit")
        nodes = store.get_all_nodes("graph_id")
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # 默认存储在 engine/mirofish/data/ 目录
            base = Path(__file__).parent.parent.parent
            db_path = str(base / "data" / "graph_store.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()
        logger.info(f"本地图谱存储已初始化: {db_path}")

    def _get_conn(self) -> sqlite3.Connection:
        """获取数据库连接（线程安全，自动创建）"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def _init_db(self):
        """初始化数据库表结构"""
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS entity_types (
                type TEXT PRIMARY KEY,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS entities (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL REFERENCES entity_types(type),
                summary TEXT DEFAULT '',
                attributes TEXT DEFAULT '{}',
                graph_id TEXT DEFAULT 'default',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS edges (
                uuid TEXT PRIMARY KEY,
                source_uuid TEXT NOT NULL REFERENCES entities(uuid),
                target_uuid TEXT NOT NULL REFERENCES entities(uuid),
                type TEXT NOT NULL,
                fact TEXT DEFAULT '',
                attributes TEXT DEFAULT '{}',
                graph_id TEXT DEFAULT 'default',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
            CREATE INDEX IF NOT EXISTS idx_entities_graph ON entities(graph_id);
            CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_uuid);
            CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_uuid);
            CREATE INDEX IF NOT EXISTS idx_edges_graph ON edges(graph_id);
        """)
        conn.commit()

    # ── 实体操作 ──

    def add_entity(
        self,
        name: str,
        type: str = "Entity",
        summary: str = "",
        attributes: Optional[Dict[str, Any]] = None,
        graph_id: str = "default",
    ) -> str:
        """添加一个实体节点。返回 uuid。"""
        conn = self._get_conn()
        eid = str(uuid.uuid4())

        # 确保 entity_type 存在
        conn.execute(
            "INSERT OR IGNORE INTO entity_types (type) VALUES (?)",
            (type,)
        )

        conn.execute(
            """INSERT INTO entities (uuid, name, type, summary, attributes, graph_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (eid, name, type, summary, json.dumps(attributes or {}, ensure_ascii=False), graph_id)
        )
        conn.commit()
        logger.debug(f"添加实体: {name} ({type}) → {eid[:8]}")
        return eid

    def add_entities_batch(
        self,
        entities: List[Dict[str, Any]],
        graph_id: str = "default",
    ) -> List[str]:
        """批量添加实体。每个 entity 需包含: name, type, [summary, attributes]"""
        ids = []
        for ent in entities:
            eid = self.add_entity(
                name=ent["name"],
                type=ent.get("type", "Entity"),
                summary=ent.get("summary", ""),
                attributes=ent.get("attributes"),
                graph_id=graph_id,
            )
            ids.append(eid)
        return ids

    def get_all_nodes(self, graph_id: str = "default") -> List[Dict[str, Any]]:
        """获取图谱所有节点（等价于 ZepEntityReader.get_all_nodes）"""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM entities WHERE graph_id = ? ORDER BY name",
            (graph_id,)
        ).fetchall()

        nodes = []
        for row in rows:
            nodes.append({
                "uuid": row["uuid"],
                "name": row["name"],
                "labels": [row["type"], "Entity"],
                "summary": row["summary"],
                "attributes": json.loads(row["attributes"]) if row["attributes"] else {},
            })
        return nodes

    def get_node_by_uuid(self, node_uuid: str) -> Optional[Dict[str, Any]]:
        """获取单个节点"""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM entities WHERE uuid = ?", (node_uuid,)
        ).fetchone()
        if not row:
            return None
        return {
            "uuid": row["uuid"],
            "name": row["name"],
            "labels": [row["type"], "Entity"],
            "summary": row["summary"],
            "attributes": json.loads(row["attributes"]) if row["attributes"] else {},
        }

    # ── 边操作 ──

    def add_edge(
        self,
        source_name: str,
        target_name: str,
        type: str = "related_to",
        fact: str = "",
        attributes: Optional[Dict[str, Any]] = None,
        graph_id: str = "default",
    ) -> str:
        """
        添加一条关系边。通过实体名称查找 source/target uuid。
        如果实体不存在则自动创建。
        """
        conn = self._get_conn()

        # 查找或创建 source 实体
        row = conn.execute(
            "SELECT uuid FROM entities WHERE name = ? AND graph_id = ?",
            (source_name, graph_id)
        ).fetchone()
        if row:
            source_uuid = row["uuid"]
        else:
            source_uuid = self.add_entity(source_name, graph_id=graph_id)
            logger.info(f"自动创建实体: {source_name} → {source_uuid[:8]}")

        # 查找或创建 target 实体
        row = conn.execute(
            "SELECT uuid FROM entities WHERE name = ? AND graph_id = ?",
            (target_name, graph_id)
        ).fetchone()
        if row:
            target_uuid = row["uuid"]
        else:
            target_uuid = self.add_entity(target_name, graph_id=graph_id)
            logger.info(f"自动创建实体: {target_name} → {target_uuid[:8]}")

        eid = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO edges (uuid, source_uuid, target_uuid, type, fact, attributes, graph_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (eid, source_uuid, target_uuid, type, fact,
             json.dumps(attributes or {}, ensure_ascii=False), graph_id)
        )
        conn.commit()
        logger.debug(f"添加边: {source_name} --[{type}]--> {target_name} → {eid[:8]}")
        return eid

    def add_edges_batch(
        self,
        edges: List[Dict[str, Any]],
        graph_id: str = "default",
    ) -> List[str]:
        """批量添加边。每条边需包含: source_name, target_name, type, [fact]"""
        ids = []
        for edge in edges:
            eid = self.add_edge(
                source_name=edge["source_name"],
                target_name=edge["target_name"],
                type=edge.get("type", "related_to"),
                fact=edge.get("fact", ""),
                attributes=edge.get("attributes"),
                graph_id=graph_id,
            )
            ids.append(eid)
        return ids

    def get_all_edges(self, graph_id: str = "default") -> List[Dict[str, Any]]:
        """获取图谱所有边（等价于 ZepEntityReader.get_all_edges）"""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT e.*, s.name as source_name, t.name as target_name
               FROM edges e
               JOIN entities s ON e.source_uuid = s.uuid
               JOIN entities t ON e.target_uuid = t.uuid
               WHERE e.graph_id = ?""",
            (graph_id,)
        ).fetchall()

        edges = []
        for row in rows:
            edges.append({
                "uuid": row["uuid"],
                "name": row["type"],
                "fact": row["fact"],
                "source_node_uuid": row["source_uuid"],
                "target_node_uuid": row["target_uuid"],
                "source_node_name": row["source_name"],
                "target_node_name": row["target_name"],
                "attributes": json.loads(row["attributes"]) if row["attributes"] else {},
            })
        return edges

    def get_node_edges(self, node_uuid: str) -> List[Dict[str, Any]]:
        """获取指定节点的所有相关边"""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT e.*, s.name as source_name, t.name as target_name
               FROM edges e
               JOIN entities s ON e.source_uuid = s.uuid
               JOIN entities t ON e.target_uuid = t.uuid
               WHERE e.source_uuid = ? OR e.target_uuid = ?""",
            (node_uuid, node_uuid)
        ).fetchall()

        result = []
        for row in rows:
            result.append({
                "uuid": row["uuid"],
                "name": row["type"],
                "fact": row["fact"],
                "source_node_uuid": row["source_uuid"],
                "target_node_uuid": row["target_uuid"],
                "source_node_name": row["source_name"],
                "target_node_name": row["target_name"],
                "attributes": json.loads(row["attributes"]) if row["attributes"] else {},
            })
        return result

    # ── 高级查询（等价于 ZepEntityReader 方法） ──

    def filter_defined_entities(
        self,
        graph_id: str = "default",
        defined_entity_types: Optional[List[str]] = None,
        enrich_with_edges: bool = True,
    ) -> FilteredEntities:
        """筛选出符合预定义实体类型的节点"""
        all_nodes = self.get_all_nodes(graph_id)
        all_edges = self.get_all_edges(graph_id) if enrich_with_edges else []
        total_count = len(all_nodes)

        # 构建节点索引
        node_map = {n["uuid"]: n for n in all_nodes}

        filtered = []
        types_found = set()

        for node in all_nodes:
            labels = node.get("labels", [])
            custom_labels = [l for l in labels if l not in ["Entity", "Node"]]

            if not custom_labels:
                continue

            if defined_entity_types:
                matching = [l for l in custom_labels if l in defined_entity_types]
                if not matching:
                    continue
                entity_type = matching[0]
            else:
                entity_type = custom_labels[0]

            types_found.add(entity_type)

            entity = EntityNode(
                uuid=node["uuid"],
                name=node["name"],
                labels=labels,
                summary=node["summary"],
                attributes=node["attributes"],
            )

            if enrich_with_edges:
                related_edges = []
                related_node_uuids: Set[str] = set()

                for edge in all_edges:
                    if edge["source_node_uuid"] == node["uuid"]:
                        related_edges.append({
                            "direction": "outgoing",
                            "edge_name": edge["name"],
                            "fact": edge["fact"],
                            "target_node_uuid": edge["target_node_uuid"],
                        })
                        related_node_uuids.add(edge["target_node_uuid"])
                    elif edge["target_node_uuid"] == node["uuid"]:
                        related_edges.append({
                            "direction": "incoming",
                            "edge_name": edge["name"],
                            "fact": edge["fact"],
                            "source_node_uuid": edge["source_node_uuid"],
                        })
                        related_node_uuids.add(edge["source_node_uuid"])

                entity.related_edges = related_edges

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
                entity.related_nodes = related_nodes

            filtered.append(entity)

        logger.info(
            f"筛选完成: {total_count}总节点 → {len(filtered)}符合条件, "
            f"类型: {types_found}"
        )
        return FilteredEntities(
            entities=filtered,
            entity_types=types_found,
            total_count=total_count,
            filtered_count=len(filtered),
        )

    def get_entities_by_type(
        self,
        entity_type: str,
        graph_id: str = "default",
        enrich_with_edges: bool = True,
    ) -> List[EntityNode]:
        """按类型获取实体"""
        result = self.filter_defined_entities(
            graph_id=graph_id,
            defined_entity_types=[entity_type],
            enrich_with_edges=enrich_with_edges,
        )
        return result.entities

    # ── 统计 ──

    def get_stats(self, graph_id: str = "default") -> Dict[str, Any]:
        """获取图谱统计信息"""
        conn = self._get_conn()
        nodes = conn.execute(
            "SELECT COUNT(*) as c FROM entities WHERE graph_id = ?", (graph_id,)
        ).fetchone()[0]
        edges = conn.execute(
            "SELECT COUNT(*) as c FROM edges WHERE graph_id = ?", (graph_id,)
        ).fetchone()[0]
        types = conn.execute(
            "SELECT DISTINCT type FROM entities WHERE graph_id = ?", (graph_id,)
        ).fetchall()
        type_list = [r[0] for r in types]

        return {
            "graph_id": graph_id,
            "node_count": nodes,
            "edge_count": edges,
            "entity_types": type_list,
        }

    # ── 清理 ──

    def clear_graph(self, graph_id: str = "default"):
        """清空指定图谱的所有数据"""
        conn = self._get_conn()
        conn.execute("DELETE FROM edges WHERE graph_id = ?", (graph_id,))
        conn.execute("DELETE FROM entities WHERE graph_id = ?", (graph_id,))
        conn.commit()
        logger.info(f"图谱已清空: {graph_id}")

    def close(self):
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
