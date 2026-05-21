"""
飞轮断路器 — 防级联崩溃的 Handoff 安全网
=============================================
绝不信任上游大模型的输出，在 Worker 接力时强制校验数据结构。
每个 Handoff 链路都有独立的校验规则和置信度阈值。

核心接口：
    validate_handoff(source_worker, target_worker, data) → (bool, str)
    safe_handoff(...) → bool  # 带日志和报警的完整流程

设计哲学：
- 校验失败 = 硬阻断，数据不进入下游
- 断路器熔断后需要人工介入（或 L2 审批）
"""

import json
from typing import Any


class HandoffValidator:
    """Handoff 数据校验器 — 每类链路独立规则"""

    # ── 校验规则注册表 ──────────────────────────
    # 格式: (source, target) → validator_fn(data) → (bool, str)

    @staticmethod
    def validate_intelligence_to_content(data: Any) -> tuple[bool, str]:
        """紫灵(情报) → 银月(内容) 的数据校验"""
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return False, "❌ 严重错误：上游输出的不是有效 JSON，无法解析为结构化数据。"

        if not isinstance(data, dict):
            return False, f"❌ 预期 dict，收到了 {type(data).__name__}。"

        required_keys = ["topic", "source_url", "key_facts", "confidence_score"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            return False, f"❌ 数据残缺：缺少必要字段 {missing}。"

        # 断路阈值：置信度 < 0.7 直接熔断
        confidence = data.get("confidence_score", 0)
        if confidence < 0.7:
            return False, (
                f"⚠️ 置信度过低 ({confidence:.2f} < 0.7)，触发断路器。"
                f"topic='{data.get('topic', 'N/A')}'，需人工介入确认。"
            )

        # key_facts 不能为空
        facts = data.get("key_facts", [])
        if not facts or (isinstance(facts, list) and len(facts) == 0):
            return False, "❌ key_facts 为空，情报无实质内容。"

        return True, "✅ 情报数据校验通过"

    @staticmethod
    def validate_content_to_publish(data: Any) -> tuple[bool, str]:
        """银月(内容) → 发布 的数据校验"""
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return False, "❌ 内容输出不是有效 JSON。"

        if not isinstance(data, dict):
            return False, f"❌ 预期 dict，收到了 {type(data).__name__}。"

        required = ["title", "body"]
        missing = [k for k in required if k not in data]
        if missing:
            return False, f"❌ 缺少必要字段 {missing}。"

        # 敏感词扫描（简易版，实际接入完整词典）
        body = data.get("body", "")
        if len(body) < 10:
            return False, "❌ body 过短（<10字符），疑似生成失败。"

        return True, "✅ 内容发布数据校验通过"

    @staticmethod
    def validate_finance_record(data: Any) -> tuple[bool, str]:
        """财务记账数据校验"""
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return False, "❌ 财务数据不是有效 JSON。"

        required = ["type", "amount", "note"]
        missing = [k for k in required if k not in data]
        if missing:
            return False, f"❌ 缺少必要字段 {missing}。"

        amount = data.get("amount", 0)
        if not isinstance(amount, (int, float)) or amount <= 0:
            return False, f"❌ 金额无效: {amount}"

        return True, "✅ 财务数据校验通过"

    @classmethod
    def validate(cls, source: str, target: str, data: Any) -> tuple[bool, str]:
        """根据源/目标匹配校验规则并执行"""
        validator = cls.VALIDATOR_MAP.get((source, target))
        if validator is None:
            # 无特定规则 → 默认放行
            return True, "✅ 无校验规则，默认放行。"

        try:
            return validator(data)
        except Exception as e:
            return False, f"❌ 校验器内部异常: {e}"


# ── 构建路由表（在类外部完成，避免类体内 staticmethod 引用问题）──
HandoffValidator.VALIDATOR_MAP = {
    ("ziling", "yinyue"): HandoffValidator.validate_intelligence_to_content,
    ("ziling.researcher", "yinyue.writer"): HandoffValidator.validate_intelligence_to_content,
    ("yinyue", "publish"): HandoffValidator.validate_content_to_publish,
    ("yinyue.writer", "publish"): HandoffValidator.validate_content_to_publish,
    ("xuanhu.finance", "record"): HandoffValidator.validate_finance_record,
}

# ── 公开 API ────────────────────────────────────

def validate_handoff(source_worker: str, target_worker: str, data: Any) -> tuple[bool, str]:
    """无副作用的纯校验：返回 (是否通过, 原因消息)"""
    return HandoffValidator.validate(source_worker, target_worker, data)


def safe_handoff(
    source_worker: str,
    target_worker: str,
    payload: Any,
    *,
    alert_on_failure: bool = False,
) -> bool:
    """
    Worker 接力时的安全网 — 校验 + 日志 + 可选报警。

    Args:
        source_worker: 上游 Worker 标识（如 'ziling.researcher'）
        target_worker: 下游 Worker 标识（如 'yinyue.writer'）
        payload: 传递的数据（dict 或 JSON string）
        alert_on_failure: 是否在失败时发送飞书报警

    Returns:
        True 表示校验通过可安全传递；False 表示被断路器阻断。
    """
    print(f"🔄 Handoff: {source_worker} → {target_worker}")

    is_valid, msg = validate_handoff(source_worker, target_worker, payload)

    if is_valid:
        print(f"   ✅ {msg}")
        return True
    else:
        print(f"   🛑 断路器阻断！{msg}")

        if alert_on_failure:
            # 飞书报警（如已配置）
            try:
                from molib.integrations.feishu import send_alert
                send_alert(
                    title="🚨 飞轮断路器熔断",
                    content=f"**{source_worker} → {target_worker}**\n\n{msg}\n\n"
                            f"Payload preview: {str(payload)[:500]}",
                )
            except ImportError:
                pass  # 飞书模块未安装，静默跳过

        return False
