# 墨麟 OS · Cron 作业一览

> 最后更新: 2026-05-19
> 数据来源: `hermes cron list`
> 共计: 19 个活跃作业

## 作业清单

| # | job_id | 名称 | 调度 (cron) | 类型 | 脚本 / Skills | 上次状态 |
|---|--------|------|-------------|------|--------------|---------|
| 1 | `210cba244f36` | Molin-OS 记忆同步 — 每小时 | `0 * * * *` | Script | `molin-sync-all.sh` | error (exit 1) |
| 2 | `5cd81602c531` | Molin-OS 每日 Git 备份 02:00 | `0 2 * * *` | Script | `git-backup.sh` | ok |
| 3 | `61cc88accaa9` | vault-compliance-weekly | `0 9 * * 1` | (默认) | workdir: Obsidian vault | ok |
| 4 | `9dd66fafeb6d` | arxiv 每日论文扫描 | `0 7 * * *` | Script | `daily_arxiv_scan.sh` | ok |
| 5 | `d1e92fbc6c8d` | 副业每日价格监控 | `30 9 * * *` | Script | `daily_side_price_monitor.sh` | ok |
| 6 | `bad81fa1d323` | 跨线请求轮询（每15分钟） | `*/15 * * * *` | Script | `cross_request_worker.py` | ok |
| 7 | `a169caa8c9ac` | 梅凝每日GitHub学习 | `0 8 * * *` | Agent | (prompt-based) | ok |
| 8 | `05ee5848f9f4` | 内容 Agent 每日复盘 22:00 | `0 22 * * *` | Agent-Skills | `content-sop-pack`, `gatekeeper-sop`, `kpi-tracker` | ok |
| 9 | `5c7c2cfe6103` | 内容 Agent 周日增长复盘 21:00 | `0 21 * * 0` | Agent-Skills | `kpi-tracker`, `content-sop-growth`, `content-sop-pack` | ok |
| 10 | `55a2385d955a` | 财务日报 23:00 | `0 23 * * *` | Agent-Skills | `finance-sop-pack`, `kpi-tracker` | ok |
| 11 | `e25fcf710cf0` | KPI看板生成 22:10 | `10 22 * * *` | Script | `generate_dashboard.py daily` | error (script not found) |
| 12 | `a22276b31c18` | 月度规划生成 — 1号 09:00 | `0 9 1 * *` | Agent-Skills | `kpi-tracker`, `finance-sop-pack` | (从未运行) |
| 13 | `ef1b8c26ce5c` | 垂直学习扫描 — 五大Agent | `0 6 * * 1` | Agent-Skills | `vertical-learning-sop` | blocked (威胁模式) |
| 14 | `712178799998` | 墨安安全 — 主动审计 周一03:00 | `0 3 * * 1` | Agent-Skills | `security-sop-pack` | ok |
| 15 | `e4a86b802135` | AutoDream精读内化与SKILL更新 | `0 7 * * 1` | Agent-Skills | `vertical-learning-sop`, `obsidian`, `github` | blocked (威胁模式) |
| 16 | `614f6c663f11` | 每日KPI采集 21:50 | `50 21 * * *` | Agent-Skills | `kpi-tracker`, `data-sop-pack` | ok |
| 17 | `ca23aefea523` | 每日复盘与明日规划 22:30 | `30 22 * * *` | Agent-Skills | `kpi-tracker`, `obsidian` | ok |
| 18 | `49961528a542` | 周计划生成 周一09:30 | `30 9 * * 1` | Agent-Skills | `obsidian`, `kpi-tracker` | ok |
| 19 | `b896895087fb` | 记忆蒸馏与质量门控 周日21:30 | `30 21 * * 0` | Agent-Skills | `obsidian`, `vertical-learning-sop` | blocked (威胁模式) |

## 问题作业

以下作业状态异常，需排查：

### error — 脚本退出码非零
- **210cba244f36** (记忆同步): Python `collect_architecture.py` 第 527 行 `AttributeError: 'int' object has no attribute 'items'`
- **e25fcf710cf0** (KPI看板): `generate_dashboard.py daily` 在 `~/.hermes/scripts/` 中找不到

### blocked — 安全护栏拦截
- **ef1b8c26ce5c** (垂直学习扫描): 触发威胁模式 `exfil_curl_url`
- **e4a86b802135** (AutoDream精读): 触发威胁模式 `exfil_curl_url`
- **b896895087fb** (记忆蒸馏): 触发威胁模式 `exfil_curl_url`

## 飞轮管线（内容自动化链）

| 棒次 | 时间 | 作业 | 说明 |
|------|------|------|------|
| 第一棒 🕐 08:00 | 情报银行 | 向 `relay/intelligencemorning.json` 写入情报 |
| 第二棒 🕐 09:20 | 内容工厂 | 消费上游文件 → 生成内容 → 写入 relay/ |
| 第三棒 🕐 10:45 | 增长引擎 | SEO 优化 + 审计 + 追踪 |

飞轮接力规则：每棒必须检查上游文件是否存在且 < 90 分钟，否则发 T4 飞书告警。

## 部署指南

首次部署或迁移时，使用 `hermes cron create` 逐一注册以上作业。
