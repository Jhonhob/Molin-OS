"""
原子数据总线 (Atomic Data Bus) — SQLite WAL 模式
=====================================================
彻底取代 relay/ 目录的文件共享机制。
SQLite WAL 模式提供行级锁、事务支持和并发读取，
消除「下游读取时上游覆盖写入」的文件竞态条件。

用法：
    from molib.data_bus import AtomicDataBus
    bus = AtomicDataBus()
    bus.write_pipe("key", "ziling", "yinyue", {"topic": "..."})
    data = bus.read_pipe("key")
    bus.clear_pipe("key")
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Any


class AtomicDataBus:
    """基于 SQLite WAL 的进程安全数据总线"""

    DEFAULT_DB_PATH = Path(__file__).parent.parent / "relay" / "bus.db"

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or self.DEFAULT_DB_PATH)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_bus()

    def _init_bus(self):
        """开启 WAL 模式，支持高并发读写"""
        with self._get_conn() as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=30000;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_bus (
                    bus_key       TEXT PRIMARY KEY,
                    source_worker TEXT NOT NULL,
                    target_domain TEXT NOT NULL,
                    payload       TEXT NOT NULL,
                    ttl_seconds   INTEGER DEFAULT 3600,
                    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_bus_target_created
                ON data_bus(target_domain, created_at)
            """)

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ── 核心 API ────────────────────────────────

    def write_pipe(
        self,
        bus_key: str,
        source_worker: str,
        target_domain: str,
        payload: dict,
        ttl_seconds: int = 3600,
    ):
        """上游 Worker 安全写入（UPSERT 语义，旧数据自动覆盖）"""
        with self._get_conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO data_bus
                   (bus_key, source_worker, target_domain, payload, ttl_seconds, updated_at)
                   VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (bus_key, source_worker, target_domain,
                 json.dumps(payload, ensure_ascii=False), ttl_seconds),
            )

    def read_pipe(self, bus_key: str) -> Optional[dict]:
        """下游 Worker 安全读取（不影响上游写入）"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT source_worker, target_domain, payload, created_at "
                "FROM data_bus WHERE bus_key = ?",
                (bus_key,),
            )
            row = cursor.fetchone()
            if row:
                return {
                    "bus_key": bus_key,
                    "source_worker": row["source_worker"],
                    "target_domain": row["target_domain"],
                    "payload": json.loads(row["payload"]),
                    "created_at": row["created_at"],
                }
        return None

    def read_pending(self, target_domain: str, limit: int = 20) -> list[dict]:
        """读取指定域下所有待消费数据"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT bus_key, source_worker, payload, created_at "
                "FROM data_bus WHERE target_domain = ? "
                "ORDER BY created_at ASC LIMIT ?",
                (target_domain, limit),
            )
            return [
                {
                    "bus_key": r["bus_key"],
                    "source_worker": r["source_worker"],
                    "payload": json.loads(r["payload"]),
                    "created_at": r["created_at"],
                }
                for r in cursor.fetchall()
            ]

    def clear_pipe(self, bus_key: str):
        """数据消费完毕后清理，防止脏数据驻留"""
        with self._get_conn() as conn:
            conn.execute("DELETE FROM data_bus WHERE bus_key = ?", (bus_key,))

    def clear_expired(self) -> int:
        """清理过期的 TTL 数据"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "DELETE FROM data_bus WHERE "
                "datetime(created_at, '+' || ttl_seconds || ' seconds') < datetime('now')"
            )
            return cursor.rowcount

    # ── 查询 API ────────────────────────────────

    def stats(self) -> dict:
        """总线统计信息"""
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM data_bus").fetchone()[0]
            by_domain = {}
            for row in conn.execute(
                "SELECT target_domain, COUNT(*) as cnt FROM data_bus GROUP BY target_domain"
            ):
                by_domain[row["target_domain"]] = row["cnt"]
            expired = self.clear_expired()
        return {
            "total_keys": total,
            "by_domain": by_domain,
            "expired_cleared": expired,
        }

    def purge(self) -> int:
        """清空总线"""
        with self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM data_bus")
            return cursor.rowcount
