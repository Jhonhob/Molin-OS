# Cron Jobs Audit — 2026-05-16

Full audit of all 7 cron jobs: status check, output verification, bug fixes, and Obsidian sync setup.
Second pass (18:00): git-backup v3.0 — target changed from MolinOS-Ultra to Molin-OS.

## Jobs Overview

| # | Name | Type | Schedule | Status | 
|---|------|------|----------|--------|
| 1 | Molin-OS 记忆同步 | Script (no_agent) | Hourly | ✅ OK |
| 2 | Molin-OS 每日 Git 备份 | Script (no_agent) | 02:00 daily | ❌→✅ v3.0 |
| 3 | vault-compliance-weekly | LLM-driven | Mon 09:00 | ⏳ Not yet run |
| 4 | arxiv 每日论文扫描 | Script (no_agent) | 07:00 daily | ✅ Tested OK |
| 5 | 副业价格监控 | Script (no_agent) | 09:30 daily | ✅ Tested OK |
| 6 | 跨线请求轮询 | Script (no_agent) | Every 15min | ❌→✅ Fixed |
| 7 | 梅凝每日GitHub学习 | LLM-driven | 08:00 daily | ✅ Built-in Obsidian sync |

## Issues Found & Fixed

### Fix 1: cross_request_worker.py — Python 3.9 type syntax

**Symptoms**: Script crashed with `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`

**Root cause**: Line 63 used `dict | None` type hint — Python 3.10+ syntax. System python3 is 3.9.6.

**Fix**: Changed `-> dict | None` to `-> dict`

**Verification**: Ran `python3 cross_request_worker.py` → `📭 无待处理请求` ✅

**Lesson**: The cron script uses `#!/usr/bin/env python3` which resolves to 3.9.6. Scripts with post-3.9 syntax need either `#!/opt/homebrew/bin/python3.11` or compatible syntax.

### Fix 2: git-backup.sh — push rejected → v3.0 rewrite

**v2.1 fix (17:38)**: Split `git pull --rebase` into `git fetch origin main` + `git rebase origin/main`.

**v3.0 fix (18:00)**: Full rewrite — backup target changed from `MolinOS-Ultra` to `Molin-OS` (main system repo). Removed redundant `cp` steps (scripts were being duplicated to the vault repo). Simplified to: `git add → commit → fetch+rebase → push`.

**Why v3.0**: Molin-OS is now the canonical system repo at `github.com/moye-tech/Molin-OS.git` (2,689 files, standardized v5.0). MolinOS-Ultra is secondary (Obsidian vault only, backed by Obsidian Git plugin).

**Cron job renamed**: `MolinOS Ultra — 每日 Git 备份` → `Molin-OS 每日 Git 备份 02:00`

### Fix 3: Relay outputs not reaching Obsidian

**Symptoms**: no_agent cron jobs (arxiv, price monitor) wrote JSON/text to `relay/` directories but content never appeared in Obsidian.

**Root cause**: The sync pipeline (sync_memory.py, obsidian_sync.py, collect_architecture.py) only processes session JSONs and report files — not relay outputs from no_agent scripts.

**Fix**: Added Step 4: `relay_to_obsidian.py` to the hourly `molin-sync-all.sh` pipeline. Scans relay output dirs, parses content, writes living docs to `知识/每日·*.md`.

## New Obsidian Living Documents Created

| File | Source | Format |
|------|--------|--------|
| `知识/每日·Arxiv论文.md` | relay/shared/results/daily_papers_*.json | Pyramid: 结论→核心内容→下一步 |
| `知识/每日·副业价格监控.md` | relay/side/results/price_monitor_*.json | Pyramid: 结论→核心内容→下一步 |

Both use the `每日·` prefix naming convention for daily-updated relay-derived content.

## New Sync Artifact

**relay_to_obsidian.py** — Step 4 of the hourly sync pipeline:
- Paths scanned: `relay/shared/results/` + `relay/side/results/`
- Tracker: `~/.hermes/relay_sync_tracker.json`
- Extension: add handler functions for new relay file types

## Current Pipeline

```
sync_memory.py → obsidian_sync.py → collect_architecture.py → relay_to_obsidian.py
```

## Repository Standardization (2026-05-16 18:00)

Molin-OS repo at `github.com/moye-tech/Molin-OS` was standardized to v5.0:
- 2,689 files across standard structure (molib/, scripts/, skills/, config/, tools/, tests/)
- .gitmodules for MiroFish + last30days-skill submodules
- .github/workflows/ci.yml for automated testing
- setup.py with grouped dependencies, setup.sh with submodule init
- .gitignore v2.0 with comprehensive coverage
- 164 lines of unrelated/non-system files removed (node_modules 11MB, package.json)
