---
name: agent-sop-template
description: Agent SOP 四层架构标准化模板 — 将每个 Agent 从"能执行任务"升级为"能经营业务"
category: molin-org
version: 1.0.0
tags: [sop, template, architecture, agent-standard, blueprint]
trigger: 创建新 Agent 或升级现有 Agent 为 SOP 规范时使用
---

# Agent SOP 标准化模板

## 概述

每个 Molin-OS Agent 必须统一拥有四层结构：

```
Agent
 ├── SOP Layer    —— 标准作业程序（做什么、怎么做、什么标准）
 ├── Cron Layer   —— 自动循环周期（何时做、做多快、什么节奏）
 ├── KPI Layer    —— 结果监控指标（做多好、成本收益、ROI）
 └── Feedback Layer —— 反思优化闭环（怎么改进、怎么增长）
```

这是将 Agent 从"高级 Prompt"升级为"可持续经营的 AI 业务部门"的核心框架。

---

## 第一层：SOP 六件套

每个 Agent 根据业务场景，从以下六个 SOP 中选择必须实现的子集。

### ① Lead SOP（线索获取）
**解决：Agent 的"输入"从哪里来？**

模板结构：
```yaml
sources:          # 数据源列表（web_search / API / Obsidian / 用户输入）
filter_rules:     # 信息筛选规则
priority:         # 优先级排序逻辑
competitor_tracking: # 竞争情报配置
intent_recognition:  # 用户意图识别
hotspot_judgment:    # 热点判断标准
```

**输出格式约定：** 线索数据统一写入 `relay/{agent_name}_lead.json`

### ② Execution SOP（执行流程）
**解决：Agent 如何稳定产出结果？**

模板结构：
```yaml
input_format:     # 输入格式要求
steps:            # 推理步骤（编号列表）
  - step 1: ...
  - step 2: ...
  - ...
style_rules:      # 风格规则
output_template:  # 输出模板
quality_threshold: # 质量阈值（0-100）
failover:         # 失败时的 Fallback 策略
```

**铁律：** 每个 Execution SOP 必须包含 自检步骤（self-check）作为倒数第二步。

### ③ QA SOP（质检流程）
**解决：输出质量如何保证？**

评分维度：
| 维度 | 权重 | 检查项 |
|------|------|--------|
| 品牌一致性 | 20% | 是否符合品牌调性 |
| 合规风险 | 20% | 是否违规/敏感 |
| 转化能力 | 15% | CTA是否明确 |
| 数据真实性 | 15% | 是否幻觉 |
| SEO结构 | 10% | 是否可索引 |
| 平台适配 | 10% | 是否符合平台推荐机制 |
| 原创性 | 10% | 是否足够差异化 |

**阈值规则：**
- 总分 ≥ 80：直接输出
- 60 ≤ 总分 < 80：自动修正后输出
- 总分 < 60：打入 `relay/{agent}_qa_failed/`，触发 Escalation SOP

### ④ Escalation SOP（升级流程）
**解决：什么情况必须通知 Founder / 触发人工干预？**

模板：
| 场景 | 触发条件 | 动作 | 治理级别 |
|------|----------|------|----------|
| 示例：成本异常 | Token消耗 > 阈值200% | 降级模型 + 飞书告警 | L1 notify |
| 示例：质量不达标 | QA评分连续3次 < 60 | 暂停任务 + 飞书告警 | L2 approve |
| 示例：合规风险 | 检测到敏感内容 | 自动撤回 + 人工审核 | L2 approve |

治理级别参考 `config/governance.yaml`（L0 自动 / L1 通知 / L2 审批 / L3 董事会 / L4 禁止）

### ⑤ Growth SOP（增长流程）
**解决：如何持续提高 ROI？**

核心回路：
```
采集数据 → 分析瓶颈 → 生成假设 → AB测试 → 应用优化 → 验证效果
```

每个 Agent 每 7 天必须回答：
1. 我的核心 KPI 是什么？本周趋势如何？
2. 最大的优化空间在哪里？
3. 可以做什么 AB 测试来验证？

### ⑥ Crisis SOP（危机处理）
**解决：外部依赖挂了怎么办？**

| 风险场景 | 处理机制 | 恢复策略 |
|----------|----------|----------|
| API 不可用 | 切换备选模型/Provider | 恢复后自动切回 |
| 平台封号 | 自动切换账号/IP | 人工介入 |
| Token 成本失控 | 降级到低成本模型 | 每日成本复核后恢复 |
| Webhook 失效 | 降级到邮件通知 | 恢复后自动切回 |
| 内容违规 | 自动撤回 + 人工审查 | 审查通过后恢复 |

---

## 第二层：Cron Layer

> 实操指南：`references/cron-sop-pattern.md` — 如何创建加载 SOP 技能的 Cron 任务、数据回环实现、已部署的 Cron-SOP 集成实例。

### 周期性经营节奏

每个 Agent 根据业务节奏定义自己的 Cron 周期：

| 节奏 | 典型时间 | 用途 |
|------|----------|------|
| 高频 | 每15-60分钟 | 监控、轮询、阈值检查 |
| 日常 | 每天固定时间 | 情报采集、内容生产、复盘 |
| 周度 | 每周固定时间 | 增长实验、KPI复盘、战略调整 |
| 月度 | 每月固定时间 | 经营报告、预算评估、系统优化 |

### Cron 数据回环

所有 Cron 执行必须包含数据回环，不能只输出不采集：

```
执行 → 输出到 Obsidian/relay → 采集表现数据 → 反馈给下一轮
```

Cron 失败必须自动记入 Escalation SOP。

---

## 第三层：KPI Layer

每个 Agent 必须定义以下三类 KPI：

### 效能类（效率）
- 任务完成率（%）
- 平均响应/执行时间
- Token 消耗/任务

### 质量类（质量）
- QA 评分均值
- 错误率
- 返工率（QA < 60 的比例）

### 业务类（价值）
- ROI（产出价值 / 成本）
- 转化率（如果涉及）
- 留存/复购率（如果涉及）

---

## 第四层：Feedback Layer

### 每日复盘（22:00 自动执行）

模板：
```markdown
## [Agent名称] 每日复盘 YYYY-MM-DD

### 执行概况
- 任务数：N
- 成功率：N%
- 平均QA评分：N

### 异常记录
- [异常1]：原因分析
- [异常2]：改进措施

### 明日优化
1. ...
2. ...
```

### 每周经营报告（周日 21:00 自动执行）

内容：
1. 本周 KPI 趋势（上升/下降/持平）
2. TOP3 异常事件及根因
3. 增长实验结论
4. 下周优化计划

---

## 架构模式 v2.0：主脑文档模式

**2026-05-17 架构升级** — 从多文件 SOP → 单一主脑文档。

核心认知转变：**SOP ≠ 文件，SOP = 一个持续更新的「操作知识体」**。

### 目录命名规则

所有 vault 顶层目录必须是中文，无编号前缀。**用户明确拒绝了 `02_Agent_Outputs` 这种英数混合名**，改为 `产出/`（平坦结构，零子目录）。

规则：
```
✅ 决策/  知识/  流程/  成果/  报告/  配置/  产出/  学习档案/
❌ 02_Agent_Outputs/  01_Decisions/  agents-output/
```

任何脚本或工具创建了编号前缀目录，立即重命名为合规中文名。

### 新3文件架构

所有 Agent SOP 合并为 3 个核心文件：

| 文件 | 用途 | 更新方式 |
|------|------|----------|
| `SYSTEM.md` | 主脑文档 — 所有 Agent SOP 作为模块块 | 直接编辑追加 |
| `AGENT_REGISTRY.md` | 轻量索引 | 追加一行 |
| `scheduler.yaml` | 唯一调度源 | 追加 job 条目 |

### SYSTEM.md Agent 模块块格式

```markdown
## 🔹 Agent: {agent_id}

### 🎯 目标
{一句话目标}

### 📥 输入 / 📤 输出

### ⚙️ 执行流程
1. {步骤1}  2. {步骤2}  3. {步骤3}

### 🚨 异常处理 / ⏱ 调度
```

模块块必须包含完整的 Lead → Execution → QA → Escalation → Growth → Crisis 六件套描述。

### 记忆检索层

所有 Agent 执行前必须通过记忆层获取历史参考。这是 v2.0 架构的核心升级。

**代码入口**: `~/Molin-OS/molib/memory/retriever.py`

双源检索：Obsidian（结构化知识 `产出/业务线｜type·date.md`，v3.0 flat vault，零子目录）+ Supermemory（语义块）。

```python
from molib.memory.retriever import retrieve_context

# 标准检索（Agent 决策时使用）
context = retrieve_context(
    query="转化率提升策略",
    agent_name="edu",
    section_filter=["洞察", "可复用知识"],  # 只返回精华区块
    top_k=5,
    days_back=30
)

# 检索结果含 summary 字段可直接注入 prompt
agent_prompt = f"{task}\\n\\n## 历史参考\\n{context['summary']}"
```

**四层记忆架构**：

```
🔴 L1 工作记忆     → 飞书对话上下文（24h 清理）
🟡 L2 情节记忆     → Supermemory（30天未调用→蒸馏到 L3）
🟢 L3 语义记忆     → Obsidian `产出/业务线｜type·date.md`（v3.0 flat vault，永久）
🔵 L4 程序记忆     → skill 文件（版本化管理）
```

L1→L2→L3→L4 的蒸馏条件和写入规则详见 `references/memory-taxonomy.md`。

### Agent 输出标准模板

所有输出必须通过 `~/Molin-OS/molib/memory/output_writer.py` 写入。

**强制区块顺序**：

```
# 🧠 Agent Output: {agent_name}
## 🕒 Metadata（时间/Agent/类型/来源）
## 🎯 任务目标
## 📊 核心结果
## 🔍 详细分析
## ⚙️ 执行动作
## 🚨 风险与异常
## 🧩 可复用知识（关键！被检索器独立索引）
## 🔗 关联知识
```

**双写机制**：
- **Obsidian**: `产出/业务线｜{type}·{date}.md`（v3.0 flat vault，零子目录）
- **Supermemory**: 拆分为语义块（Summary / Insight / Action 分别写，便于后续检索时只命中精华）

```python
from molib.memory.output_writer import write_agent_output

result = write_agent_output(
    agent_id="finance",
    output_type="daily_report",
    goal="生成今日财务日报",
    summary="总成本¥18.00 | 内容Agent占比44%",
    analysis="**成本结构**\\n- DeepSeek Flash: ¥4.50 (25%)\\n- ...",
    actions="- 已记录日成本\\n- 预算预警",
    learnings="- 内容Agent是最大成本来源",
)
# result = {agent, date, obsidian_path, supermemory}
```

### iCloud 幽灵目录处理

iCloud Drive 会在 `rm -rf` 后自动恢复目录结构。症状：空目录壳反复出现。原因：iCloud 索引与本地文件系统冲突。

**处理步骤**：
1. 清空所有文件：`echo "" > dir/*.md`
2. 设置 immutable 锁：`chflags -R uchg dir/`
3. 删除：`rm -rf dir/`
4. 如果仍恢复，移到 iCloud 外再删：`mv dir/ /tmp/ && rm -rf /tmp/dir/`
5. 如果都不行，在 `vault_health_check.py` 的 `ALLOWED_DIRS` 中白名单该目录名

v3.0: 零子目录。`产出/{agent_id}/` 这类 agent_id 子目录已消灭，所有输出以 `业务线｜type·date.md` 命名直接放入 产出/。

### 目录命名规则（硬性约束）

所有 vault 顶层目录必须用全中文，无编号前缀。

```
✅ 决策/  知识/  流程/  成果/  报告/  配置/  产出/  学习档案/
❌ 02_Agent_Outputs/  agents-output/  01_Decisions/  system_archives/
```

用户明确拒绝了 `02_Agent_Outputs` 这种英数混合名，必须改为 `产出/`。产出目录内零子目录，所有 Agent 输出以 `业务线｜主题.md` 命名直接放入。

### 执行优先原则（用户偏好 — 硬性规则）

**用户明确要求：分析后必须立刻执行，不能停留在纯分析阶段。**

处理 vault 整理、文件迁移、系统优化等任务时：
1. ❌ 分析完列出计划就说"已完成"
2. ✅ 分析 → 立刻执行迁移/删除/重命名操作 → 验证结果

用户 frustration 信号："文件要整理啊，这么傻呢"、"光分析不动手"。每次这类反馈都必须嵌入本 template 的规则。

即使操作可能被 iCloud 等外部系统干扰，也必须先尝试执行，再处理异常。

### 全量排查根因方法论（用户偏好 — 硬性规则）

**用户明确要求："要全面排查根因，不要哪里不行修哪里，没有全局考虑系统"。**

当发现 vault 或其他系统出现不合规文件/配置时：
1. ❌ 只修用户指出的那几个文件
2. ✅ 全量审计 → 根因溯源 → 封堵所有源头 → 验证归零 → 加防复发护栏

具体步骤：
```
Phase 1: 全量审计 — 扫描所有违规（不是只看用户指出的3个，而是找全所有N个）
Phase 2: 根因溯源 — 追查每个违规的写入源（脚本/技能/Cron/内存同步/Agent记忆/会话文件）
Phase 3: 源头封堵 — 一次性修复所有写入源（不是修一个漏一个）
Phase 4: 防复发护栏 — 更新检查脚本 + 记忆固化禁止路径
Phase 5: 全域验证 — grep 全量扫描确认归零
```

排查范围必须覆盖四层：
- 层1：Molin-OS 核心脚本（scripts/、molib/、tools/）
- 层2：Hermes 技能文件（~/.hermes/skills/）
- 层3：Agent 配置文件（~/.hermes/profiles/{agent}/skills/、scripts/、memories/）
- 层4：系统文档（SYSTEM.md、产出写入规范.md）

用户 frustration 信号："又出现了"、"这些还没处理呢"、"保证以后不会出现"。触发此类信号 → 立刻切换为全量排查模式，不要继续点状修复。

---

### 创建新 Agent 的 v2.0 流程

```bash
# 1. 获取此模板
skill_view('agent-sop-template')

# 2. 在 SYSTEM.md 追加模块块
vim SYSTEM.md  # 添加 ## 🔹 Agent: {id}\n\n### 🎯 目标\n...

# 3. 注册到索引
echo "| {id} | {name} | {desc} | {cron} |" >> AGENT_REGISTRY.md

# 4. 注册到调度
cat >> scheduler.yaml << 'EOF'
  - id: {id}_{task}
    agent: {id}
    cron: "{schedule}"
EOF

# 5. 如有必要，创建对应 Hermes skill 作专业知识库
skill_manage(action='create', name='{id}-sop-pack', content='...')

# 6. v3.0 flat vault — zero subdirectories. Agent outputs go to 产出/业务线｜type·date.md
#    No mkdir needed — the 8 root dirs already exist, files go directly into them.
```

### v1 兼容说明

之前创建的独立 SOP skill 文件（content-sop-pack、design-sop-pack 等）仍保留为专业知识库。执行流程知识有效，但 SOP 定义以 SYSTEM.md 为准。当两者冲突时，SYSTEM.md 优先。

## 参考文件

| 文件 | 内容 |
|------|------|
| `references/memory-augmented-decision-making.md` | 记忆检索层接入方式 + 代码示例 |
| `references/agent-output-template.md` | Agent 输出标准模板 + Supermemory 语义块划分规则 |
| `references/dual-format-sop-pattern.md` | YAML + Markdown 双格式 SOP 说明 |
| `references/vault-hardening-methodology.md` | 全量排查→根因封堵→防复发 五阶段方法论（v3.0 硬化实战） |
