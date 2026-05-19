---
created: 2026-05-16
updated: 2026-05-16
agent: global
status: 活跃
confidence: 已验证
importance: ⭐⭐⭐
source: "系统审计: 2026-05-16 17:38 + 仓库标准化: 18:00"
tags: [cron, 运维, 配置, 系统状态]
---

# Cron Jobs 运行状态

墨麟OS 共 7 个定时任务，分类维护。
主仓库: [github.com/moye-tech/Molin-OS](https://github.com/moye-tech/Molin-OS)

---

## 一、流程类（同步/备份/轮询）

### 1. Molin-OS 记忆同步 — 每小时
| 属性 | 值 |
|------|-----|
| Job ID | 210cba244f36 |
| 排程 | `0 * * * *`（每小时整点） |
| 类型 | Script (no_agent) |
| 脚本 | `~/.hermes/scripts/molin-sync-all.sh` |
| 状态 | ✅ 正常 |

**管道 4 步（v5.0）:**
1. `sync_memory.py` — 会话记忆 → 分类 → Obsidian + Supermemory
2. `obsidian_sync.py` — 报告同步到 Obsidian `报告/`
3. `collect_architecture.py` — 架构采集到 `配置/`
4. `relay_to_obsidian.py` — Relay 产出 → `知识/每日·*.md`

### 2. Molin-OS — 每日 Git 备份 02:00
| 属性 | 值 |
|------|-----|
| Job ID | 5cd81602c531 |
| 排程 | `0 2 * * *`（每日 02:00） |
| 类型 | Script (no_agent) |
| 脚本 | `~/.hermes/scripts/git-backup.sh`（v3.0） |
| 状态 | ⚠️ 已修复 ✅ |

**v3.0 变更（2026-05-16）:**
- 备份目标: MolinOS-Ultra → **Molin-OS**（主仓库）
- 移除冗余脚本复制步骤（源码已在 Molin-OS）
- 简化: `git add → commit → fetch+rebase → push`
- 远程: `github.com/moye-tech/Molin-OS.git`

### 3. 跨线请求轮询（每15分钟）
| 属性 | 值 |
|------|-----|
| Job ID | bad81fa1d323 |
| 排程 | `*/15 * * * *`（每15分钟） |
| 类型 | Script (no_agent) |
| 脚本 | `~/.hermes/scripts/cross_request_worker.py` |
| 状态 | ✅ 正常运行 |

**已修复**: Python 3.9 `dict | None` 语法错误。

---

## 二、知识类（每日学习/情报采集）

### 4. arxiv 每日论文扫描 07:00
| 属性 | 值 |
|------|-----|
| Job ID | 9dd66fafeb6d |
| 排程 | `0 7 * * *` |
| 类型 | Script (no_agent) |
| 脚本 | `~/.hermes/scripts/daily_arxiv_scan.sh` |
| 状态 | ⏳ 明日 07:00 首跑 |
| Obsidian 同步 | ✅ `知识/每日·Arxiv论文.md`（通过 relay_to_obsidian.py） |

### 5. 副业每日价格监控 09:30
| 属性 | 值 |
|------|-----|
| Job ID | d1e92fbc6c8d |
| 排程 | `30 9 * * *` |
| 类型 | Script (no_agent) |
| 脚本 | `~/.hermes/scripts/daily_side_price_monitor.sh` |
| 状态 | ⏳ 明日 09:30 首跑 |
| Obsidian 同步 | ✅ `知识/每日·副业价格监控.md`（通过 relay_to_obsidian.py） |

### 6. 梅凝每日GitHub学习 08:00
| 属性 | 值 |
|------|-----|
| Job ID | a169caa8c9ac |
| 排程 | `0 8 * * *` |
| 类型 | LLM-driven |
| 状态 | ⏳ 明日 08:00 首跑 |
| Obsidian 同步 | ✅ 内建（直接写入 `决策/梅凝·GitHub.md`） |

---

## 三、配置类（合规/审计）

### 7. vault-compliance-weekly 周一09:00
| 属性 | 值 |
|------|-----|
| Job ID | 61cc88accaa9 |
| 排程 | `0 9 * * 1`（每周一） |
| 类型 | LLM-driven |
| Workdir | Obsidian Vault 根目录 |
| 状态 | ⏳ 等待下周一 |

---

## 分类总表

| 分类 | Job | 输出目标 |
|------|-----|---------|
| 流程 | 记忆同步、Git备份、跨线轮询 | Obsidian `流程/` + Supermemory |
| 知识 | arxiv、副业价格、GitHub学习 | Obsidian `知识/` + Supermemory |
| 配置 | vault-compliance | Obsidian `配置/` + Supermemory |

## 仓库状态

| 仓库 | URL | 用途 | 状态 |
|------|-----|------|------|
| Molin-OS | github.com/moye-tech/Molin-OS | 系统主仓库（源码+技能+配置） | ✅ 标准化 v5.0, 2,689 files |
| MolinOS-Ultra | github.com/moye-tech/MolinOS-Ultra | Obsidian 笔记备份 | ⚠️ 保留中（Obsidian Git 自动备份） |

## 问题清单

1. ~~cross_request_worker.py Python 3.9 语法错误~~ ✅ 已修复
2. ~~git-backup.sh 推送被拒~~ ✅ 已修复（v3.0 改为 fetch+rebase）
3. ~~git-backup.sh 备份目标过时（MolinOS-Ultra）~~ ✅ 已修复（v3.0 → Molin-OS）
4. 🔄 arxiv 输出文本格式非 JSON —— 可优化
5. 🔄 副业价格监控无真实爬虫 —— 仅静态参考
