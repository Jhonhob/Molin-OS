---
created: 2026-05-18
updated: 2026-05-18
agent: system
category: 成果
status: 完成
confidence: 已验证
importance: ⭐⭐⭐
source: The Agency仓库 Tier 2 批量吸收
tags: [TheAgency, 吸收, Tier2, 技能补丁, SOP]
---

# The Agency 仓库 Tier 2 吸收记录

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
