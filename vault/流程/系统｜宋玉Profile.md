---
created: 2026-05-15
updated: 2026-05-16
agent: side
status: 活跃
confidence: 已验证
importance: ⭐⭐⭐
source: experiences/side-profile-setup.md 迁移
tags:
  - side
  - profile
  - 基础设施
  - 配置
---

# 宋玉创业 · Profile 配置

## 配置概要

2026-05-15 完成副业专线基础设施搭建，以下为完整组件清单与配置说明。

## 身份文件

- **SOUL_SIDE.md** — 宋玉创业身份定义文件，包含角色定位、能力边界、行为规范

## 闲鱼自动化

| 组件 | 路径 | 说明 |
|------|------|------|
| xianyu_poll.sh | ~/.hermes/profiles/side/ | 闲鱼消息轮询脚本，Watchdog 守护，每 30 分钟执行 |
| order_manager.py | ~/.hermes/profiles/side/ | 订单管理系统 |
| xianyu-automation skill | skills 目录 | 对齐定价体系：L0 / L1 / L2 / 退款分级 |

## 定时任务（Cron）

| 任务 | 频率 | 说明 |
|------|------|------|
| 闲鱼消息检测 | */30 min | 轮询新消息 |
| 每日复盘 | 每日 | 汇总当日数据 |
| 价格周检 | 每周 | 检查并调整定价 |

## 记忆同步

| 组件 | 路径/配置 | 说明 |
|------|----------|------|
| memory_sync.py | ~/.hermes/profiles/side/ | 双通道记忆同步脚本 |
| Supermemory 容器 | hermes-side（隔离） | 长期记忆存储 |
| Obsidian REST API | :27124 | 本地知识库同步 |

## 双向同步通道

```
闲鱼消息 → memory_sync.py → Supermemory (长期记忆)
                           → Obsidian (知识库)
```

## 接入渠道

- **Hermes Agent CLI**：profile 名 `side`（宋玉创业）
- **飞书网关**：消息推送与状态通知
- **Cron 定时任务**：自动化巡检

## 来源

原始记录：`~/.hermes/profiles/side/home/experiences/side-profile-setup.md`（本地 Agent 工作目录）
迁移至 vault：`流程/系统｜宋玉Profile.md`
迁移日期：2026-05-16
