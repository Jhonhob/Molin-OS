# 财务 Cron 数据对账参考

> 适用于 23:00 财务日报 Cron — 处理 daily_summary.json 与 live relay/kpi/ 的时序差异

## 数据流水线时序

```
21:50 — 墨测数据 Cron 写入 daily_summary.json
        （基于截至此刻的 relay/kpi/ 文件快照）
22:00 — 内容复盘 Cron → 可能写入 content_writer_{date}.json
22:00 — 其它 Agent Cron → 可能写入各自的 KPI JSON
23:00 — 🕐 财务 Cron 执行（本 Cron）
```

## 采集顺序（严格执行）

```
Step 1: 检查 relay/finance_daily_{date}.json 是否已存在
        → 已存在：跳过全量分析，直接输出摘要（不重复执行）
        → 不存在：执行完整分析

Step 2: ls -la /Users/laomo/relay/kpi/*{date}.json
        → 实时文件系统扫描，不依赖 daily_summary.json 的判别
        → 注意：daily_summary 的 "无KPI文件" 可能在 21:50 生成时为真，
          但 23:00 时已存在

Step 3: 读取所有匹配的 KPI JSON 文件
        → content_writer_{date}.json（如果有）
        → 其他 {agent}_{date}.json（如果有）

Step 4: 读取 daily_summary.json 获取：7日均值、前日数据、异常检测
        → 用 daily_summary 的 pre-computed 7日趋势和 z-score 判断
        → 不重复计算环比

Step 5: 对比 Step 2 与 Step 4 → 如果有 Step 2 发现但 daily_summary
        未收录的 KPI 文件，在报告数据质量节标注"复盘补扫发现"
```

## 关键陷阱

| 陷阱 | 后果 | 对策 |
|------|------|------|
| 只读 daily_summary 不扫 relay/kpi/ | 错过 content_writer 22:00 写入的数据 | 必须先 `ls relay/kpi/*{date}.json` |
| 认为 daily_summary 的 KPI 判别完全准确 | 报告显示"0 KPI"但其实已有 | 用 recheck 结果覆盖 |
| 使用旧路径 `/Users/laomo/Molin-OS/relay/kpi/` | 文件找不到，成本为 0 | 用绝对路径 `/Users/laomo/relay/kpi/` |
