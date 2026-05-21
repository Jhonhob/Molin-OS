# Cron-SOP Integration Pattern

## 概述

Molin-OS 原生 `cronjob` 工具支持通过 `skills` 参数加载 SOP 技能。这让定时任务不再只是"执行一段 prompt"，而是**在 SOP 框架内运行**——执行步骤由 Execution SOP 定义，质量由 QA SOP 把关，异常由 Escalation SOP 处理。

## 模式结构

```
cronjob(create)
 ├── skills=[content-sop-pack, gatekeeper-sop]  ← 加载 SOP 技能
 ├── prompt: """
 │     1. 加载的 SOP 技能定义了执行框架
 │     2. Prompt 自标识所处的 Layer（如 Feedback Layer）
 │     3. 内容产出写入 relay/ + Obsidian
 │     4. 执行后写入 relay 标记供下游 Agent 使用
 │   """
 └── schedule: "0 22 * * *"  ← Cron 经营节奏
```

## 关键原则

### 1. SOP 技能作为执行框架，Prompt 作为具体任务

```
❌ 错误：把所有 SOP 规则写死在 prompt 里
✅ 正确：SOP 规则放在 skill 文件中，prompt 只写"执行本技能定义的复盘流程"
```

### 2. 每层 Cron 必须自标识

Cron prompt 开头应当声明它属于哪个 Layer：

```
你是墨麟AI集团的{Agent名称}复盘 Agent（Feedback Layer）
```

可选 Layer 标识：
- **Intel Layer** — 情报采集
- **Planning Layer** — 选题/排期
- **Execution Layer** — 内容生产（含自检）
- **Gatekeeper Layer** — 质量终检
- **Distribution Layer** — 平台分发
- **Feedback Layer** — 复盘优化

### 3. 数据回环铁律

每个 Cron 执行必须以写入 relay/ 或 Obsidian 为结尾，供下游 Agent 引用：

```
执行 → 产出 → 写入 relay/{layer}_{date}.json → 数据回馈下一轮
```

### 4. 挂载多个 SOP 技能时的执行顺序

如果 Cron 加载了多个技能（如 `content-sop-pack` + `gatekeeper-sop`），执行顺序为：

1. **Execution SOP**（content-sop-pack 的 7 步流水线）
2. **QA SOP**（content-sop-pack 的自检评分）
3. **Gatekeeper SOP**（gatekeeper-sop 的终检决策树）
4. **Escalation SOP**（content-sop-pack + gatekeeper-sop 的异常触发条件）

Prompt 只需要描述"做什么"，"怎么做"从 SOP 技能中获取。

## 实战示例

### 内容复盘 Cron（已部署）
### 内容复盘 Cron（已部署）

```python
job = cronjob(
    action='create',
    name='内容 Agent 每日复盘 22:00',
    schedule='0 22 * * *',        # 每晚 22:00
    skills=['content-sop-pack', 'gatekeeper-sop', 'kpi-tracker'],  # 挂载3个SOP技能
    prompt="""
        你是内容经营复盘 Agent（Feedback Layer + KPI Layer）。

        Step 1: 搜索 relay/ 和 Obsidian 的今日内容产出
        Step 2: 对照 content-sop-pack 的 QA SOP 做趋势分析
        Step 3: 按 kpi-tracker 格式写入 KPI 数据 → relay/kpi/{agent}_{date}.json
        Step 4: 检查异常事件（飞轮断裂、成本异常等）
        Step 5: 生成复盘笔记 → 写入 Obsidian Agents/内容Agent/复盘/{date}.md
        Step 6: 写入 relay/daily_review_{date}.json
    """
)
```

多个技能按层顺序执行：Execution → QA → KPI采集 → Gatekeeper终检。

### 内容生产 Cron（规划中）

```python
content_cron = cronjob(
    action='create',
    name='内容工厂 09:00',
    schedule='0 9 * * *',
    skills=['content-sop-pack', 'gatekeeper-sop'],
    prompt="""
        你是内容工厂 Agent（Execution + Gatekeeper Layer）。

        Step 1: 从 relay/intel_{date}.json 读取今日选题
        Step 2: 按 content-sop-pack Execution SOP 执行7步流水线
        Step 3: 自检评分（QA SOP 7维矩阵）
        Step 4: 通过 gatekeeper-sop 终检
        Step 5: 产出 → relay/{platform}_content_{date}.md
        Step 6: 写入 Obsidian 内容排期表
    """
)
```

## 与独立 Python 调度器的对比

| 方案 | Molin-OS cronjob + SOP skills | 独立 scheduler_jobs.py |
|------|-------------------------------|------------------------|
| 任务定义 | 系统内 Heremes cron，生命周期由 Hermes 管理 | 独立进程，挂了全停 |
| SOP 嵌入 | 原生支持（skills 参数加载） | 硬编码在脚本里 |
| 数据回环 | relay/ 目录自动承接 | 需自行实现文件队列 |
| 异常处理 | Escalation SOP 自动触发飞书告警 | 需自行实现告警逻辑 |
## 已有 Cron-SOP 集成

| Cron | 挂载技能 | Layer | 状态 |
|------|----------|-------|------|
| 内容复盘 + KPI 22:00 | content-sop-pack, gatekeeper-sop, kpi-tracker | Feedback + KPI | ✅ 已激活 |
| KPI 看板生成 22:10 | (no_agent script: generate_dashboard.py daily) | Visualization | ✅ 已激活 |
| 财务日报 23:00 | finance-sop-pack, kpi-tracker | Finance KPI | ✅ 已激活 |
| 周日增长实验 21:00 | kpi-tracker, content-sop-growth, content-sop-pack | Growth Layer | ✅ 已激活 |
| 闲鱼客服 15/45分 | service-sop-pack | Execution | ✅ 已激活 |
| 梅凝每日学习 08:00 | (无) | Learning | ✅ 已激活 |
| 情报扫描 07:00 | (no_agent script) | Intel | ✅ 已激活 |

## KPI 数据流水线示例（多层 Cron 串联）

```
22:00 复盘 → relay/kpi/{agent}_{date}.json
                     ↓
22:10 看板 → 写入 Obsidian Agents/KPI看板/  (no_agent script)
                     ↓
23:00 财务 → 消费 relay/kpi/ 生成财务日报
```

## 参考

- SOP 元模板：`skill_view('agent-sop-template')`
- 内容 SOP：`skill_view('content-sop-pack')`
- 门禁 SOP：`skill_view('gatekeeper-sop')`
- KPI 追踪：`skill_view('kpi-tracker')`
- KPI 看板：`skill_view('kpi-dashboard')`
- 现有 Cron 清单：`cronjob(action='list')`
- cronjob 文档：`skill_view('hermes-agent')` → Cron (scheduled jobs) 章节
