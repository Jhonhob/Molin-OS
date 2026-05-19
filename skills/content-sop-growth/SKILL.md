---
name: content-sop-growth
description: 内容 Agent 增长 SOP — 基于 KPI 数据的 AB 测试生成、执行与复盘
category: molin-org
version: 1.1.0
tags: [sop, growth, ab-testing, optimization, roi]
trigger: 周日 21:00 周报复盘时加载，或手动触发增长实验
---

# 内容 Agent Growth SOP（增长优化）

## 定位

Growth SOP 的核心问题：

> 如何持续提高内容 ROI？

```
KPI 数据（过去 7 天）
    ↓ Growth SOP
增长瓶颈识别 → 实验假设生成 → 实验执行 → 结果复盘 → 优化固化
```

---

## 一、增长瓶颈识别

### 分析框架

每个周日，分析过去 7 天的 KPI 数据，回答以下问题：

| 分析维度 | 问题 | 数据来源 |
|----------|------|----------|
| 成本瓶颈 | 单任务成本在上升吗？哪个模型最贵？ | relay/kpi/ |
| 质量瓶颈 | QA 均分偏低的是哪个维度？ | relay/kpi/ + 复盘笔记 |
| 效率瓶颈 | 哪个环节最耗时？ | avg_duration_s |
| 转化瓶颈 | 内容 CTA 完成率低？是否缺少互动引导？ | 内容排期 + 互动数据 |
| 覆盖瓶颈 | 哪些平台发布少？哪些平台反馈好？ | 平台分布统计 |

### ⚠️ 首次运行/数据不足时的处理

首次运行 Growth SOP 或 relay/kpi/ 中数据不足 7 天时：

1. 如果 `relay/kpi/` 为空，先检查 Obsidian `报告/` 下是否有历史 KPI 看板（`KPI｜周报·*.md`、`KPI｜日报·*.md`），从中提取摘要数据
2. 如果既有 relay/kpi/ 空又没有 Obsidian KPI 看板：基于可获取的最佳信息估算一套基线日级KPI数据写入 `relay/kpi/{agent}_{date}.json`，标记 `"estimate": true`
3. 确保 `relay/kpi/` 目录存在（`mkdir -p`），否则后面的步骤会写入失败
4. 缺失的天数用 estimate:true 补齐，使周聚合能覆盖完整 7 天的跨度

### 输出格式

```json
{
  "week": "2026-05-11 ~ 2026-05-17",
  "bottlenecks": [
    {
      "dimension": "成本",
      "metric": "cost_per_task",
      "value": 0.42,
      "trend": "up",
      "severity": "medium",
      "description": "单任务成本较上周上升 10%，主要由抖音内容制作引起"
    },
    {
      "dimension": "质量",
      "metric": "seo_structure",
      "value": 65,
      "trend": "flat",
      "severity": "high",
      "description": "SEO 结构维度连续 3 周低于 70，是最大质量短板"
    }
  ],
  "opportunities": [
    "小红书内容互动率高于均值 20%，可加大投入",
    "用户评论高频问题未被利用，可专门出解答内容"
  ]
}
```

---

## 二、AB 实验生成

### 实验类型

| 实验类型 | 变量 | 假设模板 | 周期 |
|----------|------|----------|------|
| 内容结构 | 钩子类型/段落长度/CTA位置 | "如果 {变量}，那么 {指标} 会提高 {预期效果}" | 3天 |
| 平台适配 | 改写程度/话题标签/发布时间 | "在 {平台} 上 {变量} 会影响 {指标}" | 5天 |
| 模型路由 | 用 pro vs flash 模型执行 | "用 {模型} 做 {任务类型} 时，{成本/质量} 会 {变化}" | 5天 |
| 话题选择 | 长尾 vs 爆款内容比例 | "增加 {类型} 内容比例能提升整体 {指标}" | 7天 |

### 实验格式

```yaml
experiment_id: EXP-20260517-001
name: "不同钩子类型对小红书 CTR 的影响"
hypothesis: "故事型钩子比提问型钩子 CTR 高 15%"
variables:
  - control: 提问型钩子（"你会...吗？"）
  - treatment: 故事型钩子（"昨天我遇到一个家长..."）
metrics:
  primary: ctr
  secondary: [收藏率, 评论数]
duration: 3 天（5篇 control vs 5篇 treatment）
confidence_threshold: 90%
risk_level: low
```

---

## 三、实验执行

### 调度规则

1. 每周最多同时运行 2 个实验
2. 低风险实验自动执行，中高风险需要 L2 审批
3. 每个实验必须有明确的 stopping rule（何时叫停）
4. 实验数据自动记录到 `relay/experiments/`（如果目录不存在，先 `mkdir -p relay/experiments/`）

### ⚠️ 实验目录不存在时的处理

如果 `relay/experiments/` 目录或其关键文件不存在：
- 首次运行：`mkdir -p relay/experiments/` 后正常写入
- 实验复盘：若无历史实验，输出 `experiments_reviewed: []` 并标记 `note: "首次运行Growth SOP，无历史实验记录"`
- 新实验草稿：照常生成写入 `relay/experiments/pending_{date}.json`

### 实验状态流

```
Draft（草稿）
    ↓
Active（运行中） — 如果 3 天无显著差异 → Canceled（取消）
    ↓
Concluded（结论明确） — 写入实验报告
    ↓
Applied（优化固化） — 将成功实验写入对应的 SOP 中
```

### 实验结果格式

```yaml
experiment_id: EXP-20260517-001
conclusion: "故事型钩子 CTR 比提问型高 18%（置信度 93%）"
action: "更新 Execution SOP Step 2 钩子规则"
effect_on_kpi:
  ctr: +18%
  engagement: +12%
applied_to_skill: content-sop-pack
patch_required: true
patch_detail: "Step 2 钩子类型增加故事型钩子优先级说明"
```

---

## 四、结果复盘与优化固化

### 周日 Growth 复盘流程

```
21:00  KPI 周报生成（kpi-tracker）
       ↓
21:15  增长瓶颈识别（Growth SOP Step 1）
       ↓
21:30  实验复盘（上周实验结论）
       ↓
21:40  新实验生成（Growth SOP Step 2）
       ↓
21:50  优化固化（成功实验 → 更新对应 SOP skill）
```

### 优化固化规则

- **实验成功（置信度 ≥ 90%）** → 立即更新对应 SOP skill
- **实验部分成功（70-89%）** → 延长实验周期或调整变量
- **实验失败（< 70%）** → 记录原因，供后续参考

成功实验固化方式：

```bash
# 示例：把实验结论 patch 进 content-sop-pack
skill_manage(action='patch', name='content-sop-pack',
  old_string='钩子类型配置',
  new_string='钩子类型配置（含实验结论：故事型钩子 CTR +18%）')
```

---

## 五、Cron 配置

### 周日增长复盘 Cron

| 时间 | 任务 | 加载技能 |
|------|------|----------|
| 周日 21:00 | KPI 周报 + 增长实验 | kpi-tracker + content-sop-growth |

### 与 22:00 复盘的区别

| | 每日复盘 | 周日增长 |
|--|----------|----------|
| 粒度 | 日级回顾 | 周级趋势 |
| 产出 | 次日优化建议 | AB实验方案 + SOP固化 |
| 数据量 | 单日 KPI | 7日 KPI 趋势 |
| 动作 | 小修复 | SOP 结构性优化 |

---

## 六、参考

- KPI 数据来源：`relay/kpi/` + Obsidian KPI 看板
- 实验存档：`relay/experiments/`
- SOP 更新：通过 `skill_manage(action='patch')` 实现
- 治理级别：低风险实验自动（L0），中风险通知（L1），高风险审批（L2）
