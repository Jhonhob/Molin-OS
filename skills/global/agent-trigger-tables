---
name: agent-trigger-tables
description: "Agent 技能调用触发表 — 每个 Agent 收到任务时先查此表"
version: 1.0.0
author: Molin-OS
platforms: [all]
metadata:
  hermes:
    tags: [trigger, routing, delegation, protocol]
---

# Agent 技能调用触发表

收到任务时，**必须先查这张表**，不允许直接用 LLM 生成内容跳过技能调用。

## 调用规则（优先级从高到低）

```
1. 触发词匹配 → 调用对应技能
2. 无触发词匹配 → 查 handoff list 委派 Worker
3. 无 Worker → 查 skills 列表
4. 均不匹配 → 自己干（标注「未使用专属技能」）
```

## 元瑶教育 · 触发词表

| 触发词 | 技能 / 操作 |
|--------|------------|
| 课程设计 / 大纲 / 知识点 / 教案 | course-designer (handoff → education.py) |
| 招生 / 成交 / 转化 / 报名话术 | sales-strategist |
| 学员 / 完课 / 退款 / 学习进度 | student-crm |
| 广告 / 投放 / CAC / ROI | ads-engine |
| 裂变 / 转介绍 / 老带新 | growth-hacker |
| 竞品课程 / 同类教育机构 | → 共享层: research-engine + competitor-analysis |
| 教育趋势 / 学习方向 | → mirofish-prediction |

## 梅凝出海 · 触发词表

| 触发词 | 技能 / 操作 |
|--------|------------|
| 繁体 / 繁中 / 本地化 / 翻译 | traditional-chinese |
| 台湾 / 台湾市场 / 台湾用户 | taiwan-market |
| Shopee / 虾皮 / 跨境 | shopee-automation |
| LINE / 群组 / 推送 | line-channel |
| 配音 / TTS / 语音 | tts-taiwan |
| 出海 / 海外市场 / 全球 | → 共享层: research-engine |

## 银月传媒 · 触发词表

| 触发词 | 技能 / 操作 |
|--------|------------|
| 小红书 / xhs / 笔记 | xiaohongshu-engine |
| 视频 / 抖音 / 脚本 / 分镜 / 口播 | video-script-engine |
| SEO / 搜索优化 / 关键词排名 | seo-machine |
| 数据 / 互动量 / 点赞 / 收藏率 | analytics-tracking |
| 选题 / 内容计划 | content-strategy |
| 竞品 / 对标账号 / 行业热点 | → 共享层: research-engine |
| GitHub / 开源项目 / 技术趋势 | github-trending-scanner |
| 预测 / 趋势 / MiroFish | → mirofish-prediction |
| 近30天 / last30days | → last30days |

## 玄骨中枢 · 触发词表（共享层）

| 请求服务 | 技能 / 操作 |
|---------|------------|
| service=research / 调研 / 情报 | research-engine + web-scraper + gpt-researcher |
| service=finance / 财务 / 记账 | finance-report |
| service=legal / 法务 / 合同 | legal-review |
| service=data / 数据 / 分析 | data-analysis |
| service=competitor / 竞品 | competitor-analysis + karpathy-autoresearch |
| service=arxiv / 论文 / 学术 | arxiv-scanner |
| 预测 / 推演 / 趋势 | → mirofish-prediction (共享) |

## 宋玉创业 · 触发词表

| 触发词 | 技能 / 操作 |
|--------|------------|
| 闲鱼 / 询盘 / 买家 / 消息 | xianyu-automation |
| 猪八戒 / 外包 / 接单 / 报价 | zhubajie-automation |
| 订单 / 交付 / 进度 / 验收 | order-manager |
| 技术方案 / 代码 / 实现 / 开发 | tech-delivery |
| 定价 / 收费标准 / 价格策略 | pricing-strategist |
| 客户 / 需求 / 评估 | client-profiler |
| 创业 / 副业 / 机会 | → mirofish-prediction |

## 跨 Agent 请求协议

A/B/C/E 调用 D（共享层）的标准格式：

```json
{
  "requester_agent": "media",
  "service": "research",
  "task": "扫描逻辑思维课程竞品近30天动态",
  "priority": "L0",
  "callback_path": "relay/media/intel_response.json",
  "deadline_minutes": 30
}
```

## 技能调用失败策略

1. 技能不存在 → 记录日志，发飞书告警，用 LLM 兜底
2. 技能返回空 → 重试 1 次，仍失败则 LLM 兜底
3. 跨 Agent 请求超时 (>30min) → 发飞书通知，独立执行
4. **禁止**：技能存在时静默跳过不调用
