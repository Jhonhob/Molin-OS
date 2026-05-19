# 墨麟 OS · Molin-OS 产品介绍文档

| 版本: v5.0 | 最后更新: 2026-05-19 | 开源协议: MIT
> 标语: 一个人，一台 MacBook，一个 AI 集团。

---

## 一、产品概述

墨麟 OS（Molin-OS）是一套**AI 原生一人公司操作系统**。它不是工具集、不是 Copilot、不是 Agent 框架——而是一个完整的**AI 集团运营系统**，让一个人用一台 MacBook 就能驱动覆盖营销、运营、技术、财务、战略五大领域的 20 家虚拟子公司。

创始人墨烨通过飞书对话或 CLI 下达指令，CEO Agent（Hermes）进行智能决策和任务编排，20 家子公司 Worker 自动产出可交付的成果。

系统月收入目标 ¥52,000，已在真实商业运营中运行。

---

## 二、核心数据

- Python 代码: 89,713 行（447 模块）
- 技能库: 389 项技能
- Worker 文件: 52 个
- 子公司: 20 家
- Cron 定时作业: 19 项
- 子技能库: 约 30-40 子目录（按业务线组织）
- 运行环境: M2 MacBook 8GB 内存
- 月运营预算: ¥1,360（AI API + 工具 + 推广）
- 月收入目标: ¥52,000
- 开源协议: MIT

---

## 三、系统架构

### 3.1 执行模型

```
创始人（飞书/CLI/API）
        │
        ▼
Hermes Agent（大脑）— DARE v3.0 推理框架
        │  python -m molib <command>
        ▼
molib（执行层 / 447 模块 · 50+ CLI 命令）
        │
        ├── 20 家子公司 Worker
        ├── 389 项技能
        └── 5 级治理门禁
        │
        ▼
可交付成果（内容/设计/客服回复/订单/报表/情报）
        │
        ▼
Obsidian 产出/ + 飞书通知
```

### 3.2 三层架构

**大脑层 — Hermes Agent（Nous Research）**
- 基于 DARE v3.0 推理框架：Decompose · Analyze · Route · Elevate
- 强制委托协议：CEO 只做决策和编排，不自己写内容/代码
- 飞书对话 + CLI + REST API 三种接入方式

**执行层 — molib Package（89,713 行 Python）**
- 统一 CLI 入口: `python -m molib <command>`
- 50+ 命令覆盖所有业务线
- Handoff 自动路由系统（16 个领域自动匹配 Worker）
- 规划分解引擎（智能拆解复杂任务）

**技能层 — 389 项技能**
- 从 SEO 优化到量化交易
- 从像素艺术到红队安全测试
- 从 Excalidraw 架构图到 ComfyUI 图像生成

---

## 四、20 家子公司体系

### VP 营销（5家）

| 子公司 | 中文名 | 核心能力 |
|--------|-------|---------|
| Content Writer | 墨笔文创 | 品牌文案、小红书、公众号、SEO内容 |
| IP Manager | 墨韵IP | IP孵化、版权管理、品牌衍生 |
| Designer | 墨图设计 | FLUX.2生图、149设计系统、封面/UI |
| Short Video | 墨播短视频 | 短视频脚本+生成、FFmpeg视频引擎 |
| Voice Actor | 墨声配音 | AI语音合成、播客制作、TTS |

### VP 运营（4家）

| 子公司 | 中文名 | 核心能力 |
|--------|-------|---------|
| CRM | 墨域私域 | 用户分层、社群运营、RFM模型 |
| Customer Service | 墨声客服 | 自动化客服、闲鱼消息检测回复 |
| E-commerce | 墨链电商 | 订单管理、交易链路、多平台 |
| Education | 墨学教育 | 课程设计、AI导师、学习路径 |

### VP 技术（4家）

| 子公司 | 中文名 | 核心能力 |
|--------|-------|---------|
| Developer | 墨码开发 | 软件开发、架构设计、代码审查 |
| Ops | 墨维运维 | 部署、监控、SRE、灾备 |
| Security | 墨安安全 | 代码审计、漏洞扫描、红队测试 |
| AutoDream | 墨梦AutoDream | AI自动化实验、记忆蒸馏、自学习 |

### VP 财务（1家）

| 子公司 | 中文名 | 核心能力 |
|--------|-------|---------|
| Finance | 墨算财务 | 记账、预算、成本控制、财务报表 |

### VP 战略（3家）

| 子公司 | 中文名 | 核心能力 |
|--------|-------|---------|
| BD | 墨商BD | 商务拓展、合作洽谈、销售策略 |
| Global Marketing | 墨海出海 | 多语言本地化、全球化运营 |
| Research | 墨研竞情 | 竞争分析、趋势扫描、实时情报 |

### 共享服务（3家）

| 子公司 | 中文名 | 核心能力 |
|--------|-------|---------|
| Legal | 墨律法务 | 合同审查、合规评估、风险评估 |
| Knowledge | 墨脑知识 | 知识图谱、向量记忆、RAG |
| Data Analyst | 墨测数据 | BI仪表盘、数据分析、质量检测 |

### 专项 Workers（3家）

| Worker | 领域 |
|--------|------|
| 墨投交易 | 量化交易策略、信号生成、回测 |
| Scrapling | 网页抓取、数据采集 |
| Router9 | 网络流量、多路路由 |

---

## 五、DARE v3.0 推理框架

Hermes CEO 的核心推理模型，每次任务分四步：

**D — 解构目标（Decompose）**
先定义「成功的样子」是什么，标准是什么，再动手。

**A — 分析缺口（Analyze）**
缺实时数据？缺用户洞察？缺法律确认？缺技术实现？按需调动对应子公司。

**R — 智能编排（Route）**
不是找「能做这件事的Worker」，而是找「最擅长这个环节的Worker」。研究优先于创作，能并行不串行。

**E — 超预期设计（Elevate）**
基础之上多走一步——文章+封面+备选标题+发布时间；竞品分析+差异化建议+快赢机会点；代码+测试+部署说明。

---

## 六、5 级治理体系

| 级别 | 名称 | 预算上限 | 说明 |
|------|------|---------|------|
| L0 | 自动执行 | ¥0 | 零成本操作，AI自动完成无需审批 |
| L1 | AI自审 | ≤ ¥10 | AI检查后自动执行 |
| L2 | 人工确认 | ≤ ¥100 | 需创始人确认后执行 |
| L3 | 董事会审批 | ≤ ¥1,000 | 重大决策需全面评估 |
| L4 | 绝对禁止 | — | 涉及真实现金/转账/支付/改价，绝不触碰 |

治理规则通过飞书审批卡片实现 L2/L3 门禁，审计日志 90 天保留，Token 30 天轮换。

---

## 七、每日自动化飞轮

系统每日自动运行的**内容生产管线**，三棒全自动接力：

| 时间 | 棒次 | 名称 | 任务 |
|------|------|------|------|
| 08:00 | 第一棒 | 情报银行 | 扫描RSS+GitHub+竞品→智能筛选高价值内容 |
| 09:20 | 第二棒 | 内容工厂 | 基于情报生成内容+SEO优化 |
| 10:45 | 第三棒 | 增长引擎 | SEO审计+分发追踪+策略调整 |

飞轮接力规则：
- 每棒检查上一棒产物是否存在（<90分钟）
- 断链自动飞书告警，防止空转
- 级联保护：第一棒失败→第二棒自动断链

此外还有 18 项辅助任务全天运行：
- 03:00 系统备份
- 07:30 API余额预警
- 09:00 CEO简报
- 09:45-17:45 闲鱼消息检测（每30分钟）
- 10:00 治理合规审计
- 12:00 系统健康检查
- 14:00 竞品监控
- 18:28 CEO下班汇总
- 周末: 记忆蒸馏 / 自学习 / 技能审计

---

## 八、记忆系统

四层记忆架构，确保知识不丢失、可复用：

| 层级 | 名称 | 存储位置 | 生命周期 |
|------|------|---------|---------|
| L1 | 工作记忆 | 飞书对话上下文 | 24h清理 |
| L2 | 情节记忆 | Supermemory（语义块） | 30天未调用→蒸馏 |
| L3 | 语义记忆 | Obsidian 产出/ | 永久 |
| L4 | 程序记忆 | SKILL.md 技能文件 | 版本化管理 |

检索方式：统一通过 molib/memory/retriever.py，双源检索（Obsidian + 向量记忆）。
输出规范：所有Agent通过 molib/memory/output_writer.py 强制结构化模板写入。

记忆存储位置：
- ~/.hermes/memory/chroma_db/ — 向量记忆
- ~/.hermes/memory/vector_memory.db — 结构化记忆
- ~/.hermes/dream/ — 记忆蒸馏产出
- ~/.hermes/memory/long_term/ — 长期记忆

---

## 九、CLI 命令系统

50+ 命令通过 `python -m molib` 统一入口：

**系统管理**: health, help, validate, sync
**内容创作**: content write/publish, design image/web
**视频制作**: video script
**商业运营**: crm segment/push, xianyu reply, order list/status
**财务管理**: finance record/report, cost
**情报研究**: intel trending/save
**量化交易**: trading signal/analyze/research
**数据分析**: data analyze
**元操作**: handoff route/list, plan create/decompose, memory, query, ghost-os, self-learning, karpathy scan, moneymaker assess

---

## 十、技术栈

| 层级 | 技术 |
|------|------|
| AI大脑 | Hermes Agent（Nous Research） |
| 推理框架 | DARE v3.0 |
| 执行引擎 | Python 3.11+ · Click · Rich |
| 配置管理 | TOML · YAML · dotenv |
| 记忆系统 | ChromaDB · SQLite · claude-mem |
| 通信通道 | 飞书Bot · CLI · FastAPI（:5050） |
| 视觉设计 | FLUX.2 · Open Design · FFmpeg |
| 数据存储 | JSONL审计日志 · 文件系统 |
| 自学习 | Self-Learning Loop · AutoDream |
| 版本控制 | Git · GitHub |

---

## 十一、环境要求

- 操作系统: macOS（M2 8GB 测试通过），Linux 兼容
- Python: 3.11+
- AI引擎: Hermes Agent（Nous Research）
- API Keys: DeepSeek / DashScope / OpenRouter（至少一个）
- 可选: FFmpeg（视频）· Docker（容器化）
- 磁盘: 约 2GB

---

## 十二、开源与社区

- 开源协议: MIT License
- 基于 Hermes Agent（Nous Research）构建
- 技能库吸收自开源社区（Excalidraw、Pixel Art、Open Design 等）
- GitHub 仓库: 由 Moye Tech 维护

---

## 十三、产品定位总结

墨麟 OS 不是给开发者用的框架，而是给**独立创业者**用的**AI集团操作系统**。

它的核心理念：
1. **一人即集团** — 一个人通过 AI 子公司矩阵完成原本需要 20 人团队的工作
2. **强制委托** — CEO 不做执行，只做决策和编排，质量由专业 Worker 保证
3. **持续积累** — 四层记忆 + Obsidian 知识库，每次执行都是知识复用
4. **自动飞轮** — 每天情报→内容→增长全自动运转，创始人只需关注策略
5. **安全可控** — 5 级治理 + 预算门禁 + 审计追踪，不会失控

适合人群：独立创业者、内容创作者、跨境电商卖家、知识付费运营者、一人公司创始人。

---

*本文档由墨麟OS共享服务层（玄骨）自动审查生成。*
