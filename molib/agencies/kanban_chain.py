"""
墨麟OS — Hermes Kanban WorkerChain 适配器

将 WorkerChain 的执行映射到 Hermes Kanban 任务板，获得：
- 心跳检测 (Kanban dispatcher 周期性健康检查)
- 僵尸回收 (超时 Worker 自动释放)
- 重试预算 (每任务自动重试)
- 依赖图 (上下游 parent-child 链)
- WebUI 可视化看板

CLI 使用示例:
    hermes kanban create "营销文案" --assignee content_writer
    hermes kanban create "设计落地页" --assignee designer --parent <task_id>
"""

import json
import logging
import os
import subprocess
import time
from typing import Optional

logger = logging.getLogger(__name__)

_KANBAN_BOARD = "molin-workerchain"


class KanbanChain:
    """Hermes Kanban 驱动的容错 WorkerChain"""

    def __init__(self, board_slug: str = _KANBAN_BOARD):
        self.board_slug = board_slug

    # ── 看板管理 ────────────────────────────────────────────────

    def init_board(self) -> bool:
        """确保看板数据库和 board 存在"""
        try:
            subprocess.run(
                ["hermes", "kanban", "init"],
                capture_output=True, timeout=10, text=True,
            )
            subprocess.run(
                ["hermes", "kanban", "boards", "create",
                 "--slug", self.board_slug,
                 "--name", "Molín WorkerChain",
                 "--description", "WorkerChain 任务看板 — 自动容错编排"],
                capture_output=True, timeout=10, text=True,
            )
            return True
        except Exception as e:
            logger.warning("Kanban board init failed: %s", e)
            return False

    def switch_board(self):
        """切换到指定看板"""
        try:
            subprocess.run(
                ["hermes", "kanban", "boards", "switch", self.board_slug],
                capture_output=True, timeout=10,
            )
        except Exception:
            pass

    # ── 任务创建 ─────────────────────────────────────────────────

    def create_task(
        self,
        title: str,
        assignee: str,
        body: str = "",
        parent_ids: Optional[list] = None,
    ) -> Optional[str]:
        """创建 Kanban 任务，返回 task_id"""
        self.switch_board()
        cmd = ["hermes", "kanban", "create", title,
               "--assignee", assignee,
               "--body", body or title]
        if parent_ids:
            for pid in parent_ids:
                cmd.extend(["--parent", pid])

        try:
            result = subprocess.run(
                cmd, capture_output=True, timeout=15, text=True,
            )
            output = result.stdout.strip()
            logger.info("Kanban create: %s", output[:200])
            # 解析 task_id: "Created task: t_abc123"
            for line in output.split("\n"):
                line = line.strip()
                if "t_" in line:
                    import re
                    m = re.search(r'(t_[a-f0-9]+)', line)
                    if m:
                        return m.group(1)
            return None
        except Exception as e:
            logger.error("Kanban create failed: %s", e)
            return None

    # ── WorkerChain 执行 ──────────────────────────────────────────

    def deploy_chain(
        self,
        worker_ids: list,
        task_description: str,
    ) -> dict:
        """将 WorkerChain 部署为 Kanban 依赖图

        每个 Worker 创建一个 Kanban 任务，按序建立 parent→child 链。
        最后一个 Worker 完成后产出即为最终结果。

        Args:
            worker_ids: 按序的 Worker ID 列表
            task_description: 任务描述

        Returns:
            {"board": str, "tasks": {worker_id: task_id}, "status": str}
        """
        if not self.init_board():
            return {"status": "error", "error": "Kanban board init failed"}

        self.switch_board()
        created = {}
        prev_task_id = None

        for i, wid in enumerate(worker_ids):
            title = f"[{i+1}/{len(worker_ids)}] {wid}: {task_description[:40]}"
            body = (
                f"## WorkerChain 步骤 {i+1}/{len(worker_ids)}\n\n"
                f"**Worker:** {wid}\n"
                f"**上游:** {prev_task_id or '无（首步）'}\n"
                f"**任务描述:** {task_description}\n\n"
                f"请执行你的核心能力后调用 kanban_complete 汇报结果。\n"
                f"输出将通过 ContextBus 传递给下游 Worker。"
            )

            parents = [prev_task_id] if prev_task_id else None
            tid = self.create_task(title, wid, body, parent_ids=parents)

            if tid:
                created[wid] = tid
                prev_task_id = tid
            else:
                logger.error("Failed to create task for worker: %s", wid)
                return {
                    "status": "partial",
                    "board": self.board_slug,
                    "tasks": created,
                    "error": f"Failed creating task for {wid}",
                }

        return {
            "status": "deployed",
            "board": self.board_slug,
            "tasks": created,
            "chain_order": worker_ids,
        }

    # ── 状态查询 ─────────────────────────────────────────────────

    def chain_status(self) -> dict:
        """查询当前看板所有任务状态"""
        self.switch_board()
        try:
            result = subprocess.run(
                ["hermes", "kanban", "list", "--json"],
                capture_output=True, timeout=10, text=True,
            )
            tasks = json.loads(result.stdout) if result.stdout.strip() else []
            return {
                "board": self.board_slug,
                "total": len(tasks),
                "tasks": tasks,
            }
        except Exception as e:
            return {"board": self.board_slug, "error": str(e)}

    def recover_chain(self, task_id: str) -> dict:
        """恢复失败任务 — reclaim + 重建"""
        self.switch_board()
        try:
            subprocess.run(
                ["hermes", "kanban", "reclaim", task_id],
                capture_output=True, timeout=10,
            )
            return {"status": "reclaimed", "task_id": task_id}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_task_summary(self, task_id: str) -> Optional[str]:
        """获取已完成任务的 summary"""
        self.switch_board()
        try:
            result = subprocess.run(
                ["hermes", "kanban", "show", task_id],
                capture_output=True, timeout=10, text=True,
            )
            return result.stdout.strip()
        except Exception:
            return None


# ── 快捷入口 ────────────────────────────────────────────────────

kanban_chain = KanbanChain()


def deploy_workerchain(worker_ids: list, task_desc: str) -> dict:
    """快捷部署 WorkerChain 到 Kanban 看板"""
    return kanban_chain.deploy_chain(worker_ids, task_desc)


def smart_route(worker_ids: list, task: any, context: dict = None) -> dict:
    """智能路由：有 Kanban 走 Kanban，否则走原生 WorkerChain

    集成进 SmartDispatcher._dispatch_chain 的优先路径。
    """
    try:
        result = deploy_workerchain(worker_ids, str(task))
        if result.get("status") == "deployed":
            return result
    except Exception as e:
        logger.warning("Kanban deploy failed, falling back to native: %s", e)

    # 降级到原生 WorkerChain
    try:
        from molib.agencies.worker_chain import WorkerChain
        import asyncio
        chain = WorkerChain(worker_ids, task, context)
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(chain.execute())
        finally:
            loop.close()
    except ImportError:
        return {"status": "error", "error": "WorkerChain unavailable"}
