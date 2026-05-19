<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-00b894?style=flat-square&logo=python" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-MIT-00b894?style=flat-square" alt="License MIT">
  <img src="https://img.shields.io/badge/brain-Hermes_Agent-8e44ad?style=flat-square" alt="Hermes Agent">
  <img src="https://img.shields.io/badge/skills-389-success?style=flat-square" alt="389 Skills">
  <img src="https://img.shields.io/badge/cron_jobs-19-blue?style=flat-square" alt="19 Cron Jobs">
  <img src="https://img.shields.io/badge/revenue-%C2%A552K/month-ff6b6b?style=flat-square" alt="Revenue">
  <img src="https://img.shields.io/badge/version-v5.0-blueviolet?style=flat-square" alt="v5.0">
</p>

# 墨麟 OS · Molin OS

一个人，一台 MacBook，一个 AI 集团。
One person, one MacBook, one AI conglomerate.

> **MolinOS-Ultra 已于 2026-05-19 废弃并 archive。全部内容已整合至此仓库。**
> 引擎代码 + 技能 + Obsidian 知识库均在 main 分支。
> 这是完整的自包含系统 — `bash setup.sh` 即可从零部署。

---

## 快速开始 / Quick Start

完整系统包含引擎代码、技能库、配置模板和 Obsidian 知识库，全部在 main 分支。

### 方式 A：完整部署（推荐）

```bash
git clone git@github.com:moye-tech/Molin-OS.git
cd Molin-OS
bash setup.sh
```

setup.sh 会自动完成：系统依赖检查 → Python 虚拟环境 → pip install Hermes Agent（本地源码）→ 配置模板生成 → cron 注册 → vault 镜像初始化。

### 方式 B：仅部署脚本

```bash
git clone git@github.com:moye-tech/Molin-OS.git
cd Molin-OS
bash scripts/deploy.sh
```

### 配置 API Keys

编辑 `~/.hermes/.env` 填入 API Keys：

```bash
DEEPSEEK_API_KEY=sk-xxx
DASHSCOPE_API_KEY=sk-xxx
OPENROUTER_API_KEY=sk-xxx
```

### 知识库同步

如果已有本地 Obsidian vault，运行 vault_git_sync.py 同步到仓库 vault/ 目录：

```bash
python3 scripts/vault_git_sync.py
```

> **注意**: 从本 Mac 推送至 GitHub 请使用 SSH 方式（HTTPS 因 TLS 握手超时会失败）。

---

## 核心特性 / Core Features

- AI 原生操作系统 — 不是工具集，不是 Agent 框架，是完整的 AI 一人公司运营系统
- 20 家垂直子公司 — 覆盖营销、运营、技术、财务、战略五大 VP + 共享服务
- Hermes Agent 引擎 — 自包含在仓库中（hermes/），完整 AI 推理大脑（v0.14.0, commit 43e566f）
- 389 项技能 —— 从 SEO 优化到量化交易，从像素艺术到红队安全测试
- Obsidian 知识库 —— vault/ 目录，8 类知识管理（决策/知识/流程/成果/报告/配置/产出/学习档案）
- 强制委托协议 — CEO 只做决策和路由，产出由子公司执行，杜绝 AI 包办
- DARE v3.0 推理框架 — Decompose · Analyze · Route · Elevate，四步完成从理解到超预期
- 每日自动化飞轮 — 08:00 情报采集 → 09:20 内容工厂 → 10:45 增长引擎，全自动接力
- 5 级治理体系 — L0 自动执行到 L4 绝对禁止，预算上限 + 审批门禁 + 审计追踪
- 多通道接入 — 飞书对话、CLI 终端、REST API 三种交互方式
- 单机运行 — M2 MacBook 8GB 即可驱动整个集团
- bash setup.sh 一键部署 — 从零到完整系统，无需手动配置

---

## 仓库结构 / Repository Structure

```
Molin-OS/
├── hermes/                      # Hermes Agent 引擎源码（v0.14.0, 3450 文件）
│   └── ...                      # pip install -e 直接安装
│
├── molib/                       # 墨麟执行引擎 Python 包
│   ├── agencies/                # 子公司 Worker + Handoff 路由 + 规划分解
│   ├── ceo/                     # CEO 引擎（推理 · 决策 · 编排）
│   ├── infra/                   # 基础设施（飞书网关 · 消息管线）
│   ├── management/              # VP 管理层
│   ├── shared/                  # 共享工具层（AI · 内容 · 知识 · 发布 · 存储）
│   └── xianyu/                  # 闲鱼集成
│
├── skills/                      # 389 项技能 SKILL.md 文件
│   ├── molin-org/               # 墨麟定制技能包（crm / ops / memory 等）
│   ├── sop-packs/               # 20+ 垂直业务 SOP 包
│   │   ├── content-sop-pack/    # 内容 Agent SOP
│   │   ├── developer-sop-pack/  # 开发 Agent SOP
│   │   ├── security-sop-pack/   # 安全 Agent SOP
│   │   └── ...                  # 财务/法务/客服/设计/教育/电商/出海等
│   ├── creative/                # 创意技能（ASCII / 设计 / 视频 / 像素艺术）
│   ├── mlops/                   # ML/Ops 技能（推理 / 评估 / 模型）
│   ├── research/                # 研究技能（arXiv / 情报 / 竞品）
│   └── ...                      # 按领域组织
│
├── scripts/                     # 运行时脚本（19 个活跃）
│   ├── deploy.sh                # 配置部署脚本
│   ├── vault_git_sync.py        # Obsidian 知识库同步
│   ├── relay_to_obsidian.py      # Relay → Obsidian 管道
│   ├── cross_request_worker.py  # 跨线请求轮询
│   ├── molin-sync-all.sh        # 全量记忆/缓存同步
│   ├── git-backup.sh            # Git 备份
│   ├── vault_health_check.py    # Vault 健康检查
│   ├── diagnostics/             # 诊断工具
│   └── kpi-dashboard/           # KPI 看板生成
│
├── config/
│   └── hermes-agent/            # Hermes Agent 配置模板（无密钥）
│       ├── config.yaml.template # 匿名化配置模板
│       ├── .env.example         # 全部环境变量占位符
│       ├── cron_jobs.md         # 19 个 cron 作业文档
│       └── profiles/            # 5 个 profile 配置（edu/global/media/shared/side）
│           └── .env.example     # 每个 profile 独立环境模板
│
├── vault/                        # Obsidian 知识库（8 类管理，159 篇笔记）
├── docs/                         # 系统文档
├── tests/                       # 测试
│
├── engine/                       # 运行时引擎（MiroFish 预测引擎等）
├── setup.sh                     # 一键部署脚本（7 步完成从零到系统）
├── setup.py                     # Python 包安装入口
├── requirements.txt             # Python 依赖
├── Makefile                     # 构建/测试命令
│
├── AGENTS.md                    # 子公司上下文映射（Hermes 系统提示注入）
├── AGENT_REGISTRY.md            # Agent 轻量索引
├── SYSTEM.md                    # 主脑 SOP 文档
├── SOUL.md                      # CEO 认知框架（灵魂文件）
├── ENVIRONMENT.md               # 环境要求说明
├── 产出写入规范.md              # Agent 输出规范
├── .github/                     # GitHub Actions / 社区文件
```

---

## 子公司体系 / Subsidiary System

20 家子公司分布于 5 位 VP 麾下，加上 3 家共享服务。

### VP 营销 / Marketing（5 家）

| 子公司 | 代号 | 核心能力 |
|:-------|:-----|:---------|
| 墨笔文创 | Content Writer | 品牌文案、小红书、公众号、SEO 内容 |
| 墨韵 IP | IP Manager | IP 孵化、版权管理、品牌衍生 |
| 墨图设计 | Designer | FLUX.2 生图、149 设计系统、封面/UI |
| 墨播短视频 | Short Video | 短视频脚本 + 生成、FFmpeg 视频引擎 |
| 墨声配音 | Voice Actor | AI 语音合成、播客制作、TTS |

### VP 运营 / Operations（4 家）

| 子公司 | 代号 | 核心能力 |
|:-------|:-----|:---------|
| 墨域私域 | CRM | 用户分层、社群运营、RFM 模型 |
| 墨声客服 | Customer Service | 自动化客服、闲鱼消息检测回复 |
| 墨链电商 | E-commerce | 订单管理、交易链路、多平台 |
| 墨学教育 | Education | 课程设计、AI 导师、学习路径 |

### VP 技术 / Technology（4 家）

| 子公司 | 代号 | 核心能力 |
|:-------|:-----|:---------|
| 墨码开发 | Developer | 软件开发、架构设计、代码审查 |
| 墨维运维 | Ops | 部署、监控、SRE、灾备 |
| 墨安安全 | Security | 代码审计、漏洞扫描、红队测试 |
| 墨梦 AutoDream | AutoDream | AI 自动化实验、记忆蒸馏、自学习 |

### VP 财务 / Finance（1 家）

| 子公司 | 代号 | 核心能力 |
|:-------|:-----|:---------|
| 墨算财务 | Finance | 记账、预算、成本控制、财务报表 |

### VP 战略 / Strategy（3 家）

| 子公司 | 代号 | 核心能力 |
|:-------|:-----|:---------|
| 墨商 BD | Business Development | 商务拓展、合作洽谈、销售策略 |
| 墨海出海 | Global Marketing | 多语言本地化、全球化运营 |
| 墨研竞情 | Research | 竞争分析、趋势扫描、实时情报 |

### 共享服务 / Shared Services（3 家）

| 子公司 | 代号 | 核心能力 |
|:-------|:-----|:---------|
| 墨律法务 | Legal | 合同审查、合规评估、风险评估 |
| 墨脑知识 | Knowledge | 知识图谱、向量记忆、RAG |
| 墨测数据 | Data Analyst | BI 仪表盘、数据分析、质量检测 |

### 专项 Workers / Specialized（3 家）

| Worker | 领域 |
|:-------|:-----|
| 墨投交易 | 量化交易策略、信号生成、回测 |
| Scrapling | 网页抓取、数据采集 |
| Router9 | 网络流量、多路路由 |

---

## 飞轮管线 / Cron Flywheel Pipeline

每日全自动内容管线，通过 relay/ 目录三棒接力，断链自动告警。

```
┌─────────────────────────────────────────────────────────────────────┐
│                        每 日 自 动 化 飞 轮                            │
│                                                                     │
│  08:00          09:20          10:45                                │
│  ┌──────┐      ┌──────┐      ┌──────┐                               │
│  │情报银行│ ──→ │内容工厂│ ──→ │增长引擎│                              │
│  │ Intel │      │Content│      │Growth │                               │
│  └──────┘      └──────┘      └──────┘                               │
│  扫描+筛选      生成+SEO       优化+分发                               │
│     │              │              │                                  │
│     └── relay/intelligence.json ──┘                                  │
│                 └── relay/content.json ──┘                           │
└─────────────────────────────────────────────────────────────────────┘
```

完整 19 项 Cron 时间表详见 `config/hermes-agent/cron_jobs.md`。

★ 标记为核心飞轮三棒，任意一棒失败触发级联告警。

---

## 治理模型 / Governance Model

5 级审批体系，基于预算上限 + 风险等级的量化治理。

| 级别 | 名称 | 预算上限 | 规则 |
|:-----|:-----|:---------|:-----|
| L0 | 自动执行 | ¥0 | 零成本操作，AI 自动完成无需审批 |
| L1 | AI 自审 | ≤ ¥10 | AI 内部检查后自动执行 |
| L2 | 人工确认 | ≤ ¥100 | 需创始人确认后执行 |
| L3 | 董事会审批 | ≤ ¥1,000 | 重大决策需全面评估 |
| L4 | 绝对禁止 | — | 涉及真实现金/转账/支付/改价，绝不触碰 |

核心原则：
- 月度运营预算 ¥1,360，80% 时触发预警
- 审计日志 90 天保留
- Token 30 天轮换，禁止提交凭证

---

## Hermes Agent 引擎

仓库包含完整的 Hermes Agent 源码（v0.14.0, commit 43e566f），位于 `hermes/` 目录。

```
hermes/
├── src/hermes/                  # Agent 引擎核心
│   ├── agent/                   # Agent 执行器、工具编排、消息处理
│   ├── config/                  # 配置管理
│   ├── gateway/                 # 飞书/Telegram/Discord 网关
│   ├── providers/               # AI 模型提供商（DeepSeek / OpenAI / Anthropic）
│   ├── tools/                   # 工具系统（terminal / file / browser / web）
│   ├── cron/                    # 定时任务调度器
│   ├── skills/                  # 技能系统
│   └── tui/                     # 终端 UI
├── website/                     # Hermes Agent 文档网站
├── pyproject.toml               # Python 项目配置
└── setup.py                     # 安装入口
```

安装方式：`pip install -e hermes/`（由 setup.sh 自动完成）。

---

## 技术栈 / Tech Stack

| 层级 | 技术 |
|:-----|:-----|
| AI 大脑 | Hermes Agent（Nous Research, v0.14.0） |
| 推理框架 | DARE v3.0（Decompose · Analyze · Route · Elevate） |
| 执行引擎 | Python 3.11+ · Click · Rich |
| 配置管理 | YAML · dotenv 模板 |
| 记忆系统 | ChromaDB（向量）· SQLite（结构化）· Obsidian（长期） |
| 通信通道 | 飞书 Bot · CLI · FastAPI（:5050） |
| 视觉设计 | FLUX.2 · Open Design · FFmpeg |
| 数据存储 | JSONL 审计日志 · 文件系统 |
| 自学习 | Self-Learning Loop · AutoDream · Memory Distillation |
| 版本控制 | Git · GitHub（SSH） |

---

## 环境要求 / Requirements

| 项目 | 要求 |
|:-----|:-----|
| 操作系统 | macOS 推荐（M2 8GB 已测试通过），Linux 兼容 |
| Python | 3.11+ |
| AI 引擎 | 自包含：hermes/（本地 pip install） |
| API Keys | DeepSeek · DashScope · OpenRouter（至少一个） |
| 可选 | FFmpeg（视频功能）· Docker（容器化部署） |
| 最低硬件 | M2 8GB / 同等算力，约 4GB 磁盘 |

---

## 开源协议 / License

MIT License © 2026 Moye Tech

本项目基于 [Hermes Agent](https://github.com/nousresearch/hermes-agent)（Nous Research）构建。
仓库包含 Hermes Agent 源码（commit 43e566f, v0.14.0）。
技能库中部分技能来自开源社区贡献，各自保留原许可。

---

<p align="center">
  <strong>墨麟 OS — 一个人就是一个集团</strong><br>
  <sub>Built with Hermes Agent · 389 skills · 20 subsidiaries · 19 cron jobs</sub>
</p>
