"""
本地图谱记忆更新服务（替代 ZepGraphMemoryUpdater）
==================================================
将模拟中的Agent活动日志追加到本地SQLite存储而非Zep Cloud。
所有活动记录保存在 graph_store.db 的 simulation_logs 表中。
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from queue import Queue, Empty

from .local_graph_store import LocalGraphStore
from ..config import Config
from ..utils.logger import get_logger
from ..utils.locale import get_locale, set_locale

logger = get_logger('mirofish.local_graph_memory_updater')


@dataclass
class AgentActivity:
    """Agent活动记录（与Zep版完全一致）"""
    platform: str
    agent_id: int
    agent_name: str
    action_type: str
    action_args: Dict[str, Any]
    round_num: int
    timestamp: str


class ZepGraphMemoryUpdater:
    """
    本地图谱记忆更新服务
    替代原 zep_graph_memory_updater.py（不再需要 Zep Cloud）。

    将模拟中的Agent活动记录存入本地SQLite。
    """

    def __init__(self, graph_id: str):
        self.graph_id = graph_id
        self.store = LocalGraphStore()
        self._init_table()
        logger.info(f"本地记忆更新服务已初始化 (graph={graph_id})")

    def _init_table(self):
        """初始化活动日志表"""
        import sqlite3
        conn = sqlite3.connect(self.store.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                graph_id TEXT,
                platform TEXT,
                agent_id INTEGER,
                agent_name TEXT,
                action_type TEXT,
                action_args TEXT,
                round_num INTEGER,
                timestamp TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sim_logs_graph ON simulation_logs(graph_id)")
        conn.commit()
        conn.close()

    def add_activity(self, activity: AgentActivity):
        """记录一条Agent活动"""
        import sqlite3
        conn = sqlite3.connect(self.store.db_path)
        conn.execute(
            """INSERT INTO simulation_logs (graph_id, platform, agent_id, agent_name, action_type, action_args, round_num, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (self.graph_id, activity.platform, activity.agent_id, activity.agent_name,
             activity.action_type, json.dumps(activity.action_args, ensure_ascii=False),
             activity.round_num, activity.timestamp)
        )
        conn.commit()
        conn.close()

    def get_activities(self, round_num: Optional[int] = None, limit: int = 100) -> List[Dict]:
        """查询活动日志"""
        import sqlite3
        conn = sqlite3.connect(self.store.db_path)
        conn.row_factory = sqlite3.Row
        if round_num is not None:
            rows = conn.execute(
                "SELECT * FROM simulation_logs WHERE graph_id=? AND round_num=? ORDER BY id DESC LIMIT ?",
                (self.graph_id, round_num, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM simulation_logs WHERE graph_id=? ORDER BY id DESC LIMIT ?",
                (self.graph_id, limit)
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class ZepGraphMemoryManager:
    """图谱记忆管理器（本地SQLite版 — 替代Zep Cloud）"""

    _updaters: Dict[str, ZepGraphMemoryUpdater] = {}

    @classmethod
    def create_updater(cls, simulation_id: str, graph_id: str) -> ZepGraphMemoryUpdater:
        updater = ZepGraphMemoryUpdater(graph_id)
        cls._updaters[simulation_id] = updater
        return updater

    @classmethod
    def get_updater(cls, simulation_id: str) -> Optional[ZepGraphMemoryUpdater]:
        return cls._updaters.get(simulation_id)
