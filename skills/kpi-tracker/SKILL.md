---
name: kpi-tracker
description: 墨麟AI KPI 追踪框架 — 每个 Agent 的效能/质量/业务 KPI 采集、存储、报告
category: molin-org
version: 1.4.0
tags: [kpi, metrics, dashboard, tracking, analytics, weekly-plan]
trigger: 每日复盘 Cron 加载此技能写入 KPI 数据；每周经营报告聚合趋势；周一 09:30 周计划生成
changelog:
  - 1.5.0 (2026-05-18): 新增周一复盘·周计划耦合规范（Section 6.2 frontmatter + 周目标追踪表 + 昨日P0回检）。新增陷阱11（daily_summary.json KPI判别可能滞后，22:30需recheck relay/kpi/）
  - 1.4.0 (2026-05-18): 新增第八章「周一 09:30 周计划产出规范」→ 周计划六模块模板（复盘摘要/OKR对齐/各线优先级/学习重点/关注指标/关键决策）。数据源串联：daily_summary.json + relay/kpi/周聚合 + 上周系统日报。
  - 1.3.0 (2026-05-17): 新增第六章「22:30 系统复盘产出规范」→ 明确 报告/系统｜日报·{date}.md 的六模块模板。修正 relay 绝对路径为 /Users/laomo/Molin-OS/relay/（~/.hermes-os/ 不存在于磁盘）。新增陷阱 1（relay 绝对路径）、9（复盘 vs KPI 聚合时序）、10（产出/ vs 报告/ 系统日报区分）。
  - 1.2.0 (2026-05-17): v2 输出路径升级，Obsidian v3.0 平坦结构，全量聚合 daily_summary.json
---

# KPI Tracker — 经营指标追踪框架

## 架构

```
每个 Agent
    ↓ 执行完毕后记录
Agent 专属 KPI 数据（JSON）
    ↓ 每日复盘时汇总
日级 KPI 聚合（写入 Obsidian）
    ↓ 周日 21:00 聚合
周级 KPI 报告 + 趋势分析
```

---

## 一、KPI 分类体系

### 通用 KPI（所有 Agent 必报）

#### 效能类（效率）
| 指标 | 单位 | 采集方式 | 说明 |
|------|------|----------|------|
| task_count | 次 | 执行 SOP 完成时计数 | 当日完成任务数 |
| success_rate | % | 成功/失败计数 | 成功率 |
| avg_duration | 秒 | 开始-结束时间差 | 平均执行时长 |
| token_consumed | token | 记录消耗 | 总 Token 消耗 |
| token_per_task | token | token_consumed / task_count | 单任务 Token 效率 |

#### 质量类
| 指标 | 单位 | 采集方式 | 说明 |
|------|------|----------|------|
| avg_qa_score | 分 | QA SOP 评分均值 | 当日平均质量分 |
| min_qa_score | 分 | 当日最低分 | 质量底线 |
| pass_rate_80 | % | QA ≥ 80 的任务占比 | 高质量输出率 |
| fail_rate_60 | % | QA < 60 的任务占比 | 不合格率 |
| escalations | 次 | Escalation 触发计数 | 异常升级次数 |

#### 成本类
| 指标 | 单位 | 采集方式 | 说明 |
|------|------|----------|------|
| api_cost | ¥ | token × 模型单价 | API 成本 |
| cost_per_task | ¥ | api_cost / task_count | 单任务成本 |
| cost_per_quality_task | ¥ | api_cost / pass_count_80 | 高质量单任务成本 |

### 业务专属 KPI（各 Agent 自定义）

| Agent | 业务 KPI | 采集方式 |
|-------|----------|----------|
| Content Agent | 内容产出量、平台覆盖率、CTA 完整率 | 执行 SOP 计数 |
| Sales Agent | 跟进率、成交率、Pipeline 价值 | CRM 系统 |
| Growth Agent | 转化率、CAC、LTV、AB测试结果 | 数据系统 |
| Research Agent | 情报数量、命中率、时效性 | 情报系统 |

---

## 二、数据存储格式

### 日级数据

每个 Agent 每天一条，写入 `relay/kpi/{agent}_{date}.json`：

```json
{
  "agent": "content_writer",
  "date": "2026-05-17",
  "efficiency": {
    "task_count": 5,
    "success_rate": 100,
    "avg_duration_s": 45,
    "token_consumed": 128000,
    "token_per_task": 25600
  },
  "quality": {
    "avg_qa_score": 82,
    "min_qa_score": 68,
    "pass_rate_80": 60,
    "fail_rate_60": 0,
    "escalations": 1
  },
  "cost": {
    "api_cost": 1.28,
    "cost_per_task": 0.256,
    "cost_per_quality_task": 0.427
  },
  "business": {
    "content_count": 5,
    "platform_count": 3,
    "cta_complete_rate": 80
  },
  "anomalies": ["QA评分68：合规检查维度偏低，已自动修正"]
}
```

### v2 输出路径升级

2026-05-17 起，Agent 输出统一写入 Obsidian v3.0 平坦结构。
KPI 数据仍写 `relay/kpi/{agent}_{date}.json`（中间数据），日报/报告产出走 `产出/` + `报告/`（8根目录·零子目录）。

跨业务线全量聚合写入 `relay/data/daily_summary.json`（墨测数据·21:50 Cron 产出），包含：
- 各业务线今日 KPI + 昨日对比 + 7日均值
- 异常检测 ±2σ（周日常规低产标记 ℹ️ 不告警）
- 交叉业务异常（KPI覆盖率、数据缺失等）
- 供 06:00 数据快照和 09:00 看板消费

看板路径：`报告/KPI｜日报·{date}.md` / `报告/KPI｜周报·{start}-{end}.md`（由 `scripts/kpi-dashboard/generate_dashboard.py` 生成）。

### 周级聚合

周日复盘时自动聚合，写入 Obsidian `报告/KPI｜周报·{week_start}_{week_end}.md`：

```json
{
  "agent": "content_writer",
  "week_start": "2026-05-11",
  "week_end": "2026-05-17",
  "daily_records": ["2026-05-11", "2026-05-12", ...],
  "trends": {
    "avg_qa_score": {"monday": 75, "tuesday": 78, ..., "sunday": 82},
    "task_count": {"monday": 3, "tuesday": 4, ..., "sunday": 5},
    "cost_per_task": {"monday": 0.35, "tuesday": 0.30, ..., "sunday": 0.256}
  },
  "summary": {
    "total_tasks": 28,
    "avg_qa_score": 79,
    "improving_dimensions": ["QA评分", "成本效率"],
    "declining_dimensions": [],
    "top_issue": "合规检查（-5分 vs 上周）"
  }
}
```

---

## 三、KPI 看板模板

看板写入 Obsidian `报告/KPI｜周报·W{week_number}.md`（平坦结构，零子目录）：

```markdown
# {Agent} KPI 看板 — 第 {week_number} 周

## 效能趋势

```chart
type: line
data: [周一到周日的 task_count]
```

| 指标 | 本周 | 上周 | 环比 |
|------|------|------|------|
| 任务数 | 28 | 25 | +12% |
| 成功率 | 96% | 94% | +2% |
| 平均耗时 | 45s | 52s | -13% |

## 质量趋势

```chart
type: line
data: [周一到周日的 avg_qa_score]
```

| 指标 | 本周 | 上周 | 环比 |
|------|------|------|------|
| QA均分 | 79 | 75 | +5% |
| 高质量率 | 60% | 55% | +5% |
| 不合格率 | 3% | 5% | -2% |

## 成本趋势

| 指标 | 本周 | 上周 | 环比 |
|------|------|------|------|
| API成本 | ¥8.96 | ¥10.50 | -15% |
| 单任务成本 | ¥0.32 | ¥0.42 | -24% |

## 发现问题与改进

1. 问题：{描述}
   - 影响：{影响面}
   - 建议：{改进措施}

---

数据来源：relay/kpi/ | 生成时间：{datetime}
```

---

## 四、集成方式

### 在 22:00 复盘 Cron 中调用

复盘时增加 KPI 采集步骤（数据消费链）。**注意：22:30 复盘 Cron（本 job）包含两个产出**：
1. KPI 日报 → `报告/KPI｜日报·{date}.md`（如已由墨测数据生成则跳过）
2. 系统综合日报 → `报告/系统｜日报·{date}.md`（核心产出，见第六章模板）

```
                               ┌─────────────────────┐
                               │ relay/kpi/*.json    │ ← 各Agent日KPI（可能已存在）
                               └──────┬──────────────┘
                                      │ 读取
                               ┌──────▼──────────────┐
                               │ relay/data/         │
                               │ daily_summary.json  │ ← 跨业务聚合(21:50)
                               └──────┬──────────────┘
                                      │ 读取
                               ┌──────▼──────────────┐
                               │ 22:00 复盘 Cron     │
                               │                     │
                               │ ① 读取relay/kpi/    │
                               │ ② 读取daily_summary │
                               │ ③ 计算环比/趋势     │
                               │ ④ Gatekeeper终检    │
                               └──────┬──────────────┘
                                      │
                        ┌─────────────┼─────────────┐
                        ▼             ▼             ▼
                ┌────────────┐ ┌──────────┐ ┌──────────┐
                │ 报告/     │ │ relay/   │ │ relay/   │
                │ KPI｜日报  │ │ data/    │ │ kpi/*.   │
                │ {date}.md │ │ daily_   │ │ json     │
                └────────────┘ │ review_  │ │ (if new) │
                               │ {date}.  │ └──────────┘
                               │ json     │
                               └──────────┘
```

步骤：
1. 先检查 `relay/kpi/{agent}_{date}.json` 是否已存在——如果存在则跳过写入，仅读取
2. 再读取 `relay/data/daily_summary.json`（由墨测数据 21:50 Cron 写入，含±2σ异常检测）
3. 读取上周同日数据计算环比
4. 如果指标连续下降（3天）→ 触发 Escalation L1 通知
5. Gatekeeper 终检（确保输出质量 ≥ gatekeeper-sop 标准）
6. 写入 Obsidian `报告/KPI｜日报·{date}.md`
7. 写入复盘元数据 `relay/data/daily_review_{date}.json`

注意：`relay/data/daily_summary.json` 已在复盘前由墨测数据 Cron 产出，包含按业务线的 today/yesterday/7-day-avg/day_over_day/±2σ-zscore 预计算数据，复盘时直接读取即可，无需重新计算环比。

### 在周日 21:00 周报 Cron 中聚合

```
1. 读取本周 7 天 relay/kpi/*.json（不足7天则用 estimate:true 补齐）
2. 聚合周级数据
3. 生成趋势分析
4. 写入 Obsidian `报告/`（周报 + 内容经营周报）
```

---

## 五、现有 Cron 升级

### 22:00 复盘 Cron 升级

在现有复盘 prompt 中增加：

> ### KPI 采集（附加步骤）
> 根据今日产出，按 `relay/kpi/{agent}_{date}.json` 格式写入 KPI 数据。
> 如果不知道精确的 Token 消耗数据，估算即可（记录为 estimate:true）。

---

## 六、22:30 系统复盘产出规范

22:30 复盘 Cron 产出 **两份** 文档：

### 6.1 KPI 日报（已有模板）
→ `报告/KPI｜日报·{date}.md`（由 `scripts/kpi-dashboard/generate_dashboard.py` 生成，或手动按第三节模板写入）

### 6.2 系统综合日报（复盘核心产出）
→ `报告/系统｜日报·{date}.md`（**本节规范**）

**必含六大模块**（≥600 字），按此顺序。**周一特例**：周一复盘需额外引用当日早间已生成的 `报告/系统｜周计划·{date}.md`，在 frontmatter `related:` 中添加 `[[系统｜周计划·{date}]]`，在 Section 四（明日三重点）之后追加「WXX 本周目标达成追踪」表（对齐周计划中本周目标 vs 当日实际进度，含判定列），在 Section 二之前追加「对比昨日P0建议回检」自然段（验证昨日复盘提出的P0是否完成）。

```markdown
---
created: {date}
updated: {date}
agent: system
category: 报告
status: 活跃
confidence: 已验证
importance: ⭐⭐
source: 实践
tags: [日报, 复盘, KPI, 系统]
related: [[KPI｜日报·{date}]], [[银月｜内容经营复盘·{date}]], [[KPI｜周报·{start}~{end}]]
---

# 系统日报 · {date}（{星期}）

> 复盘时间：22:30 | 类型：每日复盘 | Gatekeeper：pass/fail

## 一、KPI 核心数据
### 今日全局（表：指标/值/昨日/7日均值/判定）
### 墨笔文创 KPI 详表（唯一量化上报Agent）
### 元瑶教育产出摘要（无量化KPI时按产出项计数）

## 二、今日完成事项
按业务线分组（内容线/增长线/教育线/数据线），每项 ✅ 标记

### 对比昨日P0建议回检（可选，非周一也推荐执行）
逐项对照昨日复盘Section四中的P0/P1建议 → 完成/未完成 → 判定列。非周一复盘取昨日系统日报即可。

## 三、卡点 / 待解决问题
分 🔴 紧急 / 🟡 需关注 / 🟢 系统健康 三级，附建议

## 四、明日三重点
| 优先级 | 事项 | 责任人 | 预期产出 | 三行表格

## 五、系统健康快照
组件状态表（Gateway/CDP/Vault/磁盘/负载/内存/Cron）

## 六、周度收官（仅周日/周报日附加）
本周概况 + 环比 + 关键发现
```

**与 KPI 日报的区别**：KPI 日报是数据看板，系统日报是综合复盘——包含完成事项、卡点、明日计划、系统健康，是面向创始人的经营摘要。

---

## 七、参考

- **relay 绝对路径**：`/Users/laomo/Molin-OS/relay/`（所有 relay 数据统一在此目录）
  - `relay/kpi/{agent}_{date}.json` → `/Users/laomo/Molin-OS/relay/kpi/`
  - `relay/data/daily_summary.json` → `/Users/laomo/Molin-OS/relay/data/`
  - `relay/data/daily_review_{date}.json` → `/Users/laomo/Molin-OS/relay/data/`
- **Obsidian vault 路径**：`/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents`（v3.0 平坦结构：报告/、产出/、成果/ 等 8 个根目录，无子目录）
- KPI 看板生成：`skill_view('kpi-dashboard')` — 从 relay/kpi/ 生成可视化的经营看板
- 看板生成脚本：`scripts/kpi-dashboard/generate_dashboard.py`
- 环比计算规则：与上周同一天对比
- 连续下降阈值：3 天自动告警
- Agent 模板：`skill_view('agent-sop-template')`

---

## 八、周一 09:30 周计划产出规范

周一 09:30 生成本周经营计划，衔接周日复盘数据与本周目标。写入 `报告/系统｜周计划·{date}.md`（平坦结构，零子目录）。

### 8.1 触发条件

| 条件 | 说明 |
|------|------|
| Cron 触发 | 周一 09:30 定时执行 |
| 数据前提 | 上周 daily_summary.json + relay/kpi/ 周聚合数据已存在 |
| 上下文来源 | 上周系统日报·周日 + 内容经营复盘 + KPI 周报 |

### 8.2 数据源采集顺序

```
① relay/data/daily_summary.json           ← 墨测数据 21:50 产出：全业务线日起/昨日/7日均值/±2σ
② relay/kpi/{agent}_weekly_*.json          ← 周日增长复盘聚合：周趋势/周总成本/问题/改进
③ relay/data/daily_review_{date}.json      ← 周日复盘 Meta：卡点/明日优先级/Gatekeeper终判
④ 报告/系统｜日报·{date}.md                ← 上周日系统日报：卡点/组件快照/周度收官
⑤ 报告/KPI｜周报·{start}~{end}.md          ← KPI 周报：指标/环比/改进建议
⑥ 报告/银月｜内容经营复盘·{date}.md         ← 内容经营复盘：优化建议/EXP 实验状态
⑦ 产出/元瑶｜*（教育线近期产出文件）         ← 教育线 Phase 进度/技术验证状态
```

**关键规则**：
- 不要重复计算环比 —— daily_summary.json 已有 ±2σ 预计算
- relay/kpi/ 可能只有 content_writer 有完整数据，其他 Agent 用 estimate 标记
- 教育线无量化 KPI 时，按产出文件数量统计（output_count）

### 8.3 六大模块结构（≥800 字）

```markdown
---
created: {date}
updated: {date}
agent: system
category: 报告
status: 活跃
confidence: 已验证
importance: ⭐⭐⭐
source: 实践
tags: [周计划, W{week_number}, 系统, 经营计划]
related: [[系统｜日报·{prev_sun}]], [[KPI｜周报·{start}~{end}]], [[KPI｜内容经营周报·W{prev_week}]], [[银月｜内容经营复盘·{prev_sun}]]
---

# 系统周计划 · 第 {week_number} 周（{date} ~ {week_end}）

> 编制时间：{date} 09:30 | 类型：周一规划 | 依据：上周复盘 + daily_summary + 周报

---

## 一、上周复盘摘要

### 经营数据速览
| 指标 | 上周 | 环比上上周 | 趋势 |
|------|------|-----------|------|
| ... | ... | ... | 🟢/🟡/🔴 |

### 本周核心发现
- ✅ 亮点：列出上周亮点
- 🔴 问题：列出上周暴露的问题（合规/KPI覆盖率等）
- 🟡 进行中：实验中/待完成事项

### 已有改进措施
| 实验/措施 | 目标 | 状态 |
|-----------|------|------|
| EXP-NNN | 描述 | ⏳ 待本周激活/✅ 已生效 |

---

## 二、OKR 对齐

推定 OKR（可更新，不硬性要求季度文档存在）。每个 O 拆 2-4 个 KR。

### O1：{主题}
| KR | 当前值 | 本周目标 | 年终目标 |
|----|--------|----------|----------|
| ... | ... | ... | ... |

### O2：{主题}
...

---

## 三、各业务线优先级

按 内容线/教育线/增长线/数据线/运维线 分组，每线含：

| 优先级 | 事项 | 预期产出 | 时间 |
|--------|------|----------|------|
| P0 | 本周最重要的是什么 | 可验证的产出 | 具体日期 |
| P1 | ... | ... | ... |
| P2 | ... | ... | ... |

**P0 标记本周不得不做的事**；P1 正常推进；P2 有余力时做。

---

## 四、学习重点

本周学习焦点表 + 持续学习管道状态表。

| 领域 | 学习主题 | 预期产出 |
|------|----------|----------|
| ... | ... | `学习档案/...` |

---

## 五、关注指标

### 日常看板指标
| 序号 | 指标 | 目标值 | 容忍上限 | 本周重点关注原因 |
|------|------|--------|----------|------------------|
| 1 | ... | ... | ... | ... |

### 阈值告警规则
| 条件 | 动作 |
|------|------|
| 连续 2 天 QA < 78 | 🟡 触发门禁复盘 |
| 单日成本 > ¥1.00/任务（工作日） | 🟡 检查模型路由 |
| KPI 覆盖率连续 3 天无增长 | 🔴 系统检查管道 |

### 周度节奏表
| 时间 | 打卡点 | 产出 |
|------|--------|------|
| 周一 09:30 | 周计划发布 | `报告/系统｜周计划·{date}.md` ✅ |

---

## 六、本周关键决策 / 待确认

| # | 决策项 | 触发时间 | 建议方案 | 建议决策 |
|---|--------|---------|----------|----------|
| 1 | ... | ... | ... | ✅ 自动/🟡 需确认 |

---

### 本周备忘
滚动重点提示（上周教训、财务预算快照、Git 备份等）
```

### 8.4 写入与交付

1. 生成完整内容后，`write_file` 写入 `报告/系统｜周计划·{date}.md`
2. 写入后 `head -n1` 验证 frontmatter 无行号污染
3. 在最终响应中输出周计划精华摘要（含 emoji 分线、数据表格、P0 标记）
4. Cron deliver 自动推送——不需要额外 send_message
5. 标记 `related:` 中 chain 回 `系统｜日报·上周日` + `KPI｜周报·上周`

### 8.5 质量门禁（写入前必问）

1. ≥800 字了吗？不足则补
2. 上周数据有来源吗？（relay/kpi/ 或 daily_summary.json 必须有引用）
3. OKR 对齐了吗？即使没找到正式 OKR 文档，也要推定一组
4. 各线都有 P0 吗？至少内容线/教育线必须写 P0
5. 关注指标有目标值吗？只看数据不看目标的周计划是废纸

---

### ⚠️ 常见陷阱

1. **relay 绝对路径**：relay 在 `/Users/laomo/Molin-OS/relay/`。使用绝对路径 `/Users/laomo/Molin-OS/relay/kpi/`、`/Users/laomo/Molin-OS/relay/data/`。
2. **Vault 路径错误**：不要假设 `~/Obsidian/` 或 `~/MolinOS-Wiki/` —— vault 在 iCloud `Library/Mobile Documents/iCloud~md~obsidian/Documents`
3. **子目录路径**：v3.0 平坦结构无子目录——所有报告直接写入 `报告/` 根目录，不要写入 `Agents/内容Agent/周报/` 等嵌套路径
4. **relay/kpi/ 可能不存在**：首次运行需要 `mkdir -p /Users/laomo/Molin-OS/relay/kpi/`
5. **relay/data/ 可能不存在**：全量聚合写入 `relay/data/daily_summary.json`，首次运行需 `mkdir -p /Users/laomo/Molin-OS/relay/data/`
6. **estimate 标记**：无法获取精确 token/成本数据时估算并标记 `"estimate": true`，不阻塞流程
7. **周日低产不告警**：API 成本 -2σ 等级别在周日属正常节奏，标记 ℹ️ 不触发 Escalation
8. **复盘元数据 JSON**：复盘 Cron 完成后写入 `relay/data/daily_review_{date}.json`，包含 gatekeeper 终判、明日优先级、异常摘要——供 09:00 选题会 Cron 和次晨快照消费
9. **22:30 复盘 vs 21:58 KPI 聚合**：复盘前 `daily_summary.json` 已由墨测数据生成。复盘只需读取已有数据——不要重复计算环比、不要重复生成 KPI 日报（如已存在则跳过），重点是产出 `报告/系统｜日报·{date}.md`（综合经营摘要）
10. **产出/ 下有另一份系统｜日报.md**：`产出/系统｜日报.md` 是滚动追加的历史日志，22:30 复盘产出的 `报告/系统｜日报·{date}.md` 是带日期后缀的综合复盘——两份文件不同，不要混淆
11. **daily_summary.json 可能滞后于实时 KPI 数据**：`daily_summary.json` 由墨测数据在 21:50 生成，而 22:00 内容复盘 Cron 可能在此之后写入 `relay/kpi/content_writer_{date}.json`。因此 22:30 复盘时 `daily_summary.json` 中的 "无KPI文件" 警报可能已过时。**应对**：22:30 复盘必须直接 `ls relay/kpi/*{date}.json` 重新扫描文件系统，不盲信 daily_summary 的判别。如果 recheck 发现文件已存在，在系统日报中标记为 `（复盘补扫发现）` 并更新相关 KPI 数据。
