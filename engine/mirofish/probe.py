"""
MiroFish 闭环预测异常挂载探针
===============================
让流量/转化预测引擎不再是独立的花瓶，
而是能够对业务故障进行反向自愈的智能监控。

核心机制：
- 对比 MiroFish 预测基线与各公司实测 KPI
- 实测跌破预测安全线 → 自动触发断路器
- 通过 AtomicDataBus 下发 SYSTEM_SUSPEND 降级工单

用法：
    from engine.mirofish.probe import MiroFishClosedLoop
    probe = MiroFishClosedLoop()
    ok = probe.monitor_business_health("元瑶", current=120, predicted=200)
"""

import time
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from molib.data_bus import AtomicDataBus


class MiroFishClosedLoop:
    """闭环自愈探针 — 预测引擎与业务监控的桥梁"""

    def __init__(self, bus: Optional[AtomicDataBus] = None):
        self.bus = bus or AtomicDataBus()

    def monitor_business_health(
        self,
        domain_name: str,
        current_metric: float,
        prediction_threshold: float,
        *,
        auto_breaker: bool = True,
        alert_ratio: float = 0.7,
    ) -> bool:
        """
        对比 MiroFish 预测安全基线与实测 KPI。

        Args:
            domain_name: 公司/域名称（如 '元瑶'）
            current_metric: 当前实测 KPI 值
            prediction_threshold: MiroFish 预测的安全基线
            auto_breaker: 是否自动触发断路器
            alert_ratio: 告警比例（< threshold * alert_ratio 触发）

        Returns:
            True: 指标正常；False: 触发告警/断路器
        """
        ratio = current_metric / max(prediction_threshold, 0.001)

        print(f"📊 [MiroFish 探针] {domain_name}: "
              f"实测={current_metric:.1f} / 预测基线={prediction_threshold:.1f} "
              f"(比例={ratio:.1%})")

        if current_metric >= prediction_threshold:
            print(f"   ✅ 指标在安全线以上")
            return True

        # 轻微下跌 → 告警但不熔断
        if current_metric >= prediction_threshold * alert_ratio:
            print(f"   ⚠️ 轻微下跌 ({ratio:.1%})，仅告警不熔断")
            self._log_alert(domain_name, "WARNING", current_metric, prediction_threshold)
            return True

        # 严重下跌 → 触发断路器
        print(f"   🚨 严重跌破安全线 ({ratio:.1%})！触发自愈断路器...")

        if auto_breaker:
            self._trigger_circuit_breaker(domain_name, current_metric, prediction_threshold)

        self._log_alert(domain_name, "CRITICAL", current_metric, prediction_threshold)
        return False

    def _trigger_circuit_breaker(
        self,
        domain_name: str,
        current: float,
        predicted: float,
    ):
        """向原子数据总线注入自愈降级工单"""
        breaker_key = f"circuit_breaker_{domain_name}_{int(time.time())}"

        self.bus.write_pipe(
            bus_key=breaker_key,
            source_worker="mirofish_probe",
            target_domain="xuangu",
            payload={
                "action": "SUSPEND_FLY_WHEEL",
                "domain": domain_name,
                "reason": f"Metric drop detected. Current: {current}, Expected: {predicted}",
                "severity": "CRITICAL",
                "auto_recovery_seconds": 1800,  # 30 分钟后自动尝试恢复
            },
            ttl_seconds=3600,
        )

        print(f"   🔒 已下发断路器工单: {breaker_key}")

    def _log_alert(
        self,
        domain_name: str,
        level: str,
        current: float,
        predicted: float,
    ):
        """记录告警（对接 AgentTraceLogger + 飞书）"""
        try:
            from molib.agent_logger import get_logger
            logger = get_logger()
            logger.log_action(
                worker="mirofish_probe",
                skill="business_health_check",
                status="error" if level == "CRITICAL" else "success",
                error_msg=f"{domain_name}: {current:.1f}/{predicted:.1f}",
                extra={
                    "domain": domain_name,
                    "alert_level": level,
                    "current": current,
                    "predicted": predicted,
                },
            )
        except ImportError:
            pass

    def batch_monitor(self, checks: list[dict]) -> dict:
        """
        批量监控多个域。

        Args:
            checks: [{"domain": "元瑶", "current": 120, "predicted": 200}, ...]

        Returns:
            {"ok": [...], "alerted": [...], "breaker_triggered": [...]}
        """
        result = {"ok": [], "alerted": [], "breaker_triggered": []}

        for check in checks:
            domain = check["domain"]
            ok = self.monitor_business_health(
                domain,
                check["current"],
                check["predicted"],
            )
            if ok:
                if check["current"] < check["predicted"]:
                    result["alerted"].append(domain)
                else:
                    result["ok"].append(domain)
            else:
                result["breaker_triggered"].append(domain)

        return result
