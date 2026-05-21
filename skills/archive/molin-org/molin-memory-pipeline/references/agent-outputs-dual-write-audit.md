# agent-outputs/ Dual-Write Source Audit (2026-05-17)

## Summary

After fixing pipeline scripts, `agent-outputs/` kept reappearing at vault root. Root cause: **agent-profile skills and scripts still hardcode `agent-outputs/` as their write target**. Because `~/MolinOS-Wiki` is a symlink to the iCloud vault, any `cp` or `write_file` targeting `MolinOS-Wiki/agent-outputs/` recreates the rogue directory.

## Symlink Bridge

```bash
MolinOS-Wiki -> ~/Library/Mobile Documents/iCloud~md~obsidian/Documents
```

## All 21 Write Sources

### Profile: edu (9 sources)
| # | File | Line(s) | Old → New |
|---|------|---------|-----------|
| 1 | `skills/workflow/edu-operations-pipeline/SKILL.md` | 221 | `agent-outputs/edu/curriculum/` → `产出/edu/` |
| 2 | `skills/.../growth-strategy-upgrade-pattern.md` | 85,114 | `agent-outputs/edu/curriculum/` → `产出/edu/` |
| 3 | `skills/workflow/edu-github-trend-research/SKILL.md` | 159,171,204 | `agent-outputs/edu/memory/` → `产出/edu/` |
| 4 | `skills/.../memory-automation-rules.md` | 50 | `agent-outputs/edu/memory/` → `产出/edu/memory/` |
| 5 | `memories/MEMORY.md` | 3 | `agent-outputs/edu/memory/` → `产出/edu/` |
| 6 | `plans/student_memory_mvp_v1.md` | 43 | `agent-outputs/` → `产出/` |
| 7 | `scripts/sync_memory.py` | 26 | `agent-outputs/edu/memory` → `产出/edu` |
| 8 | `scripts/sync_growth_full.py` | 15 | `agent-outputs/edu/memory` → `产出/edu` |

### Profile: shared (3 sources)
| # | File | Line(s) | Old → New |
|---|------|---------|-----------|
| 9 | `skills/research/intelligence-automation/SKILL.md` | 50,211 | `agent-outputs/shared/` → `产出/shared/` |
| 10 | `bin/memory_sync.py` | 13,74 | `agent-outputs/shared` → `产出/shared` |

### Profile: side (7 sources)
| # | File | Line(s) | Old → New |
|---|------|---------|-----------|
| 11 | `skills/xianyu-automation-v2/SKILL.md` | 101 | `agent-outputs/side/` → `产出/side/` |
| 12 | `skills/side-research-pipeline/SKILL.md` | 270 | local dir (不影响vault) |
| 13 | `skills/knowledge-management-agent/SKILL.md` | 82 | `agent-outputs/side/` → `产出/side/` |
| 14 | `memories/MEMORY.md` | 9 | `agent-outputs/side/` → `产出/side/` |
| 15 | `scripts/memory_sync.py` | 5,22,96,141 | `agent-outputs/side/` → `产出/side/` |

### Molin-OS shared (3 sources)
| # | File | Line(s) | Old → New |
|---|------|---------|-----------|
| 16 | `tools/memory_bridge.py` | 164 | `agent-outputs/{p}/` → `产出/{p}/` |
| 17 | `skills/obsidian-wiki-reader/SKILL.md` | 9 | `agent-outputs/{p}/` → `产出/{p}/` |
| 18 | `skills/xianyu-automation/SKILL.md` | 63 | `agent-outputs/side/` → `产出/side/` |

All files searched via `MolinOS-Wiki` → found 2 more references that `agent-outputs` alone missed.

### Follow-up pass: MolinOS-Wiki full path (2026-05-17, session 20260517_225720_052569)

**2 missed sources found** — used `MolinOS-Wiki/agent-outputs/` (full symlink path) instead of bare `agent-outputs/`:

| # | File | Line(s) | Old → New |
|---|------|---------|-----------|
| 19 | `edu/skills/workflow/edu-operations-pipeline/SKILL.md` | 291 | `MolinOS-Wiki/agent-outputs/edu/curriculum/` → `产出/edu/` |
| 20 | `edu/skills/.../references/ai-agent-engineering-patterns.md` | 190 | `MolinOS-Wiki/agent-outputs/edu/curriculum/` → `产出/edu/` |

## Audit Command (updated)

```bash
# Search both bare path AND full symlink path
for pattern in 'agent-outputs' 'MolinOS-Wiki'; do
  grep -rn "$pattern" ~/.hermes/profiles/{edu,shared,side}/skills/ \
    ~/.hermes/profiles/{edu,shared,side}/memories/ \
    ~/.hermes/profiles/{edu,shared,side}/scripts/ \
    ~/.hermes/profiles/{edu,shared,side}/plans/ \
    ~/Molin-OS/tools/ ~/Molin-OS/skills/ \
    | grep -v 'cron/output' | grep -v 'sessions/' \
    | grep -v 'iCloud 幽灵' | grep -v '已废弃' | grep -v 'agent-outputs-dual'
done
```

**⚠️ Also search `references/` files inside skills.** The audit above only scans `SKILL.md` files, but `references/<topic>.md` files can also contain old path references. Extend the search to `references/*.md` in each skill directory.

## Prevention: Three-Layer Audit

When fixing vault structure drift, always audit **three layers**:
1. **Pipeline scripts** (`~/Molin-OS/scripts/`, `~/Molin-OS/molib/`)
2. **Molin-OS shared tools/skills** (`~/Molin-OS/tools/`, `~/Molin-OS/skills/`)
3. **Agent-profile instructions** (`~/.hermes/profiles/{X}/skills/`, `memories/`, `scripts/`, `plans/`)

Fixing only layer 1 leaves layers 2 and 3 as silent recurrence vectors.
