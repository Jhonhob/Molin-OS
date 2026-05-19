# Vault Naming Convention (Established 2026-05-17)

## Core Rule

All vault top-level directory names must be **clean Chinese characters only**. No English, no numbered prefixes, no mixed-language names.

## Acceptable Directory Names

| Directory | Purpose | Established |
|-----------|---------|-------------|
| 决策/ | Irreversible decisions (architecture, strategy) | v5.3 |
| 知识/ | Knowledge accumulation (research, analysis, models) | v5.3 |
| 流程/ | Executable SOPs, configurations, checklists | v5.3 |
| 成果/ | Deliverables, reports, outputs | v5.3 |
| 报告/ | Daily aggregated reports | v5.3 |
| 配置/ | System architecture metadata | v5.3 |
| 产出/ | **Agent execution outputs** (8-section template) | v2.0 |
| 学习档案/ | Learning notes, GitHub deep-reads | v2.0 |
| Archive/ | Old backups (exception — English, read-only) | v5.3 |

## What to Avoid

- ❌ `02_Agent_Outputs/` — numbered prefix rejected by user
- ❌ `agent-outputs/` — English name, legacy path
- ❌ `Agents/`, `Daily/`, `System/`, `env/` — legacy from old architecture
- ❌ `MolinOS-Wiki/` — symlink resolved to iCloud path

## Correction Pattern

When a tool or script creates a directory with the wrong name:

1. Copy contents to correct-name directory via `cp` (never `mv` — user blocks it)
2. Update the script that created it (hardcoded path)
3. Delete the wrong-named directory
4. Run `vault_health_check.py` to verify

## Origin

User corrected `02_Agent_Outputs/` (created during v2.0 migration) with:
> "你觉得现在的根目录规范吗，突然冒出一个02-agent-outputs"
> "文件要整理啊，这么傻呢"

The name was clearly wrong in retrospect — all other dirs are concise Chinese without numbering.
