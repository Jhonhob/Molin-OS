---
title: AI Agent 框架深度研究
status: 迭代中 (Active)
last_updated: 2026-05-19
agent_sync: true
---

## TheAgency 仓库评估·0517

> 仓库：`msitarzewski/agency-agents` | Stars: 200+ | License: MIT
> 规模：140+ Agent 定义文件，19 个事业部，57KB README
> 评估日期：2026-05-17

---

## 一、总体判断

**🟢 高价值。可以直接吸收 18-22 个 Agent 定义作为墨麟子公司的技能补强。**

这是一个"AI Agent 人格库"——每个 Agent 是一份结构化的 Markdown 定义文件，包含：
- **身份定位**：Agent 的人设、专业领域、沟通风格
- **核心使命**：职责范围、目标
- **工作流程**：分步骤的操作清单（Phase/Step）
- **交付物规范**：输出格式、质量标准
- **成功指标**：可量化的验收标准

与墨麟OS的差异在于：它的 Agent 定义是**静态人格描述**（给 Claude Code 等工具读取），而墨麟的 SKILL.md 是**可执行流程 + 工具集成**。但"人格层"和"工作流层"完全可以互补——把 Agency 的领域专家人格嫁接到墨麟的 SOP 骨架和工具链上。

---

## 二、高优先级吸收清单（与墨麟20家子公司直接对标）

### 🔴 Tier 1 — 立刻吸收（直接填补能力空白，95%+ 匹配）

| # | Agency Agent | → 墨麟子公司 | 价值点 | 吸收方式 |
|---|---|---|---|---|
| 1 | **Private Domain Operator** (私域运营) | **墨域私域** | WeCom 架构、社群分层SOP、SCRM工具选型、流失预警自动化。309行，流程极详细 | 写为 `crm-private-domain` Skill |
| 2 | **Xiaohongshu Specialist** (小红书) | **银月传媒** | 品牌生活方式定位、微内容优化、算法投喂策略、UGC裂变。139行 | 合并入 `content-sop-pack` Skill |
| 3 | **Trend Researcher** (趋势研究) | **墨研竞情** | 弱信号检测、跨行业模式识别、Google Trends/SEMrush数据源、创新机会评分。159行 | 补强 `research-sop-pack` |
| 4 | **Reality Checker** (质量门控) | **门禁Agent** | "默认拒绝，需压倒性证据才放行"哲学。安全性/维护性/可测试性三维度审计。237行 | 补强 `gatekeeper-sop` |
| 5 | **Cross-Border E-Commerce** (跨境电商) | **梅凝出海** | Amazon/Shopee/Lazada运营、跨境物流、多国合规。虽404但目录存在，需确认 | 写为独立 Skill |
| 6 | **Douyin Strategist** (抖音) | **银月传媒** | 账号诊断→定位→内容矩阵→投流→数据复盘，完整五步。150行 | 合并入 `content-sop-pack` |
| 7 | **Bookkeeper & Controller** (财务) | **墨算财务** | 月末结账、科目对账、GAAP合规、RPA自动化。261行 | 补强 `finance-sop-pack` |
| 8 | **Agents Orchestrator** (Agent编排) | **墨梦AutoDream** | 多Agent编排管道、13个Phase的完整开发流程、任务状态追踪。367行 | 补强 `autodream-sop-pack` |

### 🟡 Tier 2 — 本周吸收（高匹配，增强现有能力）

| # | Agency Agent | → 墨麟子公司 | 价值点 |
|---|---|---|---|
| 9 | **Short-Video Editing Coach** | **墨播短视频** | 后期制作流程、平台规格适配、剪辑节奏控制 |
| 10 | **MCP Builder** | **墨码开发** | MCP Server 开发标准化、工具发现协议 |
| 11 | **China Market Localization** | **梅凝出海** | 全栈中国市场本地化：抖音/小红书/微信/百度全平台。284行 |
| 12 | **Content Creator** | **银月传媒 + 墨笔文创** | 多平台内容策略、编辑日历、AI辅助创作 |
| 13 | **Bilibili Content Strategist** | **银月传媒** | B站算法、弹幕文化、UP主增长 |
| 14 | **WeChat Official Account Manager** | **银月传媒** | 公众号运营、订阅用户增长 |
| 15 | **Zhihu Strategist** | **银月传媒** | 知乎思想领导力、知识驱动增长 |
| 16 | **Financial Analyst** | **墨算财务** | 财务建模、预测、情景分析 |
| 17 | **Legal Compliance Checker** | **墨律法务** | 合规检查、法规审查、合同风险评估 |
| 18 | **Security Engineer** | **墨安安全** | 威胁建模、安全代码审查、安全CI/CD |

### 🟢 Tier 3 — 择机吸收（有增强价值，非紧急）

| # | Agency Agent | → 墨麟子公司 | 价值点 |
|---|---|---|---|
| 19 | **Support Responder** | **墨声客服** | 客服话术、问题升级流程 |
| 20 | **API Tester** | **墨码开发** | API验证、集成测试 |
| 21 | **Code Reviewer** | **墨码开发** | 代码审查清单、安全扫描 |
| 22 | **Pipeline Analyst** | **墨链电商** | 销售漏斗分析、预测 |

---

## 三、不建议吸收的

| 类别 | 原因 |
|---|---|
| **工程部 18 个 Agent**（除 Code Reviewer/Security Engineer） | 墨麟不是软件公司，Frontend/Backend/Mobile/DevOps/Embedded 等多与当前业务无关 |
| **Design Division (8个)** | UI/UX 设计 Agent，墨麟无设计业务 |
| **Game Development** | 完全无关 |
| **Spatial Computing (6个)** | XR/Vision Pro 领域，无关 |
| **Academic (5个)** | 人类学/地理学/心理学等学术Agent，可择需用，不批量吸收 |
| **Paid Media (7个)** | PPC/程序化广告，银月可参考但不当前重点 |

---

## 四、吸收方法论

### 每吸收一个 Agency Agent → Molin-OS 的标准流程：

```
1. 读取 Agency 源文件（.md）
2. 提取三要素：Identity + Workflow + Deliverables
3. 与现有墨麟 SKILL.md 做 diff 对比
4. 补强缺失的流程步骤 / 质量标准 / 交付物模板
5. 将 Agency 的英文流程翻译为中文 SOP 步骤
6. 注入墨麟的工具链约束（vault路径、飞书推送、Supermemory双写）
7. 质量门控：gatekeeper-sop 检查后合并
```

### 文件格式转换：

| Agency 格式 | → 墨麟 SKILL.md 格式 |
|---|---|
| YAML frontmatter (name/description/color/emoji) | → SKILL.md YAML (name/description/category/version/tags) |
| `## Identity & Memory` | → `## Agent 身份` |
| `## Core Mission` | → `## 核心使命` |
| `### Phase 1/2/3` | → `## 执行流程` (Step 1/2/3) |
| `## Success Metrics` | → `success_criteria` (YAML) |
| 英文内容 | → 中文（保留关键英文术语） |

---

## 五、优先级路线图

### 本周 (5/18-5/24) — Tier 1 全量吸收（8个）

```
周一：Private Domain Operator → 墨域私域
周二：Xiaohongshu Specialist → 银月传媒
周三：Trend Researcher + Reality Checker → 墨研竞情 + 门禁
周四：Douyin Strategist + Cross-Border E-Commerce → 银月 + 梅凝
周五：Bookkeeper + Agents Orchestrator → 墨算财务 + 墨梦AutoDream
```

### 下周 (5/25-5/31) — Tier 2 全量吸收（10个）

### 6月 — Tier 3 择机（4个）

---

## 六、风险提示

1. **语言壁垒**：Agency Agent 均为英文定义，需翻译适配，但核心流程结构是语言无关的
2. **工具绑定**：部分 Agent 引用 Google Trends/SEMrush/Ahrefs 等海外工具，替换为国内等效工具（百度指数/新榜/5118）
3. **覆盖冗余**：Tier 1 的 8 个 Agent 中有 4 个指向银月传媒——注意避免 SOP 臃肿，采用"技能组合"而非"一个Agent一个Skill"
4. **风格冲突**：Agency 偏向"Claude Code 人格注入"范式，墨麟是"SOP + 工具链执行"范式。吸收时取流程和标准，弃人格描述

---

## 七、总结

**The Agency 是墨麟OS 2.0 以来遇到的最有价值的外部参考库。** 不是因为它的 Agent 有多强，而是因为它的 Agent 定义结构（Identity → Mission → Workflow → Deliverables → Success Metrics）恰好填补了墨麟部分子公司"有 SOP 骨架但缺领域深度"的空白。

核心价值不在代码，在**领域专家的人设定义和工作流清单**——这些是墨麟 Agent 当前最缺的"软实力"。

吸收策略：取流程、取标准、取交付物模板。弃人格、弃工具绑定、弃非相关领域。

建议从 **Private Domain Operator** 开始——它是所有 Agency Agent 中定义最完整、与墨麟缺口最大、实施路径最清晰的一个。

## TheAgency 吸收记录·0517

## 吸收概览

| 指标 | 数值 |
|------|------|
| 源仓库 | msitarzewski/agency-agents |
| 协议 | MIT |
| 首轮吸收 Agent 数 | 7 |
| 新建 Skill | 1 |
| 补强现有 Skill | 5 |

## 吸收清单

| # | 源 Agent | → 目标 | 操作 | 核心价值 |
|---|---------|-------|------|---------|
| 1 | Private Domain Operator | **墨域私域** | 🆕 新建 skill | WeCom架构+RFM分层+社群SOP+流失预警 |
| 2 | Xiaohongshu Specialist | **银月传媒** | 🔧 Patch content-sop-pack | 算法规则/内容组合/审美一致性 |
| 3 | Douyin Strategist | **银月传媒** | 🔧 Patch content-sop-pack | 前3秒钩子/算法优先级/直播电商 |
| 4 | Trend Researcher | **墨研竞情** | 🔧 Patch research-sop-pack | 弱信号检测/跨行业模式/机会评分 |
| 5 | Bookkeeper & Controller | **墨算财务** | 🔧 Patch finance-sop-pack | 月末结账流程/GAAP合规/对账方法论 |
| 6 | Agents Orchestrator | **墨梦AutoDream** | 🔧 Patch autodream-sop-pack | 13阶段编排管道/持续QA循环 |
| 7 | Reality Checker | **门禁Agent** | 🔧 Patch gatekeeper-sop | "默认拒绝"/证据驱动/评级标尺 |

## 吸收方法

每吸收一个外部 Agent → 墨麟 SKILL.md 的标准管线：
1. 读取 Agency 源文件（.md）
2. 提取三要素：Identity + Workflow + Deliverables
3. 与现有墨麟 SKILL.md 做 diff 对比，只补缺不覆盖
4. 将英文流程翻译为中文 SOP 步骤
5. 注入墨麟工具链约束（vault路径 `业务线｜内容.md`）
6. 质量门控：gatekeeper-sop 检查后合并

## 未吸收

| Agent | 原因 |
|-------|------|
| Cross-Border E-Commerce | 源文件 404（路径可能不同，需确认） |
| 工程部 18 个 Agent | 与墨麟业务无关 |
| 设计部 8 个 Agent | 墨麟无设计业务 |
| 其余 100+ Agent | 不在 Tier 1-3 范围内 |

## 验证

- ✅ vault_health_check.py 通过
- ✅ 所有新增/修改 Skill 可正常加载
- ✅ 所有路径符合 v3.0 平坦 vault 规范

## TheAgency 吸收记录·0518

> 吸收时间：2026-05-18  
> 仓库：`msitarzewski/agency-agents` (main, commit 783f6a7)  
> 仓库规模：226 个 Agent 定义文件，MIT License  
> 吸收方式：3 子 Agent 并行 patch/create

---

## 吸收总览

### Tier 1（5月17日完成，7个Agent）

| Agent | → Skill | 操作 |
|-------|---------|------|
| Private Domain Operator | `crm-private-domain` | 新建 |
| Xiaohongshu Specialist | `content-sop-pack` | patch |
| Douyin Strategist | `content-sop-pack` | patch |
| Trend Researcher | `research-sop-pack` | patch |
| Bookkeeper & Controller | `finance-sop-pack` | patch |
| Agents Orchestrator | `autodream-sop-pack` | patch |
| Reality Checker | `gatekeeper-sop` | patch |

### Tier 2（5月18日完成，13个Agent）

#### Batch 1: 营销/内容 (5 agents)

| Agent | 源文件大小 | → Skill | 新增章节 |
|-------|----------|---------|---------|
| Short-Video Editing Coach | 413行/30KB | `video-sop-pack` | 八、短视频剪辑专业技能 |
| Bilibili Content Strategist | 200行/11KB | `content-sop-pack` | 八、Bilibili Strategist |
| WeChat OA Manager | 146行/10KB | `content-sop-pack` | 九、微信公众号 Manager |
| Zhihu Strategist | 163行/12KB | `content-sop-pack` | 十、知乎 Strategist |
| Content Creator | 54行/3KB | `content-sop-pack` | 十一、Content Creator 通用策略 |

#### Batch 2: 工程/测试 (4 agents)

| Agent | 源文件大小 | → Skill | 新增章节 |
|-------|----------|---------|---------|
| Security Engineer | 305行/18KB | `security-sop-pack` | 六+七（应用安全工程+工作流） |
| API Tester | 306行/12KB | `developer-sop-pack` | 六、API 测试 SOP |
| Code Reviewer | 77行/3KB | `developer-sop-pack` | Step 5 扩展（审查清单） |
| MCP Builder | 248行/12KB | `native-mcp` | Building MCP Servers |

#### Batch 3: 分析/支持 (4 agents)

| Agent | 源文件大小 | → Skill | 新增章节 |
|-------|----------|---------|---------|
| Financial Analyst | 235行/13KB | `finance-sop-pack` | 九、财务分析（FP&A/建模/预测） |
| Legal Compliance Checker | 588行/26KB | `legal-sop-pack` | 八、多法域合规检查 |
| Support Responder | 585行/25KB | `service-sop-pack` | 七、分级客户支持体系 |
| Pipeline Analyst | 268行/19KB | `data-sop-pack` | 八、销售管道分析（MEDDPICC） |

---

## 技能变更汇总

| 技能 | 变更 | 新增行数（约） |
|------|------|--------------|
| `video-sop-pack` | +1 章 | +160 行 |
| `content-sop-pack` | +4 章 | +280 行 |
| `security-sop-pack` | +2 章节 | +160 行 |
| `developer-sop-pack` | +1 章 + 1 扩展 | +120 行 |
| `native-mcp` | +1 章 | +155 行 |
| `finance-sop-pack` | +1 章 | +120 行 |
| `legal-sop-pack` | +1 章 | +150 行 |
| `service-sop-pack` | +1 章 | +130 行 |
| `data-sop-pack` | +1 章 | +140 行 |

**合计**：9 个技能升级，13 章新增内容，~1,415 行专业领域知识注入。

---

## 设计决策

1. **中文命名一致性**：所有吸收内容使用墨麟OS 中文命名体系
2. **协同链路标注**：每章末尾标注与已有章节的协同关系
3. **SOP 四层架构保留**：遵循 Lead→Execution→QA→Escalation 框架
4. **MIT 许可证标注**：每个吸收章节首行注明来源和吸收日期
5. **content-sop-pack**：现覆盖中国主流内容平台全矩阵（小红书→抖音→B站→微信公众号→知乎）+ 通用策略层
6. **security-sop-pack**：原覆盖运维安全（密钥轮转/CVE扫描），现补充工程安全（威胁建模/代码审查/架构设计）
7. **mcp-builder**：评估不适合 autodream-sop-pack（实验/原型领域），吸收进 native-mcp（MCP 领域），形成完整 MCP 知识体系

---

## 仓库全景

The Agency 仓库现规模 226 个 Agent 定义。Tier 1+2 共吸收 20 个 Agent（约 9%），覆盖：

- 内容营销：小红书/抖音/B站/微信公众号/知乎 + 短视频剪辑 + 通用创作
- 私域运营：企业微信/RFM 分层/社群 SOP
- 财务：记账/月末结账/GAAP 合规 + FP&A/财务建模
- 研发工程：API测试/代码审查/安全工程/MCP 构建
- 法务合规：多法域合规检查
- 客户支持：分级支持/全渠道/知识库
- 数据分析：销售管道/MEDDPICC/预测
- 治理：现实检查/证据驱动门控
- 编排：13 阶段 Agent 编排管道

---

## 后续可选

- **Tier 3**（低优先级）：管道分析师(已吸收)、客服(已吸收)、API测试(已吸收)、代码审查(已吸收)
- **其他高价值 Agent**：Product Manager(产品)、Growth Hacker(增长)、SEO Specialist(搜索)、Paid Media Strategist(投放) 等

## 多Agent教育吸收·0517

================================================================================
2026-05-16 GitHub教育项目研究 · 多Agent教育+知识图谱+评估系统
================================================================================

一、核心趋势总结

A) 多Agent教育架构兴起 — 多个AI Agent分工协作（诊断师/讲师/教练）替代单一ChatBot。
代表项目：SimonsTang/feifei-companion (104★)、bcefghj/multi-agent-education (41★)
核心洞察：角色分工（总管+文科+理科/Mesh架构5-Agent）让教学质量显著提升。
启发：墨麟可设计逻辑诊断师→讲解师→教练的三Agent分工

B) 费曼学习法AI结构化落地 — 从学生提问→AI回答，转型为学生主动讲解→AI评估。
代表项目：ophiraShen/EasyDS (31★)
核心洞察：三层Agent（路由+学生+教师）实现讲解→评估→强化闭环。
启发：逻辑思维训练可强制学生先说出推理过程，AI再通过追问暴露漏洞

C) 经典算法+LLM混合架构 — BKT知识追踪+SM-2间隔重复+苏格拉底式Prompt组合。
代表项目：bcefghj/multi-agent-education (41★)
核心洞察：纯LLM不够，需要BKT概率模型跟踪掌握度+SM-2动态排期。
启发：墨麟核心差异点应放在"经典教育算法+LLM Agent"组合

D) Copilot SDK教育落地 — 通过GitHub Copilot SDK构建自适应编程练习平台。
代表项目：chrisreddington/flight-school (28★)
核心洞察：技能画像→缺口分析→个性化内容管道，Growth Mindset评估哲学（永不"错误"）。
启发：墨麟可复用在编程逻辑训练领域，构建"学员代码画像→针对性训练"

E) 教育知识图谱构建成熟 — 从Neo4j图数据库到TextCNN意图识别+Cypher查询的完整链路。
代表项目：jiangnanboy/education_knowledge_graph_app (136★)、Goooaaal/ourvision-人工智能教育知识图谱 (65★)
核心洞察：题目-知识点绑定+3段式查询（意图分类→实体抽取→图查询）。
启发：墨麟可构建逻辑知识图谱，错题自动定位薄弱逻辑点

F) 间隔重复生态成熟 — Anki (28k★)生态系统向MCP方向演进。
代表项目：ankimcp/anki-mcp-server (277★)、open-spaced-repetition/py-fsrs (427★)
核心洞察：FSRS算法优于经典SM-2，MCP让AI直接管理闪卡。
启发：墨麟复习系统可直接集成py-fsrs计算最优复习间隔

二、可直接借鉴的设计模式

1. 三Agent教学分工（feifei-companion/EasyDS）：路由Agent做意图分配→教学Agent做内容讲解→评估Agent做反馈。落地：墨麟每一道逻辑题拆为"诊断→教学→训练→评估"四步，每步由独立Agent执行

2. Mesh+事件驱动架构（multi-agent-education）：Agent间通过EventBus异步通信，而非传统Supervisor集中调度。落地：墨麟多个教学Agent可独立运行，通过事件总线交换学员状态

3. BKT+SM-2教育算法组合（multi-agent-education）：BKT实时更新知识点掌握概率，SM-2动态计算复习间隔。落地：墨麟每一逻辑知识点绑定BKT状态，自动调整训练频次

4. Growth Mindset评估框架（flight-school）：永不说"错误/错误"，用"not yet"框架+先肯定优点再提示改进。落地：墨麟代码评审/逻辑题评估统一采用建设性反馈模板

5. 技能画像→缺口分析→个性化内容管道（flight-school）：从用户数据提取技能画像，AI自动分析缺口并生成针对性内容。落地：墨麟根据学员测试数据自动生成每日逻辑训练

6. 知识点前置依赖图谱（feifei-companion/education_knowledge_graph_app）：每一逻辑知识点标注前置能力要求，AI自动回溯前置短板。落地：学员在某类推理题卡住时，Agent自动定位并推荐修复前置逻辑能力

7. 费曼教学法Agent化（EasyDS）：强迫学生先"教"（讲解执行），AI再"评"（评估反馈）。落地：墨麟逻辑思维课设计"你先说怎么推理"环节，比"直接答题"效果好

8. 基于Copilot SDK的自适应编程教育（flight-school）：MCP集成让AI能读取用户实际仓库做个性化指导。落地：墨麟AI可接入学员的代码仓库/练习记录做真正个性化教学

三、今日值得关注项目清单

• SimonsTang/feifei-companion (104★)：三位一体K12智能教育陪伴系统，Multi-Agent+五大学习法+HERMES反思引擎。推荐理由：最完整的开源Multi-Agent教育实践，架构思想直接复用

• jiangnanboy/education_knowledge_graph_app (136★)：K12教育知识图谱全链路（Neo4j+TextCNN+Django）。推荐理由：知识图谱功能原型参考，题目-知识点追踪机制成熟

• bcefghj/multi-agent-education (41★)：5-Agent Mesh架构+BKT+SM-2教育系统。推荐理由：经典算法+LLM教育Agent的最佳参考，三语言实现

• ophiraShen/EasyDS (31★)：费曼学习法AI化（LangGraph+DeepSeek+RAG）。推荐理由：方法论创新，三层Agent实现讲解→评估→强化闭环

• chrisreddington/flight-school (28★)：Copilot SDK驱动的自适应编程练习平台。推荐理由：Copilot SDK落地范本+技能画像管道+Growth Mindset评估

• Goooaaal/ourvision-Artificial-intelligence-education-knowledge-graph (65★)：AI教育领域知识图谱（5000+实体）。推荐理由：百科数据源构建策略+KNN自动分类，适合初始图谱快速创建

## Agent 交互原型设计

1|# 墨麟三Agent · 交互界面原型设计
     2|
     3|━━━━━━━━━━━━━━━━━━
     4|
     5|## Agent一：逻辑诊断Agent — 教师端实时看板
     6|
     7|> 嵌入环节：课堂学习、课后测评
     8|> 使用角色：授课老师、辅导老师、家长（只读版）
     9|
    10|━━━━━━━━━━━━━━━━━━
    11|
    12|### 界面1：课堂实时热力图
    13|
    14|位置：教师直播课助手的侧边栏
    15|
    16|├─ 全班智能评估（顶部）
    17|│  ├─ 当前专注度：92%（15人正常/1人走神）    🟢
    18|│  ├─ 当前卡壳率：8%（2人在同一题卡住）
    19|│  └─ 当前回答正确率：78%
    20|│
    21|├─ 薄弱知识点预警
    22|│  ├─ ⚠️ 分类思维 → 3人薄弱（建议重点讲P22页）
    23|│  └─ ⚠️ 有序思维 → 2人薄弱
    24|│
    25|├─ 实时学员操作面板
    26|│  ├─ 学员A   🟢 已通过  | 用时2m30s | 正确率100%
    27|│  ├─ 学员B   🟡 答题中  | 当前题:分类-03  | 用时1m45s
    28|│  ├─ 学员C   🔴 卡壳中  | 卡在:分类-02  | 建议:老师关注
    29|│  └─ 学员D   ⚪ 未作答  | 可能掉线
    30|
    31|老师可见价值：一眼看清全班谁掌握、谁卡壳、哪个知识点要重点讲。
    32|替代当前"老师凭感觉判断"的模式。
    33|
    34|━━━━━━━━━━━━━━━━━━
    35|
    36|### 界面2：课后薄弱点标注报告
    37|
    38|位置：课次报告（推送给家长）
    39|
    40|你孩子的逻辑能力诊断报告
    41|
    42|本期课程：L1-分类启蒙          上课日期：5月18日
    43|
    44|能力总览
    45|  分析思维    ⬛⬛⬛⬛⬜⬜  60%
    46|  整合思维    ⬛⬛⬛⬛⬛⬜  83%
    47|  创造性思维  ⬛⬛⬛⬜⬜⬜  50%
    48|
    49|本次发现的薄弱点
    50|  ① 分类思维（优先级：高）
    51|     表现：能按颜色分类，但多维度分类时遗漏
    52|     建议：课后教练Agent已推送3道针对性练习
    53|  ② 有序思维（优先级：中）
    54|     表现：排序基本正确，但正向→反向转换时出错
    55|     建议：下节课专题复习会再次涉及
    56|
    57|与上节课对比
    58|  准确率：72% → 78%（+6%）
    59|  完成速度：4m20s → 3m50s（-12%）
    60|  薄弱点：从上节的"对应思维"转移到"分类思维"
    61|
    62|建议：本周末让学员完成教练Agent的3道追击训练。
    63|
    64|━━━━━━━━━━━━━━━━━━
    65|
    66|## Agent二：逻辑教练Agent — 课后陪练对话
    67|
    68|> 嵌入环节：课后练习、答疑
    69|> 使用角色：学员（直接对话）、辅导老师（跟进）
    70|
    71|━━━━━━━━━━━━━━━━━━
    72|
    73|### 界面：苏格拉底式追问对话
    74|
    75|学员在做完"分类"课后练习后，教练Agent启动：
    76|
    77|━━━━━━━━━━━━━━━━━━
    78|教练Agent：
    79|  "好的，这道题你做对了！但我想知道你是怎么想的。
    80|  你可以先给老师讲一遍你的推理过程吗？"
    81|
    82|学员：（语音或打字输入推理过程）
    83|
    84|教练Agent（识别推理链中的断裂点）：
    85|  "你刚才说'因为颜色不同所以分类'——这步是对的。
    86|  但接下来你说'所有红色放一起'的时候，
    87|  有没有注意到红色的东西有两类：水果和文具？
    88|  如果只按颜色分，你漏掉了什么？"
    89|
    90|学员：（重新思考后回答）
    91|
    92|教练Agent：
    93|  "对！你发现了！同一个红色里面还有水果和文具的区别。
    94|  这就是双重分类——既要看颜色，又要看种类。
    95|  试试这道新的题看能不能用双重分类的方法？"
    96|━━━━━━━━━━━━━━━━━━
    97|
    98|### 界面变量
    99|
   100|情况                     教练Agent话术模板        追问深度
   101|第一次正确（新知识点）     先肯定→请讲解推理过程     浅（确认理解）
   102|第二次正确（练习阶段）     快速通过                 无追问
   103|第一次错误                 不给答案→三追问引导       中
   104|第二次错误（同一知识点）   换场景换例子再问           深→最终给出提示
   105|
   106|━━━━━━━━━━━━━━━━━━
   107|
   108|## Agent三：可视化Agent — 家长成长报告
   109|
   110|> 嵌入环节：月度测评、学期竞技
   111|> 使用角色：家长（微信/飞书推送）
   112|
   113|━━━━━━━━━━━━━━━━━━
   114|
   115|### 界面1：每周能力增长曲线
   116|
   117|以周为单位的折线图，展示学员在以下维度的变化：
   118|
   119|        分  100│        ⭐
   120|        析  80 │    ⭐⭐⭐
   121|        思  60 │
   122|        维  40 │
   123|              └────────────────
   124|               W1  W2  W3  W4  W5
   125|
   126|同页面展示对比信息：
   127|  相比同Level学员：高于平均12%
   128|  相比上周：增长+6%
   129|  预测：按此趋势，2周后可进入综合复习阶段
   130|
   131|━━━━━━━━━━━━━━━━━━
   132|
   133|### 界面2：20种思维方法雷达图
   134|
   135|每学期末生成的雷达图，展示学员在三大思维领域的分布：
   136|
   137|        分类思维
   138|           ⬤
   139|       有序╱ ╲对应
   140|       思维╱   ╲思维
   141|         │  ⬤  │
   142|       分步╲   ╱模型化
   143|       思维 ╲ ╱ 思维
   144|           ⬤
   145|        转化思维
   146|
   147|右侧标注：
   148|  优势：分类思维（掌握度92%）、对应思维（88%）
   149|  待加强：有序思维（55%）、模型化思维（60%）
   150|  对比上期：分类思维+8%，有序思维-3%
   151|
   152|━━━━━━━━━━━━━━━━━━
   153|
   154|### 界面3：成长动画（适合发朋友圈/社群）
   155|
   156|形式：15秒动画GIF/短视频
   157|
   158|帧1: "小明在L1课程开始时..."
   159|    显示能力值基线
   160|帧2: "...2个月后，分类思维的掌握度从45%→78%"
   161|    折线上升动画
   162|帧3: "...最棒的是，他学会了'先想再回答'"
   163|    显示一句话亮点
   164|帧4: "继续加油！🎉"
   165|    火花Logo + 课程名称
   166|
   167|使用场景：转介绍裂变、小老师视频替代品、
   168|        家长主动在朋友圈晒娃的"学习成果凭证"
   169|
   170|━━━━━━━━━━━━━━━━━━
   171|
   172|## 原型优先级排序
   173|
   174|功能                    优先级  开发量评估  对豌豆差异化价值
   175|教师端课堂热力图         P0     中（需埋点） ⭐⭐⭐⭐⭐（竞品没有）
   176|课后薄弱点标注报告       P0     低（已有数据）⭐⭐⭐⭐（现有课次报告升级）
   177|教练Agent追问对话        P1     中（LLM调用）  ⭐⭐⭐⭐（豌豆无主动陪练）
   178|能力增长曲线             P1     低            ⭐⭐⭐（家长感知提升）
   179|20种思维方法雷达图       P2     低            ⭐⭐⭐（独特维度）
   180|成长动画（朋友圈素材）   P2     中            ⭐⭐⭐⭐（转介绍催化剂）
   181|
   182|建议P0项2周内出可演示版本，P1项1个月内上线，P2项作为Q3储备。
   183|

## 技术选型评估

1|# 墨麟AI增强型思维小班课 · 技术评估与埋点接入方案
     2|
     3|> 状态：待工程团队评审
     4|> 评估对象：火花思维现有课件/直播系统
     5|
     6|━━━━━━━━━━━━━━━━━━
     7|
     8|## 一、三Agent需要的数据源
     9|
    10|现有知识图谱已覆盖L1-L9共9个级别、20种思维方法、prerequisites依赖关系。
    11|三Agent需要的数据接入点如下：
    12|
    13|### 1.1 逻辑诊断Agent 所需数据
    14|
    15|采集类型              采集时机                当前是否支持?     备注
    16|学员操作路径          课中（课件点击/拖拽     待确认            核心数据，决定Agent能否启动
    17|（点击序列、拖拽      /作答/跳转）
    18|方向、答题用时）
    19|
    20|单选题/多选题结果     课中+课后               ✅ 已有            题系统应已记录
    21|（对/错/超时）
    22|
    23|拖动排序/连线类       课中互动环节            待确认            须支持操作轨迹回放
    24|操作轨迹
    25|
    26|学员与AI对话/         课后（教练Agent         ❌ 新建            教练Agent上线后产生
    27|追问记录              +学员互动）
    28|
    29|### 1.2 逻辑教练Agent 所需数据
    30|
    31|数据类型              说明                     来源
    32|知识点掌握概率        BKT算法输出             诊断Agent计算结果
    33|错题类型分布          按20种思维方法归类       现有课程系统+诊断Agent
    34|学员当前Level和班型   L1-L9 + 基础/提高/拔高  已有
    35|最优复习间隔          按FSRS算法计算          教练Agent
    36|
    37|### 1.3 可视化Agent 所需数据
    38|
    39|数据维度              数据量                输出格式
    40|学员能力增长曲线      每周更新              折线图（PNG）
    41|20种思维方法雷达图    每次测评后更新          雷达图（SVG）
    42|推理断裂点热力图      每节课后更新            热力图
    43|学期前后对比          每学期末更新            对比动画
    44|
    45|━━━━━━━━━━━━━━━━━━
    46|
    47|## 二、现有系统接入点分析
    48|
    49|### 2.1 知识图谱（已就绪 ✅）
    50|
    51|路径：edu/curriculum/knowledge_graph.json
    52|内容：L1-L9完整章节、20种思维方法分组、prerequisites前置依赖映射
    53|可用性：诊断Agent可直接引用，无需改造
    54|
    55|### 2.2 学员生命周期管理（已就绪 ✅）
    56|
    57|路径：edu/scripts/spark_pipeline.py
    58|内容：6阶段生命周期（线索/试听/活跃/卡壳/流失）+ 3级干预机制
    59|可用性：诊断+教练Agent的干预策略可直接挂载
    60|
    61|### 2.3 学员记忆系统（已就绪 ✅）
    62|
    63|路径：edu/students/<student_id>.json
    64|内容：结构化画像（认知阶段/知识域/SRS阶段/连胜次数）
    65|可用性：教练Agent的个性化推荐依赖此系统
    66|
    67|### 2.4 10大学习闭环（需要确认 ❓）
    68|
    69|环节                      Agent嵌入点
    70|课前预习                  教练Agent发交互式热身
    71|课堂学习                  诊断Agent实时分析（需埋点支持）
    72|课后练习                  教练Agent苏格拉底追问
    73|课后答疑                  教练Agent引导
    74|专题复习                  教练Agent+FSRS排期
    75|专题测评                  诊断Agent出薄弱点报告
    76|专项突破+学期竞技         可视化Agent生成成长报告
    77|
    78|### 2.5 埋点缺失风险
    79|
    80|如果当前课件系统没有细粒度的操作轨迹埋点，
    81|诊断Agent的"实时分析"能力将大幅受限。
    82|备选方案：先退回到"课后分析模式"——
    83|学员做完题后，诊断Agent基于答题结果做BKT概率推断，
    84|而不是基于实时的操作路径热力图。
    85|
    86|同豌豆思维相比：它们的AI也是基于课后数据做推送，
    87|没能做到实时操作轨迹追踪。所以如果能做到实时追踪，
    88|就是真正的差异化壁垒。
    89|
    90|━━━━━━━━━━━━━━━━━━
    91|
    92|## 三、技术栈建议
    93|
    94|### Phase 1（诊断Agent）
    95|
    96|组件            建议技术          理由
    97|学员操作埋点     课件前端           如果做实时追踪须前端发event
    98|                event tracking     如果做课后分析则只需现有答题数据
    99|
   100|BKT引擎          Python +          20种思维方法×9个Level=180个知识点
   101|                pymc/bambi         BKT规模可控
   102|
   103|知识图谱查询     json +            现有图谱已在本地JSON中
   104|                in-memory          启动时加载即可
   105|
   106|数据存储         追加JSON          学员记忆系统已有模式，
   107|                文件                7小时内同类合并/7小时外新文件
   108|
   109|### Phase 2（教练Agent）
   110|
   111|组件            建议技术          理由
   112|苏格拉底追问     LLM Prompt        基于deepseek-v4-flash或同级别模型
   113|引擎            工程（自有）
   114|
   115|FSRS排期        py-fsrs           开源、成熟、优于经典SM-2
   116|                (FSRS v5)
   117|
   118|对话存储         追加JSON          复用学员记忆系统
   119|
   120|### Phase 3（可视化Agent）
   121|
   122|组件            建议技术          理由
   123|图表生成         matplotlib +     轻度使用，不支持canvas时
   124|                pillow            转PNG
   125|
   126|动画生成         pillow + gif      学期对比动画，拍帧合成
   127|
   128|学习报告分发     飞书Bot/微信       推送给家长
   129|
   130|━━━━━━━━━━━━━━━━━━
   131|
   132|## 四、技术评估结论
   133|
   134|### ✅ 不需要工程团队改动的部分
   135|- 知识图谱已完整（L1-L9，20种思维方法，prerequisites）
   136|- 学员生命周期管理模型已就绪
   137|- 学员记忆/画像数据模式已定义
   138|- 竞品对比定位矩阵已搭建
   139|
   140|### ❓ 需要确认的埋点问题
   141|1. 课件前端是否有操作轨迹埋点？
   142|2. 答题结果是否能导出到外部系统？
   143|3. 课后练习是否有API可接入？
   144|
   145|### ❌ 需要新建的部分
   146|- 教练Agent的追问引擎（LLM Prompt工程）
   147|- FSRS排期模块（Python包安装即可）
   148|- 可视化Agent图表生成模块
   149|- 诊断→教练→可视化的三Agent编排调度层
   150|
   151|━━━━━━━━━━━━━━━━━━
   152|
   153|建议工程团队下周先用半小时回答三个确认问题（操作轨迹/答题导出/课后API），
   154|确认后我出Phase 1详细的技术选型决策文档。
   155|

## 修订日志 (Changelog)

- **2026-05-19**: 从 TheAgency 评估 + 吸收记录 + 多Agent教育 + 交互原型 + 技术选型合并
