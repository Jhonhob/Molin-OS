"""
结构化日志探针 — Agent 全链路可观测性
=========================================
将每一次 AI 动作以 JSON Lines 格式结构化落盘，
破除大模型黑盒，支撑成本核算、性能调优、异常溯源。

输出格式：每行一个 JSON 对象（JSONL），字段：
    timestamp, worker, skill_called, metrics{input_tokens, output_tokens, latency_ms},
    status, error

日志轮转策略：
- 按月分文件 (trace_YYYYMM.jsonl)
- system.log 捕获底层异常
- 日志目录: vault/logs/

用法：
    from molib.agent_logger import AgentTraceLogger, get_logger

    logger = get_logger()
    logger.log_action("mo_xiu", "web_search", 150, 400, 2300)
    logger.log_error("mo_xiu", "web_search", 150, 0, 5000, "Connection timeout")
"""

import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── 单例 ────────────────────────────────────────

_logger_instance: Optional["AgentTraceLogger"] = None


def get_logger(log_dir: Optional[str] = None) -> "AgentTraceLogger":
    """获取全局单例日志记录器"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AgentTraceLogger(log_dir=log_dir)
    return _logger_instance


# ── 日志记录器 ──────────────────────────────────

class AgentTraceLogger:
    """结构化 Agent 行为日志 — JSONL 格式，按月轮转"""

    DEFAULT_LOG_DIR = Path(__file__).parent.parent / "vault" / "logs"

    def __init__(self, log_dir: Optional[str] = None):
        log_path = Path(log_dir) if log_dir else self.DEFAULT_LOG_DIR
        log_path.mkdir(parents=True, exist_ok=True)
        self.log_dir = log_path

        # JSONL 文件：按月分片
        self._current_month = datetime.now().strftime("%Y%m")
        self._log_file = self.log_dir / f"trace_{self._current_month}.jsonl"

        # 系统级日志：捕获底层异常
        system_log = str(self.log_dir / "system.log")
        logging.basicConfig(
            filename=system_log,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        self._sys_logger = logging.getLogger("molin.agent")

    def _rotate_if_needed(self):
        """跨月自动切换文件"""
        current_month = datetime.now().strftime("%Y%m")
        if current_month != self._current_month:
            self._current_month = current_month
            self._log_file = self.log_dir / f"trace_{current_month}.jsonl"

    # ── 核心 API ────────────────────────────

    def log_action(
        self,
        worker: str,
        skill: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        latency_ms: float = 0,
        *,
        status: str = "success",
        error_msg: str = "",
        extra: Optional[dict] = None,
    ):
        """记录一次 AI 动作（成功或失败）"""
        self._rotate_if_needed()

        record = {
            "timestamp": datetime.now().isoformat(),
            "worker": worker,
            "skill_called": skill,
            "metrics": {
                "input_tokens": tokens_in,
                "output_tokens": tokens_out,
                "latency_ms": round(latency_ms, 1),
            },
            "status": status,
            "error": error_msg,
        }
        if extra:
            record["extra"] = extra

        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        # 同时写入系统日志
        if status == "error":
            self._sys_logger.error(f"[{worker}] {skill}: {error_msg}")
        else:
            self._sys_logger.info(
                f"[{worker}] {skill}: {tokens_in}→{tokens_out} tok, {latency_ms:.0f}ms"
            )

    def log_error(
        self,
        worker: str,
        skill: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        latency_ms: float = 0,
        error_msg: str = "",
        extra: Optional[dict] = None,
    ):
        """语法糖：记录错误日志"""
        self.log_action(
            worker, skill, tokens_in, tokens_out, latency_ms,
            status="error", error_msg=error_msg, extra=extra,
        )

    def log_handoff(
        self,
        source: str,
        target: str,
        success: bool,
        reason: str = "",
    ):
        """记录 Worker 间 Handoff 事件"""
        self.log_action(
            worker=f"{source}→{target}",
            skill="handoff",
            status="success" if success else "blocked",
            error_msg=reason if not success else "",
            extra={"source_worker": source, "target_worker": target},
        )

    def log_queue_push(self, worker: str, skill: str, task_id: int):
        """记录任务入队事件"""
        self.log_action(
            worker=worker,
            skill=skill,
            status="queued",
            extra={"task_id": task_id, "action": "push"},
        )

    # ── 查询 API ────────────────────────────

    def recent_errors(self, limit: int = 20) -> list[dict]:
        """提取最近的错误记录"""
        errors = []
        if not self._log_file.exists():
            return errors

        with open(self._log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    if record.get("status") == "error":
                        errors.append(record)
                except json.JSONDecodeError:
                    continue

        return errors[-limit:]

    def cost_summary(self, month: Optional[str] = None) -> dict:
        """按 Worker 汇总 Token 消耗"""
        month = month or self._current_month
        log_file = self.log_dir / f"trace_{month}.jsonl"
        if not log_file.exists():
            return {"month": month, "total_input": 0, "total_output": 0, "by_worker": {}}

        by_worker = {}
        total_in = 0
        total_out = 0

        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    metrics = record.get("metrics", {})
                    w = record.get("worker", "unknown")
                    t_in = metrics.get("input_tokens", 0)
                    t_out = metrics.get("output_tokens", 0)

                    total_in += t_in
                    total_out += t_out

                    if w not in by_worker:
                        by_worker[w] = {"input": 0, "output": 0, "calls": 0}
                    by_worker[w]["input"] += t_in
                    by_worker[w]["output"] += t_out
                    by_worker[w]["calls"] += 1
                except (json.JSONDecodeError, KeyError):
                    continue

        return {
            "month": month,
            "total_input": total_in,
            "total_output": total_out,
            "total_calls": sum(w["calls"] for w in by_worker.values()),
            "by_worker": by_worker,
        }
