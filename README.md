<p align="center">
  <img src="https://img.shields.io/badge/版本-v8.0-6C5CE7?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/特工-44-00B894?style=flat-square" alt="workers">
  <img src="https://img.shields.io/badge/身份-6-0984E3?style=flat-square" alt="profiles">
  <img src="https://img.shields.io/badge/许可证-MIT-636E72?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/Python-3.9+-FFEAA7?style=flat-square" alt="python">
  <img src="https://img.shields.io/badge/零成本-✓-E17055?style=flat-square" alt="zero-cost">
</p>

<h1 align="center">墨麟 OS &nbsp;·&nbsp; Molin-OS</h1>

<p align="center"><strong>单人运营的 AI 商业操作系统 · 6 家子公司 · 44 位 AI 特工 · 1 个人</strong></p>
<p align="center">本地优先 · 零成本 · 一键部署 · 工业级稳定性</p>

---

## 目录

- [什么是 Molin-OS](#什么是-molin-os)
- [六司四十四将架构](#六司四十四将架构)
- [快速开始](#快速开始)
- [系统架构](#系统架构)
- [核心能力](#核心能力)
- [工业级硬化体系 (v7.5.0)](#工业级硬化体系-v750)
- [项目结构](#项目结构)
- [命令速查](#命令速查)
- [依赖说明](#依赖说明)
- [版本历史](#版本历史)
- [设计哲学](#设计哲学)
- [许可证](#许可证)

---

## 什么是 Molin-OS

Molin-OS 是一个**本地优先、零成本、单人可维护**的 AI 商业操作系统。它将一家集团公司的完整商业能力——从市场情报、内容生产、电商运营到财务审计——压缩进一个本地运行的 Python 系统中。

**不需要团队，只需要一个终端。**

### 它解决什么问题

传统的一人公司工具链是割裂的：用 ChatGPT 写文案、用 Midjourney 出图、用 Notion 做管理、用飞书做客服。切换成本高，信息不互通，无法形成自动化闭环。

Molin-OS 用一个统一的 AI 操作系统取代这一切：

| 特性 | 说明 |
|------|------|
| **6 个 AI 身份** | 替代 6 位 VP，各自管理完整业务领域 |
| **44 位专业特工** | 从竞品追踪到直播带货，各司其职 |
| **全自动飞轮管线** | 情报→内容→增长，每日无人值守运行 |
| **零外部付费依赖** | 全部组件自托管、免费、本地运行 |
| **工业级硬化** | 16 个防御模块：断路器、沙箱隔离、异步网关、记忆去重 |
| **一键部署** | `bash setup.sh` 完成全部安装配置 |

---

## 六司四十四将架构

```
🔮 紫灵 · 情报与战略调研公司
     墨嗅（信息采集） 墨影（趋势洞察） 墨标（SEO关键词）🆕
     墨数（数据分析） 墨研（竞品研究） 墨测（MVP验证）🆕 墨投（投资研判）

🌸 元瑶 · 教育与用户增长公司
     墨增（获客引流） 墨销（销售转化） 墨导（用户引导）
     墨学（课程交付） 墨创（创新实验） 墨域（私域运营）
     墨单（闲鱼接单）🆕 墨试（A/B测试）🆕

🌙 银月 · 内容生态与全媒体矩阵公司
     墨笔（文案创作） 墨图（视觉设计） 墨剪（视频后期）
     墨文（SEO深度长文）🆕 墨播（直播运营） 墨星（IP 打造）
     墨排（内容调度）🆕

❄️ 梅凝 · 跨境出海与全球化公司
     墨译（本地化翻译） 墨媒（海外媒体） 墨站（独立站建站）
     墨汇（跨境支付）🆕 墨盾（合规风控） 墨荐（产品分发）🆕

🍃 宋玉 · 产品孵化与威客接单公司
     墨图纸（极简PRD）🆕 墨架（技术选型）🆕 墨钩（免费工具）🆕
     墨对（平台申诉）🆕 墨冷（冷启动）🆕 墨价（定价策略）🆕
     墨单（威客接单）🆕 墨开（产品发版）

💀 玄骨 · 底层中枢与集团赋能公司
     墨码（研发部署） 墨维（系统运维） 墨安（安全审计）
     墨梦（自进化） 墨算（财务管控） 墨律（法务合规）
     墨人（人力资源） 墨路（成本路由）🆕
```

每个公司拥有独立的：飞书机器人 · 商业闭环 · KPI 仪表盘 · 记忆空间 · 领域配置文件

→ [完整架构文档](AGENTS.md) · [特工索引](AGENT_REGISTRY.md)

---

## 快速开始

### 前置要求

- **macOS / Linux** (Windows 通过 WSL 支持)
- **Python 3.9+**
- **Git**
- 飞书开发者账号（用于创建 6 个机器人）
- 大模型 API Key（DeepSeek / 阿里百炼 / OpenAI 兼容接口）

### 一键部署

```bash
# 克隆仓库
git clone git@github.com:moye-tech/Molin-OS.git
cd Molin-OS

# 一键部署（安装依赖 + 配置 Hermes Agent + 创建 Profile 模板）
bash setup.sh
```

部署完成后，编辑各 Profile 的环境变量文件填入 API 密钥：

```bash
# 编辑各公司配置
vim config/hermes-agent/profiles/yuanyao/.env
vim config/hermes-agent/profiles/ziling/.env
vim config/hermes-agent/profiles/yinyue/.env
vim config/hermes-agent/profiles/meining/.env
vim config/hermes-agent/profiles/songyu/.env
vim config/hermes-agent/profiles/xuanhu/.env
```

### 启动系统

```bash
# 后台异步任务处理器（必需的守护进程）
make run-background

# 异步飞书网关（如需飞书接入，端口 8000）
make run-gateway

# 查看系统状态
make status

# 查看所有可用命令
make help
```

→ [完整安装指南](ENVIRONMENT.md)

---

## 系统架构

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          Hermes Agent (AI 调度引擎)                        │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  6 Profile 身份系统 · 智能路由 · 工具调用 · 多模型高可用网关           │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────┤
│  molib 执行层 (工业级硬化)                                                 │
│  ┌────────────┬───────────────┬──────────────┬──────────────────────────┐ │
│  │ Flywheel   │ CircuitBreaker│ SandboxExec  │ SkillCompiler            │ │
│  │ 图控状态机   │ Handoff 校验   │ 技能隔离沙箱   │ Pydantic 强类型约束        │ │
│  ├────────────┼───────────────┼──────────────┼──────────────────────────┤ │
│  │ DataBus    │ MemoryPalace  │ VaultIO      │ MemoryCompactor          │ │
│  │ 原子数据总线  │ 自适应记忆管理   │ Obsidian 缓冲  │ Levenshtein 去重          │ │
│  ├────────────┼───────────────┼──────────────┼──────────────────────────┤ │
│  │ TaskQueue  │ AgentLogger   │ MiroFish     │ SmartScraper             │ │
│  │ 异步任务队列  │ 全链路追踪日志   │ 预测引擎+探针  │ AI 友好网页采集            │ │
│  └────────────┴───────────────┴──────────────┴──────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│  数据层                                                                    │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────────────────┐ │
│  │ Obsidian │ MemPalace│ ChromaDB │ SQLite   │ AtomicDataBus            │ │
│  │ 四层知识库  │ 语义检索   │ 向量存储   │ 任务队列   │ WAL 事务总线              │ │
│  └──────────┴──────────┴──────────┴──────────┴──────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│  可观测层                                                                  │
│  ┌──────────────────────┬───────────────────────────────────────────────┐ │
│  │ AgentTraceLogger     │ Langfuse Dashboard (自托管 Docker, :3000)       │ │
│  │ JSONL 结构化追踪       │ 可视化调用链路 + 成本看板 + 异常报警              │ │
│  └──────────────────────┴───────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────┤
│  通道层                                                                     │
│  飞书 6 Bot · Async Gateway (8000) · CLI 终端 · REST API · Telegram          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 核心数据流

```
用户消息 → Hermes Agent (Profile 路由)
         → molib 执行层 (技能匹配 + 飞轮调度)
         → Worker (异步任务队列执行)
         → 数据总线 (原子写入)
         → Obsidian / ChromaDB (知识沉淀)
         → AgentLogger (全链路追踪)
         → 飞书 / CLI (结果返回)
```

---

## 核心能力

### 🔄 无人值守商业飞轮

系统每日自动完成「情报采集 → 内容生产 → 增长分发」的完整链路：

```
08:00 — 情报银行   紫灵 AI 扫描 arXiv、行业博客、竞品动态 → 生成情报简报
09:20 — 内容工厂   银月基于情报自动生成小红书 / 公众号 / 短视频内容
10:45 — 增长引擎   元瑶执行 SEO 优化、跨平台分发、效果追踪与策略调整
```

三棒全自动接力。任一环节断裂，系统触发级联告警（断路器熔断），防止空转浪费 Token。

### 🧠 四层记忆架构

AI 不会「忘记」你告诉过它的事。记忆系统支持跨会话持久化，并自动去重合并。

| 层级 | 存储介质 | 生命周期 | 用途 |
|:----:|:---------|:---------|:-----|
| L1 | 对话上下文窗口 | 24h | 当前任务连贯性 |
| L2 | Obsidian 结构化笔记 | 永久 | 项目决策、客户偏好、业务知识 |
| L3 | Obsidian 六司根目录 | 永久 | 知识资产系统化沉淀 |
| L4 | SKILL.md 版本化文件 | 永久 | 可复现的标准工作流 |

辅助记忆模块：
- **MemPalace** (ChromaDB 语义向量检索) — 模糊匹配历史记忆
- **MemoryPalace v2** (自适应记忆) — 自动判断 INSERT / UPDATE / MERGE / IGNORE
- **MemoryCompactor** (Levenshtein 去重) — 防止 Token 膨胀
- **Memory GC** (定时浓缩) — 碎片记忆浓缩固化到 Obsidian

### 🚪 全通道接入

```
飞书 6 Bot ─┬─ 元瑶 Bot (教育咨询、课程服务)
             ├─ 紫灵 Bot (情报简报、竞品推送)
             ├─ 银月 Bot (内容发布、媒体管理)
             ├─ 梅凝 Bot (跨境运营、全球市场)
             ├─ 宋玉 Bot (产品孵化、威客接单)
             └─ 玄骨 Bot (系统管控、安全审计)

CLI 终端 · REST API · Telegram · Discord · 企微
```

异步飞书网关 (`engine/gateway_async.py`) 在 1 秒内闪回 `200 ACK` 响应，彻底解决飞书 5 秒 Webhook 重试风暴。

### 🏛️ 五级治理体系

| 级别 | 策略 | 触发条件示例 |
|:----:|:-----|:-------------|
| L0 自动执行 | 无需确认，直接执行 | 内容生成、数据采集、例行报告 |
| L1 知会通知 | 执行完毕告知创始人 | 系统更新、任务完成 |
| L2 审批确认 | 等待创始人确认后执行 | 对外发布、报价 > ¥100、修改配置 |
| L3 董事会 | 全面评估后执行 | 战略方向调整、新项目立项 |
| L4 绝对禁止 | 直接拒绝，不做任何操作 | 真实资金操作、支付转账 |

### 📊 商业闭环

每个公司有独立的变现路径，不是松散的工具集合，而是真正的业务系统：

- **元瑶（教育增长）**：引流获客 → 私域沉淀 → 发售转化 → 课程交付 → 督学复购 → 闲鱼接单 → A/B 测试优化
- **紫灵（情报战略）**：趋势嗅探 → 竞品监控 → SEO关键词 → 数据清洗 → 结构化研报 → MVP验证 → ROI精算
- **银月（内容媒体）**：选题策划 → 爆款写作 → 视觉设计 → 视频后期 → SEO深度长文 → 直播变现 → 内容调度发布
- **梅凝（跨境出海）**：内容本地化 → 独立站搭建 → 跨境支付 → 合规审查 → 海外获客 → 产品分发发版
- **宋玉（产品孵化）**：极简PRD → 技术选型 → 免费钩子 → 冷启动获客 → 威客接单 → 定价策略 → 平台申诉 → 产品发版
- **玄骨（底层中枢）**：成本路由 → 算力调度 → 研发部署 → 运维守护 → 安全审计 → 财务管控 → 自进化

---

## 工业级硬化体系 (v7.5.0)

v7.5.0 在原有业务能力基础上，注入了 **16 个工业级防御模块**，针对真实生产环境中会导致系统崩溃、死锁、数据污染的 12 类致命缺陷进行底层加固。全部采用纯 Python + SQLite 实现，**零外部服务依赖**。

### 防御矩阵总览

| # | 模块 | 文件路径 | 解决的致命缺陷 |
|---|------|----------|---------------|
| 1 | **原子数据总线** | `molib/data_bus.py` | 飞轮管线 relay/ 目录的文件竞态条件与状态丢失 |
| 2 | **异步任务队列** | `molib/task_queue.py` | Hermes 主循环阻塞导致飞书 Webhook 超时 |
| 3 | **后台执行器** | `engine/background_worker.py` | 长时间任务阻塞用户交互 |
| 4 | **飞轮断路器** | `molib/circuit_breaker.py` | 上游大模型幻觉导致下游级联崩溃 |
| 5 | **沙箱执行器** | `molib/sandbox_executor.py` | 339 个技能的 Python 依赖地狱与版本冲突 |
| 6 | **异步飞书网关** | `engine/gateway_async.py` | 6 个飞书 Bot 的 5 秒重试风暴 |
| 7 | **飞轮图控引擎** | `molib/flywheel_graph.py` | 扁平 Handoff 无法表达复杂条件分支与循环 |
| 8 | **强类型编译器** | `molib/skill_compiler.py` | 自然语言 Prompt 约束失效导致 JSON 解析崩溃 |
| 9 | **强类型校验器** | `molib/validators.py` | LLM 多吐字符导致自动化流水线 ValueError |
| 10 | **记忆压缩器** | `molib/memory_compactor.py` | 向量库指数膨胀导致 Token 黑洞与上下文稀释 |
| 11 | **自适应记忆** | `molib/memory_palace_v2.py` | 重复记忆堆积导致语义检索精度下降 |
| 12 | **记忆回收站** | `scripts/memory_gc_job.py` | ChromaDB 碎片记忆永不清除导致存储爆炸 |
| 13 | **Vault 写入缓冲** | `molib/vault_io.py` | Obsidian 被 iCloud/Git 锁定时 Worker 写入失败 |
| 14 | **MiroFish 探针** | `engine/mirofish/probe.py` | 预测引擎与业务闭环脱节，无法自动降级 |
| 15 | **全链路日志** | `molib/agent_logger.py` | AI 行为黑盒，无法追踪 Token 消耗与错误根源 |
| 16 | **多模型网关** | `molib/hermes_gateway.py` | 单模型故障导致全系统不可用，缺乏自动降级 |

### 硬化配置

所有防御参数集中在 `config/system_hardening.yaml` 中统一管理：

```yaml
# 数据总线
data_bus:
  engine: "sqlite3-wal"
  timeout_seconds: 30.0

# 断路器
circuit_breaker:
  intelligence_confidence_threshold: 0.7    # 置信度 < 0.7 触发熔断

# 记忆降噪
memory_gc:
  similarity_dedup_threshold: 0.78         # 相似度 > 0.78 触发合并
  nightly_consolidation_hour: 2             # 凌晨 2 点浓缩

# MiroFish 闭环
mirofish_monitoring:
  anomaly_auto_breaker: true               # 跌破预测基线自动熔断
  probe_interval_seconds: 1800             # 30 分钟检测一次
```

### 智能采集器

`skills/utils/smart_scraper.py` 提供 AI 友好的网页采集能力：

- 自动剔除导航栏、Footer、广告弹窗等 HTML 噪声
- 输出纯净 Markdown，直接喂给大模型
- 支持 crawl4ai 引擎（高鲁棒性）和本地 BeautifulSoup 降级方案
- 并发批量采集，自动计算 Token 预估消耗

---

## 项目结构

```
Molin-OS/
├── README.md                      本文件
├── AGENTS.md                      Hermes Agent 系统提示 · Worker 映射 · CLI 命令索引
├── SYSTEM.md                      主脑 SOP · 记忆架构 · 执行规范
├── SOUL.md                        CEO 认知框架 · Worker 链 · 决策原则
├── AGENT_REGISTRY.md              44 Worker 完整索引与能力描述
├── ENVIRONMENT.md                 环境安装与配置指南
├── LICENSE                        MIT 许可证
├── Makefile                       一键操作（make help 查看全部）
├── setup.sh                       一键部署脚本
│
├── config/
│   ├── domains/                   6 领域 YAML 配置 (商业闭环 + KPI)
│   │   ├── yuanyao_edu_growth.yaml
│   │   ├── ziling_intelligence.yaml
│   │   ├── yinyue_media.yaml
│   │   ├── meining_global.yaml
│   │   ├── songyu_innovation.yaml
│   │   └── xuanhu_infrastructure.yaml
│   ├── hermes-agent/              Hermes Agent 配置
│   │   ├── .env.example          全局环境变量模板
│   │   ├── config.yaml.template   主配置模板
│   │   ├── cron_jobs.md           19 个定时任务排班表
│   │   └── profiles/              6 个 Profile 独立配置
│   │       ├── yuanyao/           .env 模板 · 飞书 Bot 配置
│   │       ├── ziling/
│   │       ├── yinyue/
│   │       ├── meining/
│   │       ├── songyu/
│   │       └── xuanhu/
│   └── system_hardening.yaml      系统硬化防御参数（v7.5.0 新增）
│
├── molib/                         Python 核心执行引擎
│   ├── __init__.py
│   ├── __main__.py                CLI 入口 (python -m molib ...)
│   ├── task_queue.py              异步任务队列引擎
│   ├── data_bus.py                原子 SQLite WAL 数据总线
│   ├── circuit_breaker.py         Handoff 校验与断路器
│   ├── sandbox_executor.py        隔离沙箱技能执行器
│   ├── flywheel_graph.py          图控飞轮状态机
│   ├── skill_compiler.py          Pydantic 强类型编译器
│   ├── validators.py              Instructor 风格校验器
│   ├── memory_compactor.py        Levenshtein 去重引擎
│   ├── memory_palace_v2.py        自适应记忆管理器
│   ├── agent_logger.py            JSONL 全链路日志
│   ├── vault_io.py                Obsidian 安全写入缓冲
│   ├── hermes_gateway.py          多模型高可用网关
│   ├── agencies/                  44 Worker 实现
│   │   ├── smart_dispatcher.py   智能分发器
│   │   ├── kanban_chain.py       Kanban 编排链
│   │   ├── handoff_register.py   Handoff 注册表
│   │   └── workers/              各 Worker 代码
│   ├── ceo/                       CEO 调度层
│   │   ├── semantic_router.py    语义路由
│   │   └── intent_router.py      意图分发
│   ├── intelligence/              MiroFish 预测管线
│   └── integrations/              外部集成 (NotebookLM 等)
│
├── engine/
│   ├── background_worker.py       后台异步任务消费者
│   ├── gateway_async.py           FastAPI 飞书多路复用网关
│   └── mirofish/                  MiroFish 预测引擎
│       ├── probe.py               闭环预测探针（v7.5.0 新增）
│       ├── backend/               FastAPI 后端服务
│       ├── locales/               多语言支持
│       └── reports/               预测报告输出
│
├── hermes/                        Hermes Agent 引擎源码 (vendored)
│   ├── agent/                     核心 AI 调度引擎
│   ├── gateway/                   多通道消息网关
│   ├── hermes_cli/                CLI 工具
│   └── ...
│
├── skills/                        技能库
│   ├── global/                    全局通用技能 (150+ SKILL.md)
│   ├── domains/                   领域专属技能 (按六司分目录)
│   ├── utils/                     工具类技能
│   │   └── smart_scraper.py       AI 智能采集器（v7.5.0 新增）
│   └── archive/                   历史归档技能 (保留以备参考)
│
├── scripts/
│   └── memory_gc_job.py           记忆垃圾回收定时脚本
│
├── docs/                          项目文档
│   ├── SYSTEM_OVERVIEW.md         系统全景概述
│   ├── CRON_JOBS_AUDIT.md         定时任务审计
│   ├── business/                  业务文档
│   └── archive/                   历史文档归档
│
├── tests/                         测试套件
│   ├── unit/                      单元测试
│   ├── integration/               集成测试
│   └── conftest.py                Pytest 配置
│
├── vault/                         Obsidian 知识库（四层结构）
│   ├── 系统层/                     架构演进 · 部署环境 · 安全数据 · 决策记录
│   ├── 业务层/                     产品定义 · 项目生命周期 · 自动化工作流
│   ├── 运营层/                     商业战略 · 增长营销 · 财务法务
│   └── 知识库/                     前沿 AI 技术 · 行业研究 · 记忆科学
│
└── relay/                         飞轮管线运行时数据 (gitignored)
```

---

## 命令速查

### 一键操作 (make)

```bash
make help              查看所有命令
make status            系统实时状态（Worker、队列、总线）
make run-background    启动后台异步任务处理器
make run-gateway       启动异步飞书网关（端口 8000）
make run-monitor       启动 Langfuse 可观测面板（需要 Docker）
make gc-memory         执行 ChromaDB 记忆浓缩
make vault-flush       将缓冲记忆固化到 Obsidian
make bus-stats         查看原子数据总线统计
make memory-stats      查看自适应记忆管理统计
make test              运行测试套件
make lint              语法校验
make clean             清理构建产物
make backup            创建时间戳备份
```

### CLI 命令 (python -m molib)

```bash
# 系统
python -m molib health                       系统健康检查
python -m molib help                         查看所有 CLI 命令

# 队列管理
python -m molib queue stats                  队列统计
python -m molib queue push --worker W --skill S --payload '{}'  推送任务

# 日志
python -m molib agent-log errors             查看错误日志
python -m molib agent-log cost               查看 Token 成本

# 内容创作
python -m molib content write --topic T --platform P    创作内容
python -m molib xhs generate --topic T                   小红书内容
python -m molib video script --topic T --duration D      视频脚本

# 设计
python -m molib design image --prompt P --style S        AI 生图
python -m molib design web --prompt P --action landing_page   网页生成

# 情报
python -m molib intel predict --topic T --context C      群体智能预测
python -m molib intel trending                           热门趋势
python -m molib scrap fetch --url URL                    网页抓取

# 财务
python -m molib finance record --type T --amount A --note N    记账
python -m molib finance report                           财务报告
```

---

## 依赖说明

### 必需依赖

| 组件 | 说明 | 安装方式 |
|------|------|---------|
| Python 3.9+ | 核心运行时 | 系统自带或 `brew install python` |
| Hermes Agent | AI 调度引擎 | 已 vendored 在 `hermes/` 目录中，`setup.sh` 自动安装 |
| Git | 版本控制 | 系统自带 |
| SQLite 3 | 嵌入式数据库 | Python 内置，无需额外安装 |

### 可选依赖

| 组件 | 用途 | 安装方式 |
|------|------|---------|
| ChromaDB | 语义向量检索 (MemPalace) | `pip install chromadb` |
| FastAPI + Uvicorn | 异步飞书网关 | `pip install fastapi uvicorn` |
| Docker | Langfuse 可观测面板 | `brew install docker` |
| DiskCache | Obsidian 写入缓冲 | `pip install diskcache` |
| crawl4ai | 高鲁棒性网页采集 | `pip install crawl4ai` |
| litellm | 多模型统一网关 | `pip install litellm` |

### API 密钥

| 服务 | 用途 | 获取方式 |
|------|------|---------|
| DeepSeek API | 主力大模型 | [platform.deepseek.com](https://platform.deepseek.com) |
| 阿里百炼 | 备用大模型 | [bailian.console.aliyun.com](https://bailian.console.aliyun.com) |
| 飞书开放平台 | 6 个机器人 | [open.feishu.cn](https://open.feishu.cn) |

---

## 版本历史

| 版本 | 日期 | 里程碑 |
|:----:|:-----|:-------|
| **v8.0** | 2026-05 | 六司四十四将架构 · 宋玉完整重构为产品孵化公司 · 新增 16 个 Agent（44 将）· 19 个 Cron 作业 |
| **v7.5.0** | 2026-05 | 工业级硬化：16 个防御模块 · 原子数据总线 · 沙箱隔离 · 异步网关 · 记忆压缩 · 强类型约束 |
| v7.0 | 2026-05 | 六司三十四将架构 · 6 Profile 飞书 Bot · YAML 配置标准化 |
| v6.0 | 2026-05 | 五域一枢 · 5 Profile 体系 |
| v5.0 | 2026-05 | 扁平化 Vault · 零子模块架构 |

---

## 设计哲学

### 零付费 (Zero-Cost)
不依赖任何付费云服务。大模型使用 DeepSeek / 阿里百炼免费额度，记忆存储用本地 ChromaDB，知识库用 Obsidian + iCloud。如果你有 API Key，月成本可以为零。

### 本地优先 (Local-First)
所有数据存储在你的设备上。Obsidian Vault 通过 iCloud 同步，GitHub 做远程备份。数据不会离开你的设备，除非你主动发布。

### 单人可维护 (Solo-Maintainable)
设计目标是一个人能看懂、能修改、能排错的系统。核心代码用纯 Python 编写，配置用 YAML/Markdown，不需要 Kubernetes、不需要微服务、不需要分布式共识。

### 反脆弱 (Anti-Fragile)
每一次 Handoff 都经过断路器校验。每一个重型技能都运行在独立沙箱中。每一条记忆都经过去重合并。每一个边界都有熔断机制。系统优雅降级，绝不级联崩溃。

### 一键部署 (One-Click Deploy)
`bash setup.sh` 即可完成从零到运行的完整部署。所有依赖自动安装，所有配置模板自动生成，所有 Profile 目录自动创建。

---

## 许可证

MIT License · Copyright (c) 2026 [moye-tech](https://github.com/moye-tech)

---

<p align="center">
  <sub>Built with ❤️ for solo founders who refuse to compromise.</sub>
</p>
