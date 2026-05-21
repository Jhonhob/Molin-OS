<p align="center">
  <img src="https://img.shields.io/badge/version-v7.5.0--Hardened-6C5CE7?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/workers-34-00B894?style=flat-square" alt="workers">
  <img src="https://img.shields.io/badge/profiles-6-0984E3?style=flat-square" alt="profiles">
  <img src="https://img.shields.io/badge/license-MIT-636E72?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/python-3.9+-FFEAA7?style=flat-square" alt="python">
</p>

<h1 align="center">墨麟 OS &nbsp;·&nbsp; Molin-OS</h1>

<p align="center"><strong>Single-Person AI Business Operating System</strong></p>
<p align="center">6 Companies · 34 AI Workers · 1 Human</p>

---

## What is Molin-OS

Molin-OS is a **local-first, zero-cost AI operating system** that compresses the complete business capabilities of a holding company — market intelligence, content production, e-commerce operations, financial auditing — into a single locally-running Python system.

You don't need a team. You need a terminal.

**The problem it solves:** Traditional solo-business toolchains are fragmented — ChatGPT for copy, Midjourney for images, Notion for management, Feishu for customer service. Switching costs are high, information is siloed, and automation loops are impossible.

Molin-OS replaces all of this with a unified AI operating system:

| Feature | Description |
|---------|-------------|
| **6 AI Profiles** | Replace 6 VPs, each managing a complete business domain |
| **34 Specialized Workers** | From competitor tracking to live-stream sales, each an expert |
| **Automated Flywheel Pipeline** | Intelligence → Content → Growth, runs unattended daily |
| **Zero External Costs** | All components self-hosted, free, local-first |
| **Industrial-Grade Hardening** | Circuit breakers, sandbox isolation, async gateway, memory GC |

---

## Six-Subsidiary Architecture (六司三十四将)

```
🌸 Yuanyao · Education & User Growth
     墨增 墨销 墨导 墨学 墨创 墨域

🔮 Ziling · Intelligence & Strategy Research
     墨研 墨数 墨影 墨嗅 墨投

🌙 Yinyue · Content Ecosystem & Omni-Media
     墨笔 墨图 墨剪 墨链 墨播 墨星

❄️ Meining · Cross-Border & Globalization
     墨译 墨媒 墨站 墨航 墨盾

🍃 Songyu · Innovation & Commercialization
     墨商 墨案 墨关 墨聚 墨采

💀 Xuanhu · Core Infrastructure & Group Enablement
     墨码 墨维 墨安 墨梦 墨算 墨律 墨人
```

Each subsidiary has its own: Feishu Bot · Business Loop · KPI Dashboard · Memory Space · Domain Config

→ [Full Architecture](AGENTS.md) · [Worker Registry](AGENT_REGISTRY.md)

---

## Quick Start

```bash
git clone git@github.com:moye-tech/Molin-OS.git
cd Molin-OS
bash setup.sh
```

The system auto-installs Python dependencies, configures Hermes Agent, and creates profile templates. Fill in your Feishu bot credentials and API keys to start.

```bash
# Start background task worker
make run-background

# Check system status
make status

# Start async Feishu gateway
make run-gateway
```

→ [Full Installation Guide](ENVIRONMENT.md)

---

## Core Capabilities

### 🔄 Unattended Business Flywheel

The system automatically completes the full intelligence-to-publishing pipeline daily:

```
08:00 ─ Intelligence Bank    AI scans arXiv, blogs, competitor updates → briefing
09:20 ─ Content Factory      Generates social media / video content from intelligence
10:45 ─ Growth Engine        SEO optimization, cross-platform distribution, analytics
```

Three-stage relay automation. Cascading alerts on any link failure.

### 🧠 Four-Layer Memory Architecture

The AI never "forgets" what you've told it.

| Layer | Storage | Lifetime | Purpose |
|:-----:|:--------|:---------|:--------|
| L1 | Conversation context | 24h | Task continuity |
| L2 | Obsidian structured notes | Permanent | Project decisions, client preferences |
| L3 | Obsidian vault directories | Permanent | Knowledge asset accumulation |
| L4 | SKILL.md versioned | Permanent | Reproducible workflows |

### 🚪 Omni-Channel Access

```
Feishu 6 Bots ─┬─ Yuanyao Bot (education consulting)
                ├─ Ziling Bot  (intelligence briefing)
                ├─ Yinyue Bot  (content publishing)
                ├─ Meining Bot (cross-border ops)
                ├─ Songyu Bot  (business development)
                └─ Xuanhu Bot  (system governance)

CLI Terminal · REST API · Telegram · Discord
```

### 🏛️ Five-Level Governance

| Level | Policy | Example |
|:-----:|:-------|:--------|
| L0 Auto | No confirmation needed | Content generation, data collection |
| L1 Notify | Inform after completion | System updates, task completion |
| L2 Approve | Wait for founder confirmation | External publishing, config changes |
| L3 Board | Full assessment before execution | Strategic direction, new projects |
| L4 Forbidden | Direct rejection | Real fund operations, payments |

### 📊 Business Loops

Each subsidiary has an independent monetization path:

- **Yuanyao**: Lead gen → Private domain → Launch conversion → Course delivery → Retention
- **Ziling**: Trend detection → Competitor monitoring → Data cleaning → ROI estimation → Research reports
- **Yinyue**: Topic planning → Viral writing → Visual design → Video editing → Live commerce
- **Meining**: Content localization → Site building → Overseas acquisition → Supply chain → Compliance
- **Songyu**: BD outreach → Custom proposals → Government relations → Procurement → Events
- **Xuanhu**: Compute scheduling → R&D deployment → Security audit → Financial control → Self-evolution

---

## Industrial Hardening (v7.5.0)

Molin-OS v7.5.0 includes production-grade defenses against real-world failure modes:

| Module | File | Problem Solved |
|--------|------|---------------|
| **Atomic Data Bus** | `molib/data_bus.py` | File race conditions in relay/ pipelines |
| **Sandbox Executor** | `molib/sandbox_executor.py` | 339-skills dependency conflict isolation |
| **Async Gateway** | `engine/gateway_async.py` | Feishu 5-second retry timeout storms |
| **Memory Compactor** | `molib/memory_compactor.py` | Levenshtein dedup to prevent token bloat |
| **Circuit Breaker** | `molib/circuit_breaker.py` | Cascade failure prevention on handoff |
| **Flywheel Graph** | `molib/flywheel_graph.py` | LangGraph-style state machine with L2 governance |
| **Strong Typing** | `molib/skill_compiler.py` + `validators.py` | Pydantic enforcement to eliminate LLM hallucinations |
| **Vault I/O Buffer** | `molib/vault_io.py` | DiskCache isolation to prevent Obsidian file locks |
| **MiroFish Probe** | `engine/mirofish/probe.py` | Closed-loop prediction → circuit breaker triggering |
| **Multi-Model Gateway** | `molib/hermes_gateway.py` | LiteLLM-style auto-fallback with rate limiting |
| **Adaptive Memory** | `molib/memory_palace_v2.py` | Mem0-style INSERT/UPDATE/MERGE/IGNORE decisions |
| **Smart Scraper** | `skills/utils/smart_scraper.py` | Crawl4AI-inspired noise-free web extraction |
| **Agent Logger** | `molib/agent_logger.py` | JSONL trace logging for cost and error tracking |
| **Task Queue** | `molib/task_queue.py` | SQLite-based async queue for non-blocking execution |
| **Memory GC** | `scripts/memory_gc_job.py` | Nightly ChromaDB consolidation to Obsidian |
| **Hardening Config** | `config/system_hardening.yaml` | Centralized defense parameter management |

All hardening modules are **pure Python, zero external dependencies, local-first**.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Hermes Agent (AI Scheduler)                   │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │              HermesGateway (Multi-Model HA + Auto-Fallback)       │ │
│  └─────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│  molib Execution Layer (Industrial Hardened)                         │
│  ┌────────────┬───────────────┬──────────────┬─────────────────────┐ │
│  │ Flywheel   │ CircuitBreaker│ SandboxExec  │ SkillCompiler       │ │
│  │ Graph 状态机│ Handoff 校验   │ 技能隔离沙箱  │ Pydantic 强类型约束   │ │
│  ├────────────┼───────────────┼──────────────┼─────────────────────┤ │
│  │ DataBus    │ MemoryPalace  │ VaultIO      │ MemoryCompactor     │ │
│  │ 原子数据总线 │ 自适应记忆管理  │ Obsidian缓冲  │ Levenshtein 去重     │ │
│  └────────────┴───────────────┴──────────────┴─────────────────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│  Data Layer                                                          │
│  ┌──────────┬──────────┬──────────┬──────────┬────────────────────┐ │
│  │ Obsidian │ MemPalace│ ChromaDB │ TaskQueue│ AtomicDataBus      │ │
│  │ 知识库    │ 语义检索  │ 向量存储  │ SQLite队列│ SQLite WAL 总线    │ │
│  └──────────┴──────────┴──────────┴──────────┴────────────────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│  Observability                                                       │
│  ┌──────────────────────┬──────────────────────────────────────────┐ │
│  │ AgentTraceLogger     │ Langfuse Dashboard (localhost:3000)       │ │
│  │ JSONL 全链路追踪       │ Docker 自托管可观测面板                    │ │
│  └──────────────────────┴──────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│  Channel Layer                                                       │
│  Feishu 6 Bots · Async Gateway (port 8000) · CLI · REST · Telegram  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
Molin-OS/
├── AGENTS.md                  System prompt · Worker mapping · CLI commands
├── SYSTEM.md                  Master brain SOP · Memory architecture
├── SOUL.md                    CEO cognitive framework · Worker chains
├── AGENT_REGISTRY.md          34 Worker index
├── ENVIRONMENT.md             Installation & environment setup
├── Makefile                   One-command operations (make help)
├── setup.sh                   One-click deployment script
├── config/
│   ├── domains/               6 Domain YAML (business loops + KPIs)
│   ├── hermes-agent/          Hermes Agent profile templates · Cron definitions
│   └── system_hardening.yaml  Centralized defense configuration
├── molib/                     Python execution engine
│   ├── task_queue.py          SQLite async task queue
│   ├── data_bus.py            Atomic SQLite WAL data bus
│   ├── circuit_breaker.py     Handoff validation & cascade prevention
│   ├── sandbox_executor.py    Isolated skill execution environments
│   ├── flywheel_graph.py      LangGraph-inspired state machine
│   ├── skill_compiler.py      Pydantic schema enforcement
│   ├── validators.py          Instructor-style strong typing
│   ├── memory_compactor.py    Levenshtein dedup engine
│   ├── memory_palace_v2.py    Adaptive memory (INSERT/UPDATE/MERGE/IGNORE)
│   ├── agent_logger.py        JSONL trace logging & cost tracking
│   ├── vault_io.py            DiskCache buffer for Obsidian writes
│   ├── hermes_gateway.py      Multi-model HA gateway with auto-fallback
│   ├── agencies/              34 Worker implementations
│   ├── ceo/                   Semantic routing & intent dispatch
│   ├── intelligence/          MiroFish prediction pipeline
│   └── __main__.py            CLI entry point (python -m molib ...)
├── engine/
│   ├── background_worker.py   Async task queue consumer
│   ├── gateway_async.py       FastAPI async Feishu webhook multiplexer
│   └── mirofish/              MiroFish prediction engine + closed-loop probe
├── skills/
│   ├── global/                Cross-domain skills (150+ SKILL.md)
│   ├── domains/               Domain-specific skills by subsidiary
│   └── utils/                 Utility skills (smart_scraper, etc.)
├── scripts/
│   └── memory_gc_job.py       Nightly ChromaDB memory consolidation
├── tests/                     Test suite (unit + integration)
├── docs/                      Documentation & historical archives
├── vault/                     Obsidian knowledge base (4-layer structure)
│   ├── 系统层/                 System layer (architecture, security, deployment)
│   ├── 业务层/                 Business layer (products, projects, workflows)
│   ├── 运营层/                 Operations layer (finance, growth, strategy)
│   └── 知识库/                 Knowledge base (AI research, industry, methodology)
└── relay/                     Flywheel pipeline data (runtime, gitignored)
```

---

## Design Philosophy

**Zero-Cost (零付费)**
No paid cloud services. LLMs via DeepSeek / Alibaba Bailian free tiers. Memory via local ChromaDB. Knowledge base via Obsidian + iCloud. Monthly cost can reach zero with API keys.

**Local-First (本地优先)**
All data stored locally. Obsidian Vault synced via iCloud, GitHub as remote backup. No data leaves your device unless you explicitly publish.

**Solo-Maintainable (单人可维护)**
Designed for one person to understand, modify, and debug. Core logic in plain Python with YAML/Markdown config. No Kubernetes, no microservices, no distributed systems.

**Anti-Fragile (反脆弱)**
Every handoff validated. Every skill sandboxed. Every memory deduplicated. Circuit breakers at every boundary. The system degrades gracefully, never cascades.

---

## Commands

```bash
make help              # Show all commands
make status            # System live status (workers, queue, bus)
make run-background    # Start async task worker
make run-gateway       # Start async Feishu gateway (port 8000)
make run-monitor       # Start Langfuse observability dashboard
make gc-memory         # Run ChromaDB memory consolidation
make vault-flush       # Flush memory buffer to Obsidian
make bus-stats         # AtomicDataBus statistics
make memory-stats      # AdaptiveMemoryManager statistics
make test              # Run test suite
make lint              # Syntax validation
make clean             # Remove build artifacts
make backup            # Create timestamped backup
```

---

## Dependencies

- **Hermes Agent** — AI scheduling engine. Install via `pip install hermes-agent` or `brew install hermes-agent`. Configuration in `config/hermes-agent/`.
- **Python 3.9+** — Core runtime
- **SQLite 3** — Built-in, no install needed
- **Optional**: ChromaDB (memory vectors), FastAPI + Uvicorn (async gateway), Docker (Langfuse observability)

---

## Version History

| Version | Date | Milestone |
|:-------:|:-----|:----------|
| v7.5.0 | 2026-05 | Industrial hardening: 16 defense modules, atomic data bus, sandbox isolation, async gateway |
| v7.0 | 2026-05 | Six-subsidiary 34-worker architecture · 6 Profile Feishu Bots · YAML standardization |
| v6.0 | 2026-05 | Five-domain one-hub · 5 Profiles |
| v5.0 | 2026-05 | Flat vault structure · Zero submodule architecture |

---

## License

MIT · [moye-tech/Molin-OS](https://github.com/moye-tech/Molin-OS)
