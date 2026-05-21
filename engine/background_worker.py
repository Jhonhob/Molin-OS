"""
后台无头执行器 — Molin-OS 的「苦力层」
=====================================
脱离 Hermes 对话主循环独立运行，轮询 tasks.db 执行耗时任务。

启动方式：
    nohup python engine/background_worker.py > vault/logs/bg_worker.log 2>&1 &
    或 make run-background

设计原则：
- 单进程轮询，避免 SQLite 并发锁竞争
- 任务执行失败不崩溃，记录后继续下一轮
- 支持多 Worker 并发（通过 pop_pending_tasks 批量拉取）
"""

import time
import json
import sys
import signal
import traceback
from pathlib import Path

# 确保 molib 可导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from molib.task_queue import LiteTaskQueue


# ── 任务执行器映射 ──────────────────────────────
# 每个 skill_id 对应一个同步执行函数。
# 扩展：在这里注册新的耗时任务处理器。

SKILL_EXECUTORS = {
    # 示例 — 实际任务在集成时按六司 Worker 展开
    # "web_search": web_search_executor,
    # "content_generate": content_generate_executor,
}


def execute_task(skill_id: str, payload: dict) -> dict:
    """根据 skill_id 分发到对应执行器"""
    executor = SKILL_EXECUTORS.get(skill_id)
    if executor:
        return executor(payload)

    # 默认：模拟耗时执行（实际接入后移除）
    time.sleep(2)
    return {
        "status": "executed",
        "skill": skill_id,
        "payload_keys": list(payload.keys()),
        "note": "模拟执行 — 接入实际 Worker 后替换此逻辑",
    }


# ── 主循环 ──────────────────────────────────────

def run_background_loop(poll_interval: float = 3.0):
    """无限轮询任务队列的主循环"""
    queue = LiteTaskQueue()
    running = True

    def handle_shutdown(signum, frame):
        nonlocal running
        print(f"\n🛑 收到信号 {signum}，Worker 将在当前任务完成后退出...")
        running = False

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    print("🚀 后台 Worker 进程已启动，开始轮询任务...")
    print(f"   DB 路径: {queue.db_path}")
    print(f"   轮询间隔: {poll_interval}s")
    print(f"   已注册执行器: {list(SKILL_EXECUTORS.keys()) or '无（使用模拟执行）'}")
    print("-" * 50)

    consecutive_empty = 0

    while running:
        task = queue.pop_pending_task()

        if not task:
            consecutive_empty += 1
            # 空闲时逐渐延长休眠，减少 CPU 空转
            sleep_time = min(poll_interval * (1 + consecutive_empty * 0.5), 30.0)
            time.sleep(sleep_time)
            continue

        consecutive_empty = 0
        task_id = task["id"]
        worker = task["worker_name"]
        skill = task["skill_id"]

        print(f"📥 [ID:{task_id}] {worker} → {skill}")

        try:
            payload = json.loads(task["payload"]) if isinstance(task["payload"], str) else task["payload"]
            start = time.time()
            result = execute_task(skill, payload)
            elapsed = time.time() - start

            queue.complete_task(task_id, result, success=True)
            print(f"✅ [ID:{task_id}] 完成 ({elapsed:.1f}s)")

        except Exception as e:
            error_detail = {
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
            queue.fail_task(task_id, str(e))
            print(f"❌ [ID:{task_id}] 失败: {e}")
            # 未来可接入飞书报警：
            # from molib.notify import send_feishu_alert
            # send_feishu_alert(f"Worker 任务失败 [ID:{task_id}]: {e}")

    print("👋 Worker 已安全退出。")


# ── CLI 入口 ────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Molin-OS 后台任务执行器")
    parser.add_argument(
        "--interval", "-i",
        type=float,
        default=3.0,
        help="轮询间隔（秒），默认 3.0",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="仅显示队列统计信息后退出",
    )
    args = parser.parse_args()

    if args.stats:
        queue = LiteTaskQueue()
        stats = queue.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        sys.exit(0)

    run_background_loop(poll_interval=args.interval)
