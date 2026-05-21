"""
飞轮图控调度引擎 (Flywheel Graph)
====================================
借鉴 LangGraph 的「基于图的状态机」思想，
将 34 个 Worker 定义为节点，24 条 Handoff 路由定义为边。
原生支持中断挂起等待人工审批（L2 治理）。

用法：
    from molib.flywheel_graph import FlywheelGraph
    graph = FlywheelGraph()
    graph.add_worker("ziling", intel_worker_fn)
    graph.add_handoff("ziling", "yinyue", condition_fn=confidence_check)
    graph.execute("ziling", initial_state)
"""

import time
import json
from typing import Any, Callable, Optional
from pathlib import Path


class FlywheelGraph:
    """
    基于 DAG 的飞轮调度引擎 — 节点 = Worker，边 = Handoff 路由。
    """

    def __init__(self, max_depth: int = 10, checkpoint_dir: Optional[str] = None):
        self.nodes: dict[str, Callable] = {}
        self.edges: dict[str, dict] = {}
        self.max_depth = max_depth
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else None
        self._execution_log: list[dict] = []

    # ── 图构建 API ─────────────────────────────

    def add_worker(self, name: str, worker_fn: Callable[[dict], dict]):
        """
        注册一个 Worker 节点。

        Args:
            name: Worker 名称（如 'ziling', 'yinyue'）
            worker_fn: 执行函数，签名为 fn(state: dict) -> dict
        """
        self.nodes[name] = worker_fn

    def add_handoff(
        self,
        from_worker: str,
        to_worker: str,
        condition_fn: Optional[Callable[[dict], bool]] = None,
        requires_approval: bool = False,
    ):
        """
        注册一条 Handoff 路由（有向边）。

        Args:
            from_worker: 上游 Worker
            to_worker: 下游 Worker
            condition_fn: 可选的条件函数 fn(state) -> bool，返回 False 时阻断
            requires_approval: 是否需要 L2 人工审批
        """
        self.edges[from_worker] = {
            "target": to_worker,
            "condition": condition_fn,
            "requires_approval": requires_approval,
        }

    def add_conditional_edge(
        self,
        from_worker: str,
        routes: dict[str, Callable[[dict], bool]],
    ):
        """
        注册条件分支（一对多边）。

        Args:
            from_worker: 上游 Worker
            routes: {"target_a": fn_a, "target_b": fn_b}
                    每个 target 配一个条件函数，第一个返回 True 的生效
        """
        self.edges[from_worker] = {"conditional": routes}

    # ── 执行引擎 ───────────────────────────────

    def execute(
        self,
        start_worker: str,
        initial_state: dict,
        *,
        checkpoint_interval: int = 3,
    ) -> dict:
        """
        从指定 Worker 启动飞轮调度。

        Args:
            start_worker: 起始 Worker 名
            initial_state: 初始状态字典
            checkpoint_interval: 每 N 个节点保存一次检查点

        Returns:
            最终状态 dict，包含 _flywheel_log 执行日志和 _status
        """
        current = start_worker
        state = dict(initial_state)
        self._execution_log = []
        depth = 0
        checkpoint_counter = 0

        while current in self.nodes:
            depth += 1
            checkpoint_counter += 1

            if depth > self.max_depth:
                state["_status"] = "max_depth_exceeded"
                state["_error"] = f"飞轮深度超过上限 {self.max_depth}"
                break

            # 1. 执行当前节点
            node_start = time.time()
            print(f"⚙️ [深度{depth}] 飞轮激活: [{current}]")

            try:
                state = self.nodes[current](state)
                elapsed = (time.time() - node_start) * 1000
                self._execution_log.append({
                    "depth": depth,
                    "worker": current,
                    "status": "completed",
                    "elapsed_ms": round(elapsed, 1),
                })
                print(f"   ✅ [{current}] 完成 ({elapsed:.0f}ms)")
            except Exception as e:
                self._execution_log.append({
                    "depth": depth,
                    "worker": current,
                    "status": "failed",
                    "error": str(e),
                })
                state["_status"] = "node_failed"
                state["_error"] = f"[{current}] 执行异常: {e}"
                break

            # 2. 保存检查点
            if checkpoint_counter >= checkpoint_interval and self.checkpoint_dir:
                self._save_checkpoint(current, depth, state)
                checkpoint_counter = 0

            # 3. 查找下一条边
            if current not in self.edges:
                state["_status"] = "completed"
                break

            edge = self.edges[current]

            # 条件分支
            if "conditional" in edge:
                next_worker = None
                for target, cond_fn in edge["conditional"].items():
                    if cond_fn(state):
                        next_worker = target
                        break
                if next_worker is None:
                    state["_status"] = "no_route"
                    state["_error"] = f"[{current}] 无条件分支命中"
                    break
                current = next_worker
                continue

            # 单一边
            target = edge.get("target")

            # L2 审批检查
            if edge.get("requires_approval"):
                print(f"   🛑 [{current}] 需要 L2 人工审批，挂起在 → {target}")
                state["_status"] = "awaiting_l2_approval"
                state["_pending_handoff"] = {"from": current, "to": target}
                break

            # 条件检查
            condition = edge.get("condition")
            if condition and not condition(state):
                print(f"   🛑 [{current}] 断路条件触发，挂起在 → {target}")
                state["_status"] = "circuit_broken"
                state["_pending_handoff"] = {"from": current, "to": target}
                break

            current = target

        # 附加执行日志
        state["_flywheel_log"] = self._execution_log

        if "_status" not in state:
            state["_status"] = "completed"

        return state

    def resume_from_checkpoint(self, checkpoint_id: str) -> Optional[dict]:
        """从检查点恢复执行"""
        if not self.checkpoint_dir:
            return None
        cp_file = self.checkpoint_dir / f"flywheel_{checkpoint_id}.json"
        if not cp_file.exists():
            return None
        with open(cp_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_checkpoint(self, worker: str, depth: int, state: dict):
        """保存飞轮检查点"""
        if not self.checkpoint_dir:
            return
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        cp_id = f"{worker}_d{depth}_{int(time.time())}"
        cp_file = self.checkpoint_dir / f"flywheel_{cp_id}.json"
        cp_data = {
            "checkpoint_id": cp_id,
            "worker": worker,
            "depth": depth,
            "state": {k: v for k, v in state.items() if not k.startswith("_")},
            "timestamp": time.time(),
        }
        with open(cp_file, "w", encoding="utf-8") as f:
            json.dump(cp_data, f, ensure_ascii=False, indent=2)

    # ── 可视化 ─────────────────────────────────

    def visualize(self) -> str:
        """生成飞轮图的 ASCII 可视化"""
        lines = ["⚙️ Molin-OS 飞轮拓扑:", ""]
        for from_worker, edge in self.edges.items():
            if "conditional" in edge:
                for target in edge["conditional"]:
                    lines.append(f"  [{from_worker}] ──?──> [{target}]")
            else:
                target = edge.get("target", "?")
                condition = "🔒" if edge.get("requires_approval") else ""
                lines.append(f"  [{from_worker}] ──{condition}──> [{target}]")
        return "\n".join(lines) if len(lines) > 2 else "⚙️ 飞轮图为空"
