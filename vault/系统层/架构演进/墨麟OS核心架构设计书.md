---
title: 墨麟OS核心架构设计书
status: 活跃
last_updated: 2026-05-19
agent_sync: true
frameworks_applied:
  - 金字塔原理
  - MECE
  - DIKW
---

墨麟OS是一套AI原生一人公司操作系统，让一个人用一台MacBook即可驱动覆盖营销、运营、技术、财务、战略五大领域的20家虚拟子公司。创始人通过飞书或CLI下达指令，Hermes Agent进行智能决策和任务编排。

---

## 一、系统架构

大脑层(Hermes Agent) → 执行层(molib Package, 447模块, 89,713行Python) → 技能层(362项技能)

三层流水线：Hermes Agent基于DARE推理框架(Decompose/Analyze/Route/Elevate)做决策编排，molib作为执行引擎驱动20家子公司Worker，技能层提供从SEO到量化交易的全域能力。

系统月收入目标52,000元，运行于M2 MacBook 8GB内存环境。

## 二、五级治理体系

| 级别 | 名称 | 预算上限 | 说明 |
|------|------|---------|------|
| L0 | 自动执行 | 0元 | 零成本操作，AI自动完成无需审批 |
| L1 | AI自审 | ≤10元 | AI检查后自动执行 |
| L2 | 人工确认 | ≤100元 | 需创始人确认后执行 |
| L3 | 董事会审批 | ≤1,000元 | 重大决策需全面评估 |
| L4 | 绝对禁止 | — | 涉真实现金/转账/支付/改价，绝不触碰 |

治理规则通过飞书审批卡片实现L2/L3门禁，审计日志90天保留，Token 30天轮换。

## 三、DARE推理框架

每次任务分四步：解构目标(Decompose)——先定义成功标准再动手。分析缺口(Analyze)——缺数据、缺洞察、缺法律确认、缺技术实现，按需调动对应子公司。智能编排(Route)——不是找能做这件事的Worker，而是找最擅长这个环节的Worker。超预期设计(Elevate)——基础之上多走一步，文章+封面+备选标题+发布时间，竞品分析+差异化建议+快赢机会点。

## 四、20家子公司体系

VP营销5家：墨笔文创(品牌文案/小红书/公众号/SEO)、墨韵IP(IP孵化/版权管理)、墨图设计(FLUX.2生图/封面/UI)、墨播短视频(脚本/生成/视频引擎)、墨声配音(AI语音合成/播客/TTS)。

VP运营4家：墨域私域(用户分层/社群运营/RFM)、墨声客服(自动化客服/消息检测)、墨链电商(订单管理/交易链路)、墨学教育(课程设计/AI导师/学习路径)。

VP技术4家：墨码开发(软件开发/架构设计/代码审查)、墨维运维(部署/监控/SRE)、墨安安全(代码审计/漏洞扫描/红队)、墨梦AutoDream(AI自动化实验/记忆蒸馏/自学习)。

VP财务1家：墨算财务(记账/预算/成本控制/财务报表)。

VP战略3家：墨商BD(商务拓展/合作洽谈)、墨海出海(多语言本地化/全球化运营)、墨研竞情(竞争分析/趋势扫描)。

共享服务3家：墨律法务(合同审查/合规评估)、墨脑知识(知识图谱/向量记忆/RAG)、墨测数据(BI仪表盘/数据分析)。

专项Worker3家：墨投交易(量化交易策略)、Scrapling(网页抓取)、Router9(网络流量)。

## 五、每日自动化飞轮

08:00情报银行——扫描RSS/GitHub/竞品，智能筛选高价值内容。09:20内容工厂——基于情报生成内容+SEO优化。10:45增长引擎——SEO审计+分发追踪+策略调整。

飞轮接力规则：每棒检查上一棒产物是否存在，断链自动飞书告警，级联保护防止空转。

此外18项辅助任务全天运行：03:00系统备份、07:30API余额预警、09:00CEO简报、09:45~17:45闲鱼消息检测(每30分钟)、10:00治理合规审计、12:00系统健康检查、14:00竞品监控、18:28CEO下班汇总、周末记忆蒸馏/自学习/技能审计。

## 六、记忆系统

四层记忆架构：L1工作记忆(飞书对话上下文，24h清理)、L2情节记忆(Supermemory语义块，30天未调用蒸馏)、L3语义记忆(Obsidian，永久)、L4程序记忆(SKILL.md技能文件，版本化管理)。

检索统一通过molib/memory/retriever.py，双源检索(Obsidian+向量记忆)。输出通过molib/memory/output_writer.py强制结构化模板写入。

## 七、CLI命令系统

50+命令通过python -m molib统一入口：系统管理(health/help/validate/sync)、内容创作(content write/publish/design)、视频制作(video script)、商业运营(crm segment/push/xianyu reply/order)、财务管理(finance record/report/cost)、情报研究(intel trending/save)、量化交易(trading signal/analyze/research)、数据分析(data analyze)、元操作(handoff route/list/plan create/decompose/memory/query/ghost-os/self-learning/karpathy scan/moneymaker assess)。

## 八、技术栈

AI大脑Hermes Agent(Nous Research)，推理框架DARE，执行引擎Python 3.11+/Click/Rich，配置管理TOML/YAML/dotenv，记忆系统ChromaDB/SQLite/claude-mem，通信通道飞书Bot/CLI/FastAPI(:5050)，视觉设计FLUX.2/Open Design/FFmpeg，数据存储JSONL审计日志/文件系统，自学习Self-Learning Loop/AutoDream，版本控制Git/GitHub。
