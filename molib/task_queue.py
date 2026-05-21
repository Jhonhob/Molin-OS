"""
LiteTaskQueue — 纯 SQLite 本地异步任务队列引擎
=====================================================
Molin-OS 工业级稳定性的基石：Hermes 大脑永不阻塞。

Hermes（大脑）调用 push_task() 发工单后立即返回，
后台 Worker 轮询 pop_pending_task() 执行耗时操作。
完全本地化，零外部依赖，与 SQLite 共生。

用法：
    from molib.task_queue import LiteTaskQueue
    q = LiteTaskQueue()
    task_id = q.push_task("mo_xiu", "web_search", {"url": "..."})
    # ... 后台 Worker 自动取走并执行 ...
"""

import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Any


class LiteTaskQueue:
    """轻量级 SQLite 任务队列 — 状态机：pending → running → completed/failed"""

    DEFAULT_DB_PATH = Path(__file__).parent.parent / "vault" / "tasks.db"

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or self.DEFAULT_DB_PATH)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ── 内部初始化 ──────────────────────────────

    def _init_db(self):
        """初始化极简任务表（幂等）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_queue (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    worker_name TEXT    NOT NULL,
                    skill_id    TEXT    NOT NULL,
                    payload     JSON    NOT NULL,
                    status      TEXT    DEFAULT 'pending',
                    result      TEXT,
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                    started_at  DATETIME,
                    finished_at DATETIME
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_status_created
                ON task_queue(status, created_at)
            """)

    # ── 生产者 API（Hermes 调用）────────────────

    def push_task(self, worker_name: str, skill_id: str, payload: dict) -> int:
        """Hermes 调用：将耗时任务推入队列，立即返回 task_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO task_queue (worker_name, skill_id, payload) VALUES (?, ?, ?)",
                (worker_name, skill_id, json.dumps(payload, ensure_ascii=False)),
            )
            task_id = cursor.lastrowid
        return task_id

    def push_batch(self, tasks: list[tuple[str, str, dict]]) -> list[int]:
        """批量推入任务 [(worker_name, skill_id, payload), ...] → ids"""
        ids = []
        with sqlite3.connect(self.db_path) as conn:
            for worker_name, skill_id, payload in tasks:
                cursor = conn.execute(
                    "INSERT INTO task_queue (worker_name, skill_id, payload) VALUES (?, ?, ?)",
                    (worker_name, skill_id, json.dumps(payload, ensure_ascii=False)),
                )
                ids.append(cursor.lastrowid)
        return ids

    # ── 消费者 API（后台 Worker 调用）───────────

    def pop_pending_task(self) -> Optional[dict]:
        """后台轮询调用：获取一个待执行任务并锁定为 running"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM task_queue WHERE status='pending' "
                "ORDER BY created_at ASC LIMIT 1"
            )
            task = cursor.fetchone()

            if task:
                conn.execute(
                    "UPDATE task_queue SET status='running', started_at=CURRENT_TIMESTAMP "
                    "WHERE id=?",
                    (task["id"],),
                )
                return dict(task)
        return None

    def pop_pending_tasks(self, limit: int = 5) -> list[dict]:
        """批量取任务（用于并发 Worker）"""
        tasks = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM task_queue WHERE status='pending' "
                "ORDER BY created_at ASC LIMIT ?",
                (limit,),
            )
            for row in cursor.fetchall():
                conn.execute(
                    "UPDATE task_queue SET status='running', started_at=CURRENT_TIMESTAMP "
                    "WHERE id=?",
                    (row["id"],),
                )
                tasks.append(dict(row))
        return tasks

    # ── 状态更新 API ────────────────────────────

    def complete_task(self, task_id: int, result_data: Any, success: bool = True):
        """更新任务为 completed 或 failed"""
        status = "completed" if success else "failed"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE task_queue SET status=?, result=?, finished_at=CURRENT_TIMESTAMP "
                "WHERE id=?",
                (status, json.dumps(result_data, ensure_ascii=False), task_id),
            )

    def fail_task(self, task_id: int, error_msg: str):
        """快速标记失败（语法糖）"""
        self.complete_task(task_id, {"error": error_msg}, success=False)

    # ── 查询 API ────────────────────────────────

    def get_stats(self) -> dict:
        """获取队列统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM task_queue").fetchone()[0]
            by_status = {}
            for row in conn.execute(
                "SELECT status, COUNT(*) as cnt FROM task_queue GROUP BY status"
            ):
                by_status[row[0]] = row[1]
            oldest_pending = conn.execute(
                "SELECT created_at FROM task_queue WHERE status='pending' "
                "ORDER BY created_at ASC LIMIT 1"
            ).fetchone()

        return {
            "total": total,
            "by_status": by_status,
            "pending": by_status.get("pending", 0),
            "running": by_status.get("running", 0),
            "completed": by_status.get("completed", 0),
            "failed": by_status.get("failed", 0),
            "oldest_pending_age": (
                f"{(datetime.utcnow() - datetime.fromisoformat(oldest_pending[0])).total_seconds():.0f}s"
                if oldest_pending and oldest_pending[0]
                else "N/A"
            ),
        }

    def purge_completed(self, before_days: int = 7) -> int:
        """清理 N 天前的已完成/失败任务"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM task_queue WHERE status IN ('completed','failed') "
                "AND created_at < datetime('now', ?)",
                (f'-{before_days} days',),
            )
            return cursor.rowcount
