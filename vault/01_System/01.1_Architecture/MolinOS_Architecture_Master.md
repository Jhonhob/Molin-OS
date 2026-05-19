---
title: 墨麟 OS 核心架构设计书
status: 迭代中 (Active)
last_updated: 2026-05-19
agent_sync: true
---

## 系统架构自动采集

## Agent 总览

| Agent | 名称 | 容器 | 飞书 App | 关联 Workers |
|-------|------|-----------------|----------|-------------|
| edu | 元瑶教育 | `edu` | cli_a956c83187395cd4 | education.py |
| global | 梅凝出海 | `molin-global` | cli_aa881c316d789bb5 | global_marketing.py |
| media | 银月传媒 | `molin-media` | cli_a966ede1d9789bd2 | content_writer.py, designer.py, short_video.py, voice_actor.py |
| shared | 玄骨中枢 | `molin-shared` | cli_aa884b4a88bc9bb4 | crm.py, customer_service.py, ops.py, finance.py, data_analyst.py, ecommerce.py |
| side | 宋玉创业 | `molin-side` | cli_a9513691d4f89bcf | — |


## 元瑶教育 (`edu`)

- **描述**: 教育内容、课程设计、学习辅导
- **容器**: `edu`
- **飞书 App ID**: `cli_a956c83187395cd4`
- **关联 Workers**: education.py


## 梅凝出海 (`global`)

- **描述**: 海外市场本地化运营、跨境营销
- **容器**: `molin-global`
- **飞书 App ID**: `cli_aa881c316d789bb5`
- **关联 Workers**: global_marketing.py


## 银月传媒 (`media`)

- **描述**: 全媒体内容创作、社交媒体运营、视频音频
- **容器**: `molin-media`
- **飞书 App ID**: `cli_a966ede1d9789bd2`
- **关联 Workers**: content_writer.py, designer.py, short_video.py, voice_actor.py


## 玄骨中枢 (`shared`)

- **描述**: CRM客户管理、运维部署、财务记账、数据分析
- **容器**: `molin-shared`
- **飞书 App ID**: `cli_aa884b4a88bc9bb4`
- **关联 Workers**: crm.py, customer_service.py, ops.py, finance.py, data_analyst.py, ecommerce.py


## 宋玉创业 (`side`)

- **描述**: 创业项目、副业探索、市场调研
- **容器**: `molin-side`
- **飞书 App ID**: `cli_a9513691d4f89bcf`
- **关联 Workers**: 无


## Vault 同步状态

| 分类 | 文件数 |
|------|-------|
| 报告 | 15 |
| 流程 | 25 |
| 配置 | 4 |
| 决策 | 48 |
| 成果 | 14 |
| 知识 | 18 |


## 记忆系统架构

```
每个 Agent 拥有独立 容器（container_tag）
记忆自动写入 → Obsidian vault（Markdown 全文检索）
定时同步 → Obsidian iCloud Vault（人工阅读 + 结构化）

Obsidian Vault 结构:
  决策/ → 不可逆选择（技术选型、架构定稿）
  知识/ → 沉淀积累（研究、架构理解）
  流程/ → 可执行步骤（SOP、配置、操作手册）
  成果/ → 可交付物（报告、产出、数据）
  配置/ → 系统架构元数据（含 Agent 配置快照）
  报告/ → 每日报告、定期产出
```

## 架构说明文档

## Agent 总览

| Agent | 名称 | Supermemory 容器 | 飞书 App | 关联 Workers |
|-------|------|-----------------|----------|-------------|
| edu | 元瑶教育 | `edu` | cli_a956c83187395cd4 | education.py |
| global | 梅凝出海 | `molin-global` | cli_aa881c316d789bb5 | global_marketing.py |
| media | 银月传媒 | `molin-media` | cli_a966ede1d9789bd2 | content_writer.py, designer.py, short_video.py, voice_actor.py |
| shared | 玄骨中枢 | `molin-shared` | cli_aa884b4a88bc9bb4 | crm.py, customer_service.py, ops.py, finance.py, data_analyst.py, ecommerce.py |
| side | 宋玉创业 | `molin-side` | cli_a9513691d4f89bcf | — |


## 元瑶教育 (`edu`)

- **描述**: 教育内容、课程设计、学习辅导
- **Supermemory 容器**: `edu`
- **飞书 App ID**: `cli_a956c83187395cd4`
- **关联 Workers**: education.py


## 梅凝出海 (`global`)

- **描述**: 海外市场本地化运营、跨境营销
- **Supermemory 容器**: `molin-global`
- **飞书 App ID**: `cli_aa881c316d789bb5`
- **关联 Workers**: global_marketing.py
- **记忆上下文**: 墨麟AI出海专线Agent · 梅凝。专注台湾和东南亚市场本地化内容运营与平台变现。所有内容使用繁体中文（台湾用语）。


## 银月传媒 (`media`)

- **描述**: 全媒体内容创作、社交媒体运营、视频音频
- **Supermemory 容器**: `molin-media`
- **飞书 App ID**: `cli_a966ede1d9789bd2`
- **关联 Workers**: content_writer.py, designer.py, short_video.py, voice_actor.py
- **记忆上下文**: 银月传媒Agent · 负责全媒体内容创作、社交媒体运营、视频生成、音频制作等传媒业务。


## 玄骨中枢 (`shared`)

- **描述**: CRM客户管理、运维部署、财务记账、数据分析
- **Supermemory 容器**: `molin-shared`
- **飞书 App ID**: `cli_aa884b4a88bc9bb4`
- **关联 Workers**: crm.py, customer_service.py, ops.py, finance.py, data_analyst.py, ecommerce.py
- **记忆上下文**: 玄骨中枢Agent · 负责CRM客户管理、运维部署、财务记账、数据分析等中枢共享服务。


## 宋玉创业 (`side`)

- **描述**: 创业项目、副业探索、市场调研
- **Supermemory 容器**: `molin-side`
- **飞书 App ID**: `cli_a9513691d4f89bcf`
- **关联 Workers**: 无
- **记忆上下文**: 宋玉创业Agent · 负责创业项目管理、副业探索、市场调研等创业相关业务。


## Vault 同步状态

| Agent | 分类 | 文件数 |
|-------|------|-------|
| — | 暂无同步文件 | 0 |


## 记忆系统架构

```
每个 Agent 拥有独立 Supermemory 容器（container_tag）
记忆自动写入 → Supermemory 云服务（语义检索）
定时同步 → Obsidian iCloud Vault（人工阅读 + 结构化）

Obsidian Vault 结构:
  Agents/<agent>/<category>/  → Agent 业务记忆
  Daily/<agent>/               → 每日报告
  System/                       → 系统架构元数据
```

## Molin-OS v3.0 部署运营决策

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

## 系统总览

## Vault 路径

`/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents/`

## v3.0 平坦结构（8 根目录，零子目录）

| 目录 | 用途 | 命名示例 |
|------|------|---------|
| **决策/** | 不可逆的选择：技术选型、架构定稿、战略方向 | `决策/系统｜DeepSeek路由策略.md` |
| **知识/** | 沉淀积累：方法论、行业洞察、技术参考 | `知识/银月｜小红书流量密码.md` |
| **流程/** | 可执行步骤：SOP、配置规范、系统架构 | `流程/系统｜执行规范.md` |
| **成果/** | 可交付物：完成的任务、分析报告 | `成果/元瑶｜火花思维增长方案.md` |
| **报告/** | 周期性复盘：KPI日报/周报/月报/季度报告 | `报告/系统｜日报·20260517.md` |
| **配置/** | 系统配置文档、规则说明 | `配置/系统｜产出写入规范.md` |
| **产出/** | Agent 运行产出：内容、代码、分析 | `产出/银月｜竞品扫描·20260517.md` |
| **学习档案/** | 学习成果：GitHub精读笔记、论文摘要 | `学习档案/系统｜Supertonic精读.md` |

### 文件命名规范

格式：`业务线｜具体内容.md`（全角竖线 `｜`）

**业务线前缀：**
| 前缀 | 对应 Agent |
|------|-----------|
| `系统｜` | 系统全局（hermes） |
| `元瑶｜` | 元瑶教育（edu） |
| `银月｜` | 银月传媒（media） |
| `梅凝｜` | 梅凝出海（global） |
| `宋玉｜` | 宋玉创业（side） |
| `玄骨｜` | 玄骨中枢（shared） |
| `KPI｜` | KPI 追踪 |

## 5 个 Agent

| ID | 名称 | 业务线前缀 | 职责 |
|------|------|-----------|------|
| `media` | 银月传媒 | `银月｜` | 全媒体内容创作、社交媒体运营 |
| `edu` | 元瑶教育 | `元瑶｜` | 在线教育课程开发、学习辅导 |
| `global` | 梅凝出海 | `梅凝｜` | 跨境电商、海外市场本地化 |
| `shared` | 玄骨中枢 | `玄骨｜` | 系统运维、CRM、财务、数据 |
| `side` | 宋玉创业 | `宋玉｜` | 创业项目、副业探索 |

## 日报规范

所有 Agent 的每日产出写入 `报告/系统｜日报·{YYYYMMDD}.md`。
格式：KPI表格 + 完成事项 + 卡点问题 + 明日重点 + 系统健康。

## 数据流

```
对话记忆 → memory_bridge.py → Supermemory（语义检索）+ Obsidian（v3.0 平坦 vault）
系统快照 → collect_architecture.py → 流程/系统｜架构.md
日报     → Cron 每日复盘 → 报告/系统｜日报·{date}.md
学习     → GitHub扫描 → 学习档案/{业务线}｜{项目}·{date}.md
```

## 相关文档

| 文档 | 内容 |
|------|------|
| `流程/系统｜执行规范.md` | Agent 写入规范 — 分类判定、质量门禁、格式模板 |
| `配置/系统｜产出写入规范.md` | v3.0 产出路径映射、防复发检查 |
| `流程/系统｜架构.md` | 系统架构快照 |

## 迁移历史

| 日期 | 版本 | 变更说明 |
|------|------|----------|
| 2026-05-17 | v3.0 flat | 8 根目录，零子目录，`业务线｜内容.md` 命名。消灭 Agents/ Daily/ System/ Archive/ 旧结构 |
| 2026-05-15 | v3 (旧) | 4 分类（决策/知识/流程/成果）+ Agents/ 子目录 |
| — | v2 | 6 分类（🎯⚙️🧠📊💬📖） |
| — | v1 | 8 分类（按来源） |

旧版本文件已全部重命名迁移至 v3.0 平坦结构。

## 记忆架构

## Supermemory 容器映射

| Agent | 容器 tag | 用途 |
|-------|---------|------|
| 元瑶教育 (`edu`) | `edu` | 教育内容、课程设计、学习辅导 |
| 梅凝出海 (`global`) | `molin-global` | 海外市场本地化运营、跨境营销 |
| 银月传媒 (`media`) | `molin-media` | 全媒体内容创作、社交媒体运营、视频音频 |
| 玄骨中枢 (`shared`) | `molin-shared` | CRM客户管理、运维部署、财务记账、数据分析 |
| 宋玉创业 (`side`) | `molin-side` | 创业项目、副业探索、市场调研 |

## Obsidian Vault 映射

**Vault 路径**: `/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents`

| 路径 | 内容 |
|------|------|
| `Agents/<agent>/` | 各 Agent 的业务记忆（按领域分类 + `.archives`） |
| `Agents/<agent>/🎯 任务与执行/` | 任务、决策、流程、SOP |
| `Agents/<agent>/⚙️ 系统与配置/` | 环境、配置、工具链、技能图 |
| `Agents/<agent>/🧠 知识库/` | 知识沉淀、架构文档、学习笔记 |
| `Agents/<agent>/📊 数据与报告/` | 数据、分析、日报、产出 |
| `Agents/<agent>/💬 对话记录/` | 历史对话记忆 |
| `Agents/<agent>/📖 参考与规范/` | 索引、模板、快速参考 |
| `Daily/<agent>/` | 每日报告 |
| `System/` | 系统架构元数据 |
| `System/agents/<agent>.md` | Agent 配置快照 |

## 基础设施

| 服务 | 端口 | 用途 |
|------|------|------|
| CloakServe CDP 池 | `localhost:9222` | 共享 stealth 浏览器（5 种子池） |
| Phoenix Live Dashboard | N/A | 监控集群 (如有) |

## 记忆架构规范

## 概述

基于 Molin-OS 审计报告建议，建立时效 × 深度的四层记忆架构。

## 四层定义

| 层级 | 名称 | 载体 | 内容特征 | 深度 | 时效 | 清理规则 |
|------|------|------|----------|------|------|----------|
| 🔴 L1 | 工作记忆 | 飞书对话上下文 / Session | 当前任务状态、待审批项 | 摘要级 | 当日 | 24小时自动清理 |
| 🟡 L2 | 情节记忆 | Supermemory（向量检索） | 任务执行经验、失败分析 | 结构化卡片 300-800字 | 近期 | 30天未调用→蒸馏到L3 |
| 🟢 L3 | 语义记忆 | Obsidian 知识/ 学习档案/ | 方法论、SOP、行业洞察 | 深度文档 1000-5000字 | 长期 | 永久保留，定期回顾更新 |
| 🔵 L4 | 程序记忆 | SKILL.md 文件（技能体系） | 技能配置、Prompt模板 | 可执行规范 | 永久 | 经测试验证后合并 |

## 写入规则

### L1 → L2（对话提升）
- 策略讨论 → 写入 Supermemory L2，profile=CEO，不进 Obsidian
- 任务指令完成后 → Worker 执行结果写 Obsidian `学习档案/{agent_id}/success/`（成功）或 `failures/`（失败）
- 复盘总结 → 强制深度写，最少 800 字，进 Obsidian `学习档案/{agent_id}/retrospectives/`

### L2 → L3（蒸馏条件）
- Supermemory 中 30 天未被检索的条目
- 内容长度 ≥ 500 字且有方法论价值
- 蒸馏后写入 Obsidian `知识/` 对应文件，添加标签 `distilled:true`

### L3 → L4（技能化条件）
- 方法论在 Obsidian 中积累了 3+ 次引用
- 至少 2 次实践验证（有成功案例）
- 对应 Agent 的 Growth SOP 确认有价值
- 由 AutoDream 生成 SKILL_UPDATE_PROPOSAL.md，触发 L2 审批

## 分类标签体系

所有写入 Obsidian 的文件必须包含以下标签：

```yaml
tags: [记忆层级(L1/L2/L3/L4), 来源(对话/审计/学习/手动), 可信度(已验证/待验证/实验性)]
```

示例：
```yaml
tags: [L3, 学习, 已验证, vertical-learning, 墨笔文创]
```

## 禁止规则

- ❌ L1 内容不进 Obsidian（只在 Supermemory）
- ❌ L3 文件不能直接修改 L4 技能（必须通过 AutoDream 提案）
- ❌ 学习结果不混入业务产出目录（必须在 `学习档案/` 下独立存放）
- ✅ 深度笔记最低字数：L2 ≥ 300 | L3 ≥ 1000 | L4 可执行即可

## 修订日志 (Changelog)

- **2026-05-19**: 从旧 vault 8目录体系迁移合并：系统架构、部署决策、记忆架构
