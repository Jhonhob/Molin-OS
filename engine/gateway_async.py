"""
异步多路复用飞书网关 — 解决 6 个 Bot 的 5 秒重试风暴
==========================================================
收到 Webhook 后 1 秒内闪回 200 ACK 响应，
内部通过 asyncio 非阻塞队列排队分发。

启动：
    python engine/gateway_async.py
    uvicorn engine.gateway_async:app --host 0.0.0.0 --port 8000

设计原则：
- FastAPI + asyncio.Queue 零外部依赖
- 飞书 URL 挑战验证直接透传
- 1 秒内闪回 200，截断飞书的 3 次重试机制
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from typing import Optional

# 确保 molib 可导入
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from fastapi import FastAPI, Request
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    FastAPI = object


# ── Bot 路由映射 ───────────────────────────────

BOT_ROUTING = {
    "yuanyao_bot": "元瑶",
    "ziling_bot": "紫灵",
    "yinyue_bot": "银月",
    "meining_bot": "梅凝",
    "songyu_bot": "宋玉",
    "xuangu_bot": "玄骨",
}

# ── 全局异步队列 ──────────────────────────────

task_queue: asyncio.Queue = asyncio.Queue(maxsize=500)

# ── 消息处理器（注入具体业务逻辑）─────────────

async def process_webhook_event(bot_id: str, event_data: dict) -> dict:
    """
    实际的业务处理入口。
    这里对接 Hermes Router / Skill Dispatcher。
    """
    company = BOT_ROUTING.get(bot_id, "未知")

    # 提取飞书消息文本
    msg_text = ""
    if "event" in event_data:
        event = event_data["event"]
        msg_text = event.get("text", "") or event.get("message", {}).get("content", "")

    if isinstance(msg_text, str):
        msg_text = json.loads(msg_text).get("text", msg_text) if msg_text.startswith("{") else msg_text

    print(f"📨 [{company}] 收到消息: {msg_text[:80]}...")

    # ── 在此注入实际调度逻辑 ──
    # from molib.ceo.intent_router import route_and_execute
    # result = await route_and_execute(company, msg_text, event_data)
    await asyncio.sleep(0.5)  # 模拟处理

    return {"company": company, "response": "OK", "bot_id": bot_id}


# ── 后台队列消费者 ────────────────────────────

async def async_worker_drain():
    """独占后台协程：有序消化队列中的请求"""
    print("🔄 后台队列消费者已启动...")
    while True:
        try:
            job = await task_queue.get()
            bot_id = job["bot_id"]
            event_data = job["event_data"]

            company = BOT_ROUTING.get(bot_id, "未知")
            start = time.time()

            try:
                result = await process_webhook_event(bot_id, event_data)
                elapsed = (time.time() - start) * 1000
                print(f"✅ [{company}] 处理完成 ({elapsed:.0f}ms) → {result}")
            except Exception as e:
                print(f"❌ [{company}] 处理异常: {e}")

        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"💥 队列消费者严重异常: {e}")
        finally:
            if "job" in locals():
                task_queue.task_done()


# ── 启动 FastAPI 应用 ─────────────────────────

if HAS_FASTAPI:
    app = FastAPI(title="Molin-OS Async Gateway", version="7.5.0")

    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(async_worker_drain())
        print("🚀 Molin-OS Async Gateway 已启动 (port 8000)")

    @app.post("/webhook/{bot_id}")
    async def feishu_webhook_ingress(bot_id: str, request: Request):
        """1 秒内闪回响应的飞书 Webhook 入口"""
        body = await request.json()

        # 飞书 URL 挑战验证直接透传
        if "challenge" in body:
            return {"challenge": body["challenge"]}

        # 推入非阻塞异步队列
        try:
            task_queue.put_nowait({"bot_id": bot_id, "event_data": body})
        except asyncio.QueueFull:
            return {"status": "overloaded", "message": "队列已满，请稍后重试"}

        # 瞬间返回 200，截断飞书重试机制
        return {"status": "accepted", "message": "job enqueued"}

    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "queue_size": task_queue.qsize(),
            "bots": list(BOT_ROUTING.keys()),
        }

else:
    app = None


# ── CLI 入口 ───────────────────────────────────

def main():
    if not HAS_FASTAPI:
        print("❌ 需要安装 FastAPI 和 Uvicorn:")
        print("   pip install fastapi uvicorn")
        sys.exit(1)

    import argparse
    parser = argparse.ArgumentParser(description="Molin-OS Async Gateway")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
