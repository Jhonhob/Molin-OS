<p align="center">
  <img src="https://img.shields.io/badge/version-v7.0-6C5CE7?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/workers-34-00B894?style=flat-square" alt="workers">
  <img src="https://img.shields.io/badge/profiles-6-0984E3?style=flat-square" alt="profiles">
  <img src="https://img.shields.io/badge/license-MIT-636E72?style=flat-square" alt="license">
</p>

# 墨麟 OS &nbsp;·&nbsp; Molin-OS

**单人运营的 AI 商业操作系统。6 家公司、34 个 AI Worker、1 个人。**

Molin-OS 将一家集团公司的完整商业能力——从市场情报、内容生产、电商运营到财务审计——压缩进一个本地运行的 AI 系统中。你不需要团队，你只需要一个终端。

---

## 为什么是 Molin-OS

传统的一人公司工具链是割裂的：ChatGPT 写文案、Midjourney 出图、Notion 做管理、飞书做客服。切换成本高、信息不互通、无法形成自动化闭环。

Molin-OS 用一个统一的 AI 操作系统替代这一切：

- **6 个 AI Profile 替代 6 个 VP**，每个管理一个完整业务领域
- **34 个专业 Worker**，从竞品追踪到直播带货，各司其职
- **全自动飞轮管线**，情报 → 内容 → 增长，每日无人值守运行
- **零外部付费依赖**，所有组件自托管、免费、本地运行

---

## 六司架构

```
🌸 元瑶 · 教育与用户增长公司              墨增 墨销 墨导 墨学 墨创 墨域
🔮 紫灵 · 情报与战略调研公司              墨研 墨数 墨影 墨嗅 墨投
🌙 银月 · 内容生态与全媒体矩阵公司        墨笔 墨图 墨剪 墨链 墨播 墨星
❄️ 梅凝 · 跨境出海与全球化公司            墨译 墨媒 墨站 墨航 墨盾
🍃 宋玉 · 创新拓展与商业化公司            墨商 墨案 墨关 墨聚 墨采
💀 玄骨 · 底层中枢与集团赋能公司          墨码 墨维 墨安 墨梦 墨算 墨律 墨人
```

每个公司拥有独立的：飞书机器人 · 商业闭环 · KPI 仪表盘 · 记忆空间 · 领域配置文件

[查看完整架构 →](AGENTS.md) &nbsp;·&nbsp; [Worker 索引 →](AGENT_REGISTRY.md)

---

## 快速开始

```bash
git clone git@github.com:moye-tech/Molin-OS.git
cd Molin-OS
bash setup.sh
```

系统将自动安装 Python 依赖、配置 Hermes Agent、创建 Profile 模板。之后填入飞书机器人和 API 密钥即可运行。

[完整安装指南 →](ENVIRONMENT.md)

---

## 核心能力

### 🔄 无人值守商业飞轮

系统每日自动完成从情报采集到内容分发的完整链路：

```
08:00 ─ 情报银行   AI 扫描 arXiv、行业博客、竞品动态 → 生成情报简报
09:20 ─ 内容工厂   基于情报自动生成小红书/公众号/短视频内容
10:45 ─ 增长引擎   SEO 优化、跨平台分发、效果追踪与策略调整
```

三棒全自动接力。任一环节断裂，系统级联告警，防止空转。

### 🧠 四层记忆架构

AI 不会「忘记」你告诉过它的事。

| 层级 | 存储 | 生命周期 | 用途 |
|:----:|:-----|:---------|:-----|
| L1 | 飞书对话上下文 | 24h | 当前任务连贯性 |
| L2 | Obsidian 结构化笔记 | 永久 | 项目决策、客户偏好 |
| L3 | Obsidian `产出/` | 永久 | 知识资产沉淀 |
| L4 | SKILL.md 版本化 | 永久 | 可复现工作流 |

### 🚪 全通道接入

```
飞书 6 Bot ─┬─ 元瑶 Bot (教育咨询)
             ├─ 紫灵 Bot (情报简报)
             ├─ 银月 Bot (内容发布)
             ├─ 梅凝 Bot (跨境运营)
             ├─ 宋玉 Bot (商务对接)
             └─ 玄骨 Bot (系统管控)

CLI 终端 · REST API · Telegram · Discord · 企微
```

### 🏛️ 五级治理

| 级别 | 策略 | 示例 |
|:----:|:-----|:-----|
| L0 自动执行 | 无需确认 | 内容生成、数据采集、例行报告 |
| L1 通知 | 完成后告知 | 系统更新、任务完成通知 |
| L2 审批 | 等创始人确认 | 对外发布、报价 > ¥100、修改配置 |
| L3 董事会 | 全面评估后执行 | 战略方向调整、新项目立项 |
| L4 绝对禁止 | 直接拒绝 | 真实资金操作、支付转账 |

### 📊 商业闭环

每个公司有独立的变现路径，不是松散的工具集合，而是真正的业务系统：

- **元瑶**：引流 → 私域沉淀 → 发售转化 → 课程交付 → 督学复购
- **紫灵**：趋势嗅探 → 竞品监控 → 数据清洗 → ROI测算 → 结构化研报
- **银月**：选题策划 → 爆款写作 → 视觉设计 → 视频后期 → 直播变现
- **梅凝**：内容本地化 → 独立站搭建 → 海外获客 → 供应链 → 合规风控
- **宋玉**：商务拓展 → 定制提案 → 政企关系 → 资源采购 → 线下活动
- **玄骨**：算力调度 → 研发部署 → 安全审计 → 财务管控 → 自进化

---

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    Hermes Agent                      │
│              (AI 调度引擎 · 6 Profile)                │
├─────────────────────────────────────────────────────┤
│  molib 执行层                                        │
│  ┌─────────┬──────────┬──────────┬────────────────┐ │
│  │ Handoff │ Planning │ Flywheel │ Memory/Retrieve│ │
│  │ 自动路由 │ 任务分解  │ 飞轮管线  │ 四层记忆检索    │ │
│  └─────────┴──────────┴──────────┴────────────────┘ │
├─────────────────────────────────────────────────────┤
│  数据层                                              │
│  ┌──────────┬──────────┬──────────┬───────────────┐ │
│  │ Obsidian │ MemPalace│ ChromaDB │ relay/ 管线   │ │
│  │ 知识库    │ 语义检索  │ 向量存储  │ 飞轮数据      │ │
│  └──────────┴──────────┴──────────┴───────────────┘ │
├─────────────────────────────────────────────────────┤
│  通道层                                              │
│  飞书 6 Bot · CLI · REST API · Telegram · Discord   │
└─────────────────────────────────────────────────────┘
```

---

## 技术原则

**零付费 (Zero-Cost)**
不依赖任何付费云服务。LLM 用 DeepSeek/阿里百炼免费额度，记忆用本地 ChromaDB，知识库用 Obsidian + iCloud。如果你有 API key，月成本可以为零。

**本地优先 (Local-First)**
所有数据存储在本地。Obsidian Vault 通过 iCloud 同步，GitHub 做远程备份。没有数据离开你的设备，除非你主动发布。

**单人可维护 (Solo-Maintainable)**
设计目标是一个人能看懂、能修改、能排错的系统。核心代码 ~5000 行 Python，配置文件用 YAML/Markdown，不需要 K8s、不需要微服务。

---

## 项目结构

```
Molin-OS/
├── AGENTS.md                  系统提示 · Worker映射 · CLI命令
├── SYSTEM.md                  主脑 SOP · 记忆架构
├── SOUL.md                    CEO 认知框架 · Worker链
├── AGENT_REGISTRY.md          34 Worker 索引
├── config/
│   ├── domains/               6 领域 YAML (商业闭环+KPI)
│   └── hermes-agent/          配置模板 · Cron定义
├── molib/                     Python 执行引擎
├── skills/                    技能库 (150+ SKILL.md)
├── scripts/                   运维脚本
├── engine/mirofish/           MiroFish 预测引擎
├── vault/                     Obsidian 知识库
├── docs/                      文档
│   ├── archive/               28 历史文档
│   ├── CRON_JOBS_AUDIT.md     Cron 审计
│   └── SYSTEM_OVERVIEW.md     系统全景
└── relay/                     飞轮管线数据
```

---

## 版本

| 版本 | 日期 | 里程碑 |
|:----:|:-----|:-------|
| v7.0 | 2026-05 | 六司三十四将 · 6 Profile 飞书Bot · YAML 标准化 |
| v6.0 | 2026-05 | 五域一枢 · 5 Profile |
| v5.0 | 2026-05 | 扁平化 Vault · 零子模块架构 |

---

## License

MIT &nbsp;·&nbsp; [moye-tech/Molin-OS](https://github.com/moye-tech/Molin-OS)
