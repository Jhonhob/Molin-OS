# 墨测数据 · 数据源发现指引

> 目的：当 Agent 未写入 relay/kpi/ JSON 时，提供 Agent 级的数据发现路径和估算方法。
> 适用范围：daily_summary 采集、KPI 聚合、06:00 数据快照、09:00 看板刷新。

---

## 核心原则

1. **relay/kpi/{agent}_{date}.json 是首选数据源** — 存在则直接读取，无需推测
2. **缺失时不要跳过该 Agent** — 用 Obsidian 产出/成果/ 文件推断 activity 并标记 `estimate: true`
3. **不可虚构指标** — 无产出即无数据，保持 `kpi_available: false`
4. **所有 estimate 数据必须在 meta.estimate_fields 中列明**

---

## Agent 级数据发现路径

### 墨笔文创 (content_writer)

| 路径 | 文件模式 | 发现方法 |
|------|---------|---------|
| `成果/银月｜*.md` | `银月｜小红书.md`, `银月｜墨麟OS.md`, `银月｜Replying.md` | `find .../成果/ -name '银月*' -newermt {date}` |
| `产出/银月｜*.md` | 日志型产出（日报等） | `find .../产出/ -name '银月*' -newermt {date}` |
| `relay/kpi/content_writer_{date}.json` | 标准 KPI JSON | 存在则直接使用 |

**当 relay/kpi 缺失时估算**：
- 根据成果/ 和产出/ 文件数估 task_count
- platform_count：观察文件名关键词（小红书/公众号/B站/抖音）去重计数
- avg_qa_score：无精确值取 80（典型工作日）或 75（周末），标记 estimate
- api_cost：task_count × ¥0.55（工作日常规 ¥3.31/5.85 = ¥0.56/task）

### 元瑶教育 (education)

| 路径 | 文件模式 | 发现方法 |
|------|---------|---------|
| `产出/元瑶｜*.md` | `元瑶｜memory_*.md`, `元瑶｜对话记录.md`, `元瑶｜学员记忆方案.md` | `find .../产出/ -name '元瑶*' -newermt {date}` |
| `产出/元瑶｜Phase*.md` | Phase 进展文档 | `find .../产出/ -name '元瑶｜Phase*'` |
| `学习档案/元瑶｜*.md` | 学习吸收产出 | `find .../学习档案/ -name '元瑶*' -newermt {date}` |
| `学习档案/银月｜*.md` | 与教育相关的共享学习产出 | `find .../学习档案/ -name '银月*' -newermt {date}` |
| `报告/元瑶｜*.md` | 元瑶报告 | `find .../报告/ -name '元瑶*' -newermt {date}` |

**估算规则**：
- output_count = 产出/ 文件数 + 学习档案/ 相关文件数
- key_deliverables = 读取每个文件 frontmatter 的 description/title 或 head -n 10 提取
- 无量化 KPI（task_count/success_rate/qa）→ 标记 kpi_available: false
- 可描述 today_summary 而不填效率/质量/成本数据

### 墨商BD (宋玉)

| 路径 | 文件模式 |
|------|---------|
| `产出/宋玉｜Boss直聘简报.md` | 招聘情报摘要 |
| `产出/宋玉｜回复记录.md` | 沟通过程 |
| `成果/宋玉｜*.md` | 横向成果 |

**估算规则**：
- output_count = 当日产出文件数
- 无量化 KPI → kpi_available: false

### 墨链电商 (ecommerce)

| 路径 | 文件模式 | 说明 |
|------|---------|------|
| `relay/side/orders.json` | orders JSON | last_updated 字段判定时效性 |
| `relay/side/daily_status.json` | 日状态 | period 字段确认日期 |
| `relay/side/leads.json` | 线索 | 同上 |
| `relay/side/messages_inbox.json` | 消息 | 同上 |
| `relay/side/price_strategy.json` | 定价策略 | 周级更新 |

**估值规则**：
- 优先检查 orders.json 的 last_updated：
  - 如果 last_updated >= {date} → 数据有效，直接读取
  - 如果 last_updated < {date} → 标记 status: idle，注"最新数据来自 {date}"
- orders.total = 0 且 leads.total = 0 → status: idle
- orders.total > 0 → status: active

### 墨算财务 (finance)

| 路径 | 文件模式 |
|------|---------|
| `relay/finance_daily_{date}.json` | 财务日报 |

**估值规则**：
- finance_daily 是最可靠的跨线成本估算源（由独立 cron 生成）
- 读取 cost.api.today_estimate、revenue.total、monthly_used
- 如果 finance_daily 不存在 → 用 content_writer 的 api_cost + 推算其他线
- 利润 = 0（投入期）= ¥0 收入

### 玄骨研究 (research)

| 路径 | 文件模式 |
|------|---------|
| `产出/玄骨｜*.md` | 情报产出、简报 |
| `relay/shared/daily_intel.json` | 共享情报 |

**估值规则**：
- 检查 daily_intel.json 的 date 字段是否匹配当日
- output_count = 当日产出/ 文件数 + 1（daily_intel）
- 无量化 KPI

### 墨图设计 (designer)、墨播短视频 (short_video) 等其余 Agent

当前状态：**无 relay/kpi/ 文件，无 Obsidian 产出规律可循**。
→ 在 cross_business_anomalies.kpi_coverage.affected_agents 中列名，mark 缺失

---

## 时间判断

```python
today = "2026-05-18"
# 查找今日文件:
find_cmd = f"find {OBSIDIAN_VAULT}/产出/ -name '银月*' -newermt '{today}'"
find_cmd = f"find {OBSIDIAN_VAULT}/产出/ -name '元瑶*' -newermt '{today}'"
find_cmd = f"find {OBSIDIAN_VAULT}/学习档案/ -name '元瑶*' -newermt '{today}'"
```

注意：Obsidian 文件的 `-newermt` 过滤使用文件的 mtime，与 date 字符串格式一致。

---

## 数据源发现决定树

```
relay/kpi/{agent}_{date}.json 存在？
  ├─ 是 → 直接读取（无需估算）
  └─ 否 → 按 Agent 从 Obsidian 查找文件：
          ├─ 有文件 → 按上表规则估算，标记 estimate: true
          └─ 无文件 → 标记 kpi_available: false, status: idle/nodata
```

---

## Obisidian Vault 路径

```
/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents
```

平坦结构，8 个根目录：报告/ 产出/ 成果/ 学习档案/ 技能库/ 系统/ 模板/ 日记/
