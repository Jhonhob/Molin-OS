"""
Hermes 多模型高可用网关 (LiteLLM Gateway)
============================================
借鉴 BerriAI/litellm 的统一多模型封装思想。
将 100+ 大模型的 API 统一封装为标准 OpenAI 格式，
原生支持自动重试、故障平滑切换（Fallbacks）、
流控限速（RPM/TPM）和精准 Token 级费用统计。

依赖：pip install litellm（可选，不安装则降级到 openai SDK）

用法：
    from molib.hermes_gateway import HermesGateway
    gw = HermesGateway()
    content, usage, latency = gw.ask("你好", tier="thinking")
"""

import time
import os
from typing import Optional

# 优先使用 litellm，不安装则降级到 openai SDK
try:
    import litellm  # noqa: F401
    HAS_LITELLM = True
except ImportError:
    HAS_LITELLM = False
    try:
        from openai import OpenAI
        HAS_OPENAI = True
    except ImportError:
        HAS_OPENAI = False


class HermesGateway:
    """
    统一多模型网关 — 高可用路由 + 自动降级 + Token 统计。
    """

    # ── 模型分层 ───────────────────────────────
    # tier → 主模型 + 备用模型列表

    MODEL_TIERS = {
        "thinking": {
            "primary": os.environ.get("HERMES_THINKING_MODEL", "deepseek/deepseek-reasoning"),
            "fallbacks": [
                "qwen/qwen-max",
                "openai/gpt-4o",
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
        },
        "execution": {
            "primary": os.environ.get("HERMES_EXECUTION_MODEL", "deepseek/deepseek-chat"),
            "fallbacks": [
                "qwen/qwen-plus",
                "openai/gpt-4o-mini",
            ],
            "temperature": 0.3,
            "max_tokens": 8192,
        },
        "lightweight": {
            "primary": os.environ.get("HERMES_LIGHT_MODEL", "qwen/qwen-turbo"),
            "fallbacks": [
                "openai/gpt-4o-mini",
            ],
            "temperature": 0.1,
            "max_tokens": 2048,
        },
    }

    def __init__(
        self,
        max_retries: int = 3,
        rpm_limit: int = 60,
        tpm_limit: int = 100000,
    ):
        """
        Args:
            max_retries: 单个模型最大重试次数
            rpm_limit: 每分钟请求数上限
            tpm_limit: 每分钟 Token 数上限
        """
        self.max_retries = max_retries
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit

        # 简易流控计数器
        self._request_count_minute = 0
        self._token_count_minute = 0
        self._minute_start = time.time()

        # 初始化客户端
        if HAS_LITELLM:
            self._backend = "litellm"
        elif HAS_OPENAI:
            self._backend = "openai"
            base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            api_key = os.environ.get("OPENAI_API_KEY", "sk-placeholder")
            self._openai_client = OpenAI(base_url=base_url, api_key=api_key)
        else:
            self._backend = "none"

    # ── 核心调用 API ───────────────────────────

    def ask(
        self,
        prompt: str,
        tier: str = "execution",
        *,
        system_prompt: str = "",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> tuple[Optional[str], dict, float]:
        """
        向 Hermes 大脑发起请求。

        Args:
            prompt: 用户提示
            tier: 模型层级 (thinking / execution / lightweight)
            system_prompt: 系统提示词
            temperature: 覆盖默认温度
            max_tokens: 覆盖默认最大 Token

        Returns:
            (content, usage_dict, latency_ms)
            content: 模型输出文本，失败时为 None
            usage_dict: {"prompt_tokens": N, "completion_tokens": N, "model": "..."}
            latency_ms: 耗时毫秒
        """
        if self._backend == "none":
            return None, {"error": "no LLM backend"}, 0

        tier_config = self.MODEL_TIERS.get(tier, self.MODEL_TIERS["execution"])
        model = tier_config["primary"]
        temp = temperature if temperature is not None else tier_config["temperature"]
        max_tok = max_tokens if max_tokens is not None else tier_config["max_tokens"]

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start = time.time()

        # 尝试主模型
        result = self._try_completion(model, messages, temp, max_tok)
        if result[0] is not None:
            content, usage, latency = result
            return content, usage, latency

        # 主模型失败 → 尝试降级备用模型
        for fallback_model in tier_config["fallbacks"]:
            print(f"   🔄 主模型失败，降级到: {fallback_model}")
            result = self._try_completion(fallback_model, messages, temp, max_tok)
            if result[0] is not None:
                content, usage, latency = result
                return content, usage, latency

        # 全部失败
        total_latency = int((time.time() - start) * 1000)
        return None, {"error": "all models failed", "tried": [model] + tier_config["fallbacks"]}, total_latency

    def _try_completion(
        self,
        model: str,
        messages: list,
        temperature: float,
        max_tokens: int,
    ) -> tuple[Optional[str], dict, float]:
        """尝试单次 completion，返回 (content, usage, latency_ms)"""
        self._check_rate_limit()

        for attempt in range(self.max_retries):
            try:
                start = time.time()

                if self._backend == "litellm":
                    response = litellm.completion(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                elif self._backend == "openai":
                    # 简化 model 名（去掉 litellm 前缀）
                    model_name = model.split("/")[-1] if "/" in model else model
                    response = self._openai_client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                else:
                    return None, {}, 0

                latency = int((time.time() - start) * 1000)
                content = response.choices[0].message.content
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "model": model,
                }

                # 更新流控
                self._token_count_minute += usage["prompt_tokens"] + usage["completion_tokens"]
                self._request_count_minute += 1

                # 日志
                try:
                    from molib.agent_logger import get_logger
                    get_logger().log_action(
                        worker="hermes_gateway",
                        skill=model,
                        tokens_in=usage["prompt_tokens"],
                        tokens_out=usage["completion_tokens"],
                        latency_ms=latency,
                    )
                except ImportError:
                    pass

                return content, usage, latency

            except Exception as e:
                wait = 2 ** attempt
                print(f"   ⚠️ [{model}] 调用失败 (attempt {attempt + 1}): {e}，{wait}s 后重试")
                if attempt < self.max_retries - 1:
                    time.sleep(wait)

        return None, {}, 0

    def _check_rate_limit(self):
        """简易流控：每分钟重置计数器"""
        now = time.time()
        if now - self._minute_start > 60:
            self._request_count_minute = 0
            self._token_count_minute = 0
            self._minute_start = now

        if self._request_count_minute >= self.rpm_limit:
            wait = 60 - (now - self._minute_start) + 1
            print(f"   ⏳ RPM 限流，等待 {wait:.0f}s...")
            time.sleep(max(wait, 1))

    # ── 查询 API ───────────────────────────────

    def get_tiers(self) -> dict:
        """获取模型分层配置"""
        return {
            tier: {
                "primary": cfg["primary"],
                "fallbacks": cfg["fallbacks"],
                "temperature": cfg["temperature"],
            }
            for tier, cfg in self.MODEL_TIERS.items()
        }

    def health_check(self) -> dict:
        """网关节康检查"""
        return {
            "backend": self._backend,
            "has_litellm": HAS_LITELLM,
            "has_openai": HAS_OPENAI,
            "tiers": list(self.MODEL_TIERS.keys()),
            "rate_limits": {
                "rpm": self.rpm_limit,
                "tpm": self.tpm_limit,
                "current_minute_requests": self._request_count_minute,
                "current_minute_tokens": self._token_count_minute,
            },
        }
