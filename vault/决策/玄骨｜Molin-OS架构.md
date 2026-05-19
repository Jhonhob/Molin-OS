---
created: 2026-05-15
updated: 2026-05-16
agent: shared
status: 活跃
confidence: 待验证
importance: ⭐⭐⭐
source:
  - 对话: session_20260515_015103_31c7ce8e
  - 对话: session_20260515_183430_80cbd3
tags: [决策, shared, Molin-OS, 部署, 运维]
---

# Molin-OS v3.0 · 部署与运营

> 墨麟OS v3.0 完整部署手册 (2578行) 的执行记录与运营决策。

## 部署状态盘点

### 环境基线

| 组件 | 状态 |
|------|------|
| Hermes v0.13.0 | ✅ 已就绪 |
| 5 个 Profile | ✅ 全部运行 |
| Python 3.11 | ✅ /opt/homebrew |
| Node.js v20/v22 | ✅ ~/.nvm |

### 部署步骤进度

| 步骤 | 内容 | 状态 |
|------|------|------|
| 01 | 基础环境 | ✅ |
| 02 | Hermes 安装 | ✅ |
| 03 | Provider 配置 | ⚠️ 待修复 |
| 04 | Profile 部署 | ✅ |
| 05 | SOUL 文件 | 🔄 进行中 |
| 06 | Cron 调度 | 🔄 进行中 |
| 07 | Supermemory + Obsidian 记忆系统 | ❌ 未配置 |

### 已知问题

- **Provider 认证失败**: `No inference provider configured` — 需运行 `hermes model` 配置
- **记忆管线未搭建**: Supermemory 写入失败，Obsidian 路径偏移
- **Cron 配置文件存在但未注册到调度器**

## 财务核账 Cron

### molin-finance-daily 技能

- **类型**: class-level umbrella (devops/)
- **首次执行**: 2026-05-15
- **发现**: 多个结构性知识点，涉及财务数据管道

### 运行机制

```
墨麟OS cron → molin-finance-daily 技能 → 财务数据采集
→ 结构化分析 → Obsidian 写入
```

## 玄骨记忆管线

### 架构决策

- 给玄骨搭一套专属记忆管线
- Supermemory: shared 容器隔离
- Obsidian: 目录隔离
- 通过 Hermes 官方插件封装 Supermemory SDK

### 待修复

- [ ] Provider API Key 配置 (DeepSeek)
- [ ] Supermemory 连接与写入
- [ ] Obsidian REST API 路径修正
- [ ] Cron 调度器注册三条定时任务
- [ ] 记忆定期同步 cron

## 运维经验

- **路径解析**: `2>/dev/null` 隐藏路径解析失败 — 排查初期不应静默 stderr
- **部署审计**: 使用 verification/auditing methodology 逐项检查
- **记忆保真**: 学习成果必须全量保真，不压缩、不摘要、不删实质内容
