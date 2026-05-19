# 22:00 内容复盘执行规范

> 每次 22:00 复盘 Cron 必须执行此流程。
> 依赖技能：`content-sop-pack` + `kpi-tracker` + `gatekeeper-sop`

---

## 执行顺序

```
① 确认 daily_summary.json 是否存在
② 检查 relay/kpi/ 是否存在今日数据
③ 读取 daily_summary 获取今日 KPI + ±2σ 异常
④ 搜索今日内容产出文件（Obsidian 成果/ + relay/ 产出）
⑤ QA 趋势分析（周环比 vs 上周同日）
⑥ 3 天连续下降检测
⑦ 写入/跳过 KPI 数据
⑧ Gatekeeper 终检
⑨ 写入复盘笔记到 Obsidian
⑩ 写入复盘元数据到 relay/data/
```

---

## 详细子步骤

### Step 0：确认日期
```bash
date '+%Y-%m-%d'
```
存入变量 `$TODAY`。

### Step 1：确认 daily_summary.json
路径：`/Users/laomo/relay/data/daily_summary.json`
- 由墨测数据 Cron 在 21:50 写入
- 包含：各业务线 today/yesterday/7-day-avg/day_over_day/±2σ-zscore
- 如果没有 → 跳过环比计算，标记全部 estimate:true

### Step 2：检查今日 KPI 是否已有
路径：`/Users/laomo/relay/kpi/content_writer_${TODAY}.json`
- 如果存在 → 跳过 Step 7，只读取并引用
- 如果不存在 → 从 daily_summary 提取估算值，写入 KPI

### Step 3：读取 daily_summary 关键数据
从 `content` 业务块提取：
```python
today = daily_summary["business_lines"]["content"]["today"]
yesterday = daily_summary["business_lines"]["content"]["yesterday"]
seven_day_avg = daily_summary["business_lines"]["content"]["seven_day_avg"]
anomalies = daily_summary["business_lines"]["content"]["anomalies"]
cross_biz = daily_summary.get("cross_business_anomalies", {})
# 注意：带"｜"的文件名在 Obsidian 路径中是全角符号
```

### Step 4：搜索今日内容产出
检查两个位置：
1. Obsidian `成果/` 目录（`银月｜*.md` 等）
2. `relay/` 下今日新建的 JSON/MD 文件
3. 用户 home 目录下的内容 JSON 文件

提取：内容标题、平台、类型、状态

### Step 5：QA 趋势分析
- **环比上周同日**：读取上周同日的 KPI（如今天周一，读 `content_writer_{last_monday}.json`）
- **3 天连续下降检测**：检查近 3 天 avg_qa_score 是否连续下降
- **QA 波动规律**：周二至周四为高峰期（85-86），周一/周末偏低（78-80）

### Step 6：3 天连续下降检查
```python
qa_trend = [day3_qa, day2_qa, day1_qa, today_qa]  # 最新 4 天
if all(qa_trend[i] > qa_trend[i+1] for i in range(3)):
    trigger_escalation = True
```
如果触发 → 写入异常记录 + 在回复中告警

### Step 7：写入 KPI 数据
格式参见 kpi-tracker 的 `relay/kpi/{agent}_{date}.json` 模板。
必须标记 `"estimate": true` 除非有精确数据。
Token 估算：25K tokens × task_count（deepseek-chat 典型值）

### Step 8：Gatekeeper 终检
对照 gatekeeper-sop QA矩阵打分：
- 数据真实性：数据来源可验证？（daily_summary + 文件系统）
- 合规无风险：内容无敏感词/红线
- 逻辑完整性：趋势分析有数据支撑
- 可操作性：复盘建议可执行
- 格式规范性：文件按标准格式写入
- 时效性：当天的复盘

如果整体评分 ≥ 85 → pass
如果 70-84 → 自动修正
如果 < 70 → 触发 Escalation

### Step 9：写入复盘笔记到 Obsidian
路径：`报告/银月｜内容经营复盘·{date}.md`
模板参考 kpi-tracker 六模块 + content-sop SOP Section 四结构。

必含内容：
1. KPI 快照表格（含与上周同日、7日均值对比）
2. QA 趋势分析（含周度折线图示）
3. 今日内容产出清单
4. 异常记录（含严重度、状态）
5. 明日优化建议（短线修复 + 中期改进）
6. 经营建议（明日重点关注 + 成本监控 + W21 达成追踪）

### Step 10：写入复盘元数据
路径：`/Users/laomo/relay/data/daily_review_{date}.json`
包含：
```json
{
  "agent": "content_writer",
  "date": "...",
  "type": "daily_review",
  "generated_at": "...",
  "gatekeeper_status": "pass|fail",
  "kpi_written": true|false,
  "qa_summary": { ... },
  "anomalies": [...],
  "tomorrow_priorities": [...],
  "w21_review_progress": { ... }
}
```

---

## 常见陷阱

1. **daily_summary.json 不存在** → 22:00 复盘应在 21:50 之后启动，如果确实没有，标记全部 estimate:true 并写入异常
2. **KPI 文件已存在** → 跳过写入，只读取引用。同一个 Cron 不要重复写入
3. **Obsidian vault 不可用** → iCloud 路径可能被锁定，先 check 路径存在性
4. **数据精度问题** → 除非有精确 token 统计，否则永远标记 estimate:true
5. **平台覆盖计数** → `platform_count` 是独立平台数（小红书=1，小红书+抖音=2），不是内容数
6. **名义 vs 实际路径** → Obsidian 路径全角符号 `｜` 在 shell 中需正确转义，Python 中直接使用
