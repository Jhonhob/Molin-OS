# daily_summary.json 数据结构

输出路径：`relay/data/daily_summary.json`
生成者：墨测数据·21:50 Cron（data-sop-pack + kpi-tracker）

## 顶层结构

```json
{
  "report_type": "daily_summary",
  "date": "2026-05-17",
  "generated_at": "2026-05-17T21:58:05+08:00",
  "generated_by": "墨测数据·data_daily_cron",
  "version": "2.0",
  "summary": { ... },
  "business_lines": { ... },
  "cross_business_anomalies": { ... },
  "meta": { ... }
}
```

## summary — 全局摘要

```json
{
  "headline": "一句话总结当天",
  "key_metrics": {
    "total_api_cost_estimate": 1.14,
    "total_tasks": 2,
    "agents_active": 2,
    "agents_total": 22,
    "agents_reporting_kpi": 1
  },
  "alerts": ["需要关注的问题列表"]
}
```

## business_lines — 各业务线详情

每业务线结构：

```json
{
  "agent": "Agent名称",
  "today": { /* 今日指标 */ },
  "yesterday": { /* 昨日指标 */ },
  "day_over_day": { /* 环比变化 */ },
  "seven_day_avg": { /* 7日均值 */ },
  "seven_day_trend": { /* 7日序列 */ },
  "anomalies": [{ /* 异常检测结果 */ }],
  "estimate": true/false
}
```

### 异常检测字段

```json
{
  "metric": "api_cost",
  "value": 1.14,
  "mean": 3.01,
  "std": 0.834,
  "z_score": -2.24,
  "severity": "info|medium|high|critical",
  "note": "低于-2σ，但符合周日产量规律，非异常"
}
```

severity 判定：
- z ≤ ±2σ → 无异常（不写入）
- |z| > 2σ 且 |z| ≤ 3σ → info/medium（需业务判断）
- |z| > 3σ → critical

## cross_business_anomalies — 交叉业务异常

```json
{
  "anomaly_id": {
    "severity": "medium",
    "issue": "问题描述",
    "action": "建议行动",
    "affected_agents": ["列表"]
  }
}
```

## 数据源优先级

1. `relay/kpi/{agent}_{date}.json` — 结构化 KPI（最优先）
2. `relay/finance_daily_{date}.json` — 财务日报
3. `relay/side/daily_status.json` — 电商/客服数据
4. Obsidian `产出/` 目录 — 非结构化 Agent 产出（教育线等）
5. Obsidian `学习档案/` — Agent 学习产出
