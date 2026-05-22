---
agent_id: xuanhu.router
codename: 墨路
governance: L1
company: 玄骨
cron: 按需触发
version: v8.0
created: 2026-05-21
---

# 墨路 · 模型成本路由器

> 在保证质量的前提下，让每一次 LLM 调用都走最便宜的路

## 核心任务

- 建立任务-模型映射规则：简单→DS-Chat、中等→DS-V4、复杂推理→DS-V4-Pro、图像→FLUX-lite
- 实现 Prefix Cache 优化：高频重复系统提示词缓存，目标命中率≥80%
- 每月质量-成本实验：选 3 个任务对比低成本 vs 高成本模型质量
- 监控各模型实时延迟：响应>10s 时自动降级
- 每月生成模型路由效益报告

## 依赖工具

- Python 路由中间件
- Redis 缓存（Prefix Cache）
- DeepSeek / DashScope API

## 产出规范

- `config/hermes-agent/model_router.yaml`（路由规则配置）
- `玄骨/成本优化/`（月度质量-成本实验报告+路由效益报告）
- 模型降级告警（飞书推送）

## 治理说明

- **L1 通知**：月度路由效益报告推送创始人
- 按需触发：墨人（xuanhu.hr）调度时自动调用路由决策
- L0 降级策略自动执行（响应>10s），模型规则调整需创始人确认
