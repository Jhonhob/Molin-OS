# 墨麟 OS (Molin-OS) v7.0

> **六司三十四将 · 全自动 AI 商业操作系统**
> 一人公司 · AI Native · 零外部付费依赖

---

## 是什么 / What

墨麟 OS 是一个单人运营的 AI 商业操作系统。6 大领域公司、34 个专业 Worker、6 个飞书机器人——覆盖从教育增长到跨境出海、从内容媒体到中枢赋能的完整商业链路。

核心理念：**用 6 个 AI Profile 替代 6 个 VP**，每个 Profile 管理一个领域的完整商业闭环。

---

## 六司架构 / 6 Companies

```
🌸 元瑶 · 教育与用户增长公司 (Edu & Growth Co.)
   墨增/墨销/墨导/墨学/墨创/墨域 — Profile: yuanyao

🔮 紫灵 · 情报与战略调研公司 (Intelligence Co.)
   墨研/墨数/墨影/墨嗅/墨投 — Profile: ziling

🌙 银月 · 内容生态与全媒体矩阵公司 (Content & Media Co.)
   墨笔/墨图/墨剪/墨链/墨播/墨星 — Profile: yinyue

❄️ 梅凝 · 跨境出海与全球化公司 (Global Business Co.)
   墨译/墨媒/墨站/墨航/墨盾 — Profile: meining

🍃 宋玉 · 创新拓展与商业化公司 (Innovation & B2B Co.)
   墨商/墨案/墨关/墨聚/墨采 — Profile: songyu

💀 玄骨 · 底层中枢与集团赋能公司 (Group Infrastructure Co.)
   墨码/墨维/墨安/墨梦/墨算/墨律/墨人 — Profile: xuanhu
```

每个公司有独立的：飞书机器人 · 商业闭环 · KPI 体系 · 记忆空间 · 领域 YAML 配置

详见 [`AGENTS.md`](AGENTS.md) · [`AGENT_REGISTRY.md`](AGENT_REGISTRY.md) · [`config/domains/`](config/domains/)

---

## 快速开始 / Quick Start

```bash
git clone git@github.com:moye-tech/Molin-OS.git
cd Molin-OS
bash setup.sh          # 安装依赖 + 配置模板
```

详见 [`ENVIRONMENT.md`](ENVIRONMENT.md)

---

## 核心特性 / Key Features

### 🏢 六司三十四将
6 大领域 34 个专业 Worker，每个有独立商业闭环、KPI 指标和飞书机器人。

### 🔄 每日自动化飞轮
```
08:00  情报银行 → relay/intelligence.json
09:20  内容工厂 → relay/content.json
10:45  增长引擎 → 飞书/公众号/小红书
```
三棒全自动接力，断链级联告警。

### 🧠 四层记忆架构
- L1 工作记忆 — 飞书对话上下文 (24h)
- L2 情节记忆 — Obsidian 结构化笔记
- L3 语义记忆 — Obsidian `产出/` 永久存储
- L4 程序记忆 — SKILL.md 版本化管理

### 🔍 MemPalace 语义检索
向量化语义搜索，跨 vault 关联，与 Evolution Engine 深度融合。

### 🚪 飞书网关集成
6 个独立飞书机器人，自然语言输入 → Handoff 自动路由 → Worker 执行。

### 🏛️ 5 级治理体系
L0 自动执行 → L4 绝对禁止，预算上限 + 审批门禁。

---

## 系统架构 / Architecture

```
Molin-OS/
├── AGENTS.md              # 公司上下文（系统提示注入）
├── SYSTEM.md              # 主脑 SOP 文档
├── SOUL.md                # CEO 认知框架
├── AGENT_REGISTRY.md      # Worker 轻量索引
├── ENVIRONMENT.md          # 环境配置指南
├── config/
│   ├── domains/           # 6 领域 YAML Master Profile
│   └── hermes-agent/      # Hermes 配置模板 + Cron 定义
├── molib/                 # Molin OS 执行引擎 (Python)
├── skills/                # 技能库 (SKILL.md)
├── scripts/               # 运维脚本
├── engine/mirofish/       # MiroFish 预测引擎
├── hermes/                # Hermes Agent 源码
├── vault/                 # Obsidian 知识库（独立 git）
├── docs/                  # 文档
└── relay/                 # 飞轮管线数据
```

---

## 技术栈 / Tech Stack

| 层 | 技术 |
|----|------|
| AI 框架 | Hermes Agent · DeepSeek v4 · 阿里百炼 |
| 执行引擎 | Python 3.11 · molib |
| 记忆系统 | MemPalace · ChromaDB · Obsidian |
| 消息通道 | 飞书 6 Bot · Telegram · Discord |
| 部署 | macOS · Homebrew · Docker |

**零付费原则**：所有依赖均为免费/自托管，不依赖任何付费云服务。

---

## 文档索引 / Docs

| 文档 | 内容 |
|------|------|
| [`AGENTS.md`](AGENTS.md) | 六司架构 · CLI命令 · 飞轮管线 · 治理体系 |
| [`SYSTEM.md`](SYSTEM.md) | Agent SOP · 记忆架构 · Vault 目录 |
| [`SOUL.md`](SOUL.md) | CEO认知框架 · Worker链 · 经营节奏 |
| [`AGENT_REGISTRY.md`](AGENT_REGISTRY.md) | 34 Worker 索引 |
| [`ENVIRONMENT.md`](ENVIRONMENT.md) | 环境变量 · 安装步骤 · 常见问题 |
| [`config/domains/`](config/domains/) | 6 领域 YAML 配置 |
| [`config/hermes-agent/cron_jobs.md`](config/hermes-agent/cron_jobs.md) | 19 个 Cron 作业 |
| [`docs/SYSTEM_OVERVIEW.md`](docs/SYSTEM_OVERVIEW.md) | 系统全景 |
| [`docs/CRON_JOBS_AUDIT.md`](docs/CRON_JOBS_AUDIT.md) | Cron 审计报告 |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v7.0 | 2026-05-21 | 六司三十四将架构 · 6 Profile 飞书Bot |
| v6.0 | 2026-05-19 | 五域一枢 · 5 Profile |
| v5.0 | 2026-05-15 | 扁平化 Vault · 零子模块 |

---

## License

MIT
