# Molin-OS 子公司 ⇄ SOP 技能映射表

创建新 Agent SOP 时，参考此表确定命名约定和已有模式。

## 完整映射

| VP | 子公司 | Worker 文件 | SOP 技能 | 六件套状态 |
|----|--------|------------|----------|-----------|
| 营销 | 墨笔文创 | content_writer.py | content-sop-pack, content-sop-lead, content-sop-growth, content-sop-crisis | ✅ 齐全（+gatekeeper） |
| 营销 | 墨韵IP | ip_manager.py | ip-sop-pack | ✅ Base |
| 营销 | 墨图设计 | designer.py | design-sop-pack | ✅ Base + prompts |
| 营销 | 墨播短视频 | short_video.py | video-sop-pack | ✅ Base |
| 营销 | 墨声配音 | voice_actor.py | voice-sop-pack | ✅ Base |
| 运营 | 墨域私域 | crm.py | crm-sop-pack（蓝图，待激活） | 🚧 需 LINE 基建 |
| 运营 | 墨声客服 | customer_service.py | service-sop-pack | ✅ Base + 话术库 |
| 运营 | 墨链电商 | ecommerce.py | ecommerce-sop-pack | ✅ Base |
| 运营 | 墨学教育 | education.py | education-sop-pack | ✅ Base |
| 技术 | 墨码开发 | developer.py | developer-sop-pack | ✅ Base |
| 技术 | 墨维运维 | ops.py | ops-sop-pack | ✅ Base |
| 技术 | 墨安安全 | security.py | security-sop-pack | ✅ Base |
| 技术 | 墨梦AutoDream | auto_dream.py | autodream-sop-pack | ✅ Base |
| 财务 | 墨算财务 | finance.py | finance-sop-pack | ✅ Base |
| 战略 | 墨商BD | bd.py | bd-sop-pack | ✅ Base |
| 战略 | 墨海出海 | global_marketing.py | global-marketing-sop-pack | ✅ Base |
| 战略 | 墨研竞情 | research.py | research-sop-pack | ✅ Base |
| 共同服务 | 墨律法务 | legal.py | legal-sop-pack | ✅ Base |
| 共同服务 | 墨脑知识 | knowledge.py | （由 memory 系统 + kpi-tracker 覆盖） | ✅ 间接覆盖 |
| 共同服务 | 墨测数据 | data_analyst.py | data-sop-pack | ✅ Base |

## 跨 Agent 共享技能

| 技能 | 用途 | 所有 Agent |
|------|------|-----------|
| gatekeeper-sop | 全流量合规门禁 + QA 终检 | 所有对外输出 Agent |
| kpi-tracker | KPI 数据采集标准 | 复盘 Cron |
| kpi-dashboard | 看板可视化生成 | 复盘 Cron + 手动调用 |

## SOP 命名约定

```
{agent-domain}-sop-pack         → 基础包（Execution + QA + Escalation 三合一）
{agent-domain}-sop-{type}       → 单类型补充（lead / growth / crisis）
gatekeeper-sop                  → 共享门禁
kpi-tracker                     → 共享 KPI
kpi-dashboard                   → 共享看板
agent-sop-template              → 元模板
```

`-pack` 后缀代表该技能包含 Execution + QA + Escalation 三件套。
单类型文件（-lead, -growth, -crisis）是 -pack 的补充扩展。

## Cron-SOP 集成

| Cron | 挂载技能 | 数据流向 |
|------|----------|----------|
| 22:00 复盘 + KPI | content-sop-pack + gatekeeper + kpi-tracker | relay/kpi/ → Obsidian |
| 22:10 看板 | (no_agent) generate_dashboard.py | relay/kpi/ → Obsidian 看板 |
| 23:00 财务日报 | finance-sop-pack + kpi-tracker | relay/kpi/ → Obsidian 日报 |
| 周日 21:00 增长 | kpi-tracker + content-sop-growth + pack | relay/kpi/ → AB实验 → SOP patch |
| 15/45分 客服 | service-sop-pack | 闲鱼 → 回复 |
