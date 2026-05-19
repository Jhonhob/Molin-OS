# AI Provider 策略层设计 v1.0

吸收来源: moodle-ai-skill-navigator (Berserk-hub150, 137★)
设计模式: Strategy + Factory + Facade

## 为什么需要策略层

现有架构: 每个Agent直接调用LLM provider API
问题:
- 换模型要改每个Agent的调用代码
- 无法一键切换 GPT/Claude/DeepSeek
- 本地Ollama部署需要额外适配
- 无法做A/B测试(同一个请求发给不同模型比质量)

## 三件套架构

```
┌─────────────────────────────────────────────┐
│  Agent Layer                                 │
│  CoachAgent / DiagnoseAgent / VisualAgent    │
└─────────────────┬───────────────────────────┘
                  │ 调用 LLMService
┌─────────────────▼───────────────────────────┐
│  Facade: LLMService                          │
│  统一接口: generate(prompt, context)         │
│  自动路由: 根据配置 + 实时状态选择Provider    │
└─────────────────┬───────────────────────────┘
                  │ 委托给选中的Provider
┌─────────────────▼───────────────────────────┐
│  Factory: LLMProviderFactory                  │
│  create("openai"|"claude"|"deepseek"|"ollama")│
└─────────────────┬───────────────────────────┘
                  │ 实例化
┌─────────────────▼───────────────────────────┐
│  Strategy: LLMProvider (接口抽象类)           │
│  ├── OpenAIProvider                           │
│  ├── ClaudeProvider                           │
│  ├── DeepSeekProvider                         │
│  └── OllamaProvider (本地部署)                │
└─────────────────────────────────────────────┘
```

## 接口定义

```python
# 所有Provider实现此接口
class LLMProvider:
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        ...

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = "",
    ) -> AsyncIterator[str]:
        ...

    def model_name(self) -> str:
        ...  # 返回当前模型名，用于日志/A/B测试标记
```

## 路由规则 (Facade层)

无状态请求:
  默认: 配置中的 main_provider
  降级: main_provider 超时/限流 -> 自动切到 fallback_provider

有状态请求:
  同一session保持同一provider (避免风格抖动)
  缓存 conversation_id -> provider 映射

A/B测试:
  开启 flag: ab_test_enabled = true
  按 config.ab_test_ratio 分流 (如 50% GPT, 50% Claude)
  返回结果附加 provider 标记用于后续评估

本地/开发模式:
  默认使用 OllamaProvider (llama3.1:8b)
  无网络依赖，适合离线测试

## Provider对比

| Provider | 优势 | 劣势 | 建议场景 |
|----------|------|------|---------|
| GPT-4o | 推理最强，工具调用稳定 | 价格高(~$10/百万token) | Coach Agent核心推理 |
| Claude Sonnet 4 | 长上下文，代码理解好 | 中速 | 诊断报告生成 |
| DeepSeek V4 | 价格低(~$0.5/百万token) | 中文推理略弱于GPT | 大规模批处理/复习推送 |
| Ollama(本地) | 零成本，数据不出域 | 能力弱，速度慢 | 开发测试/隐私敏感场景 |

## 与当前架构的集成点

当前: CoachAgent.__init__() 中硬编码了模型名称
改为: CoachAgent.__init__(provider_name="openai") -> 从LLMService获取

配置文件(agent_config.json):
```json
{
  "llm_service": {
    "strategy": "auto",  // auto|manual|ab_test
    "main_provider": "openai",
    "fallback_provider": "deepseek",
    "ab_test": {
      "enabled": false,
      "ratio": 0.5,
      "group_a": "openai",
      "group_b": "claude"
    },
    "providers": {
      "openai": {
        "model": "gpt-4o",
        "temperature": 0.7
      },
      "claude": {
        "model": "claude-sonnet-4",
        "temperature": 0.7
      },
      "deepseek": {
        "model": "deepseek-v4",
        "temperature": 0.7
      },
      "ollama": {
        "model": "llama3.1:8b",
        "base_url": "http://localhost:11434"
      }
    }
  }
}
```

## 实施建议

P0 (文档就绪，无需代码):
  确认策略层接口设计
  确认路由规则

P1 (可执行):
  LLMService + OpenAIProvider 实现(已有es-kit/packages/es-kit集成)
  DeepSeekProvider + OllamaProvider 实现
  Agent配置迁移: 硬编码 -> 配置化

P2 (增强):
  A/B测试分流支持
  Provider实时性能监控
  自动降级熔断
