# Vault Path Map — V5.3 (2026-05-16)

Authoritative mapping of scripts → vault directories.
Use this to audit and fix vault structure drift.

## Vault Structure

```
Vault/ (~/MolinOS-Wiki/ 或 iCloud)
├── 决策/     ← irreversible choices (技术选型/架构定稿/战略)
├── 知识/     ← learning + deliverables (研究/报告/日报)
├── 流程/     ← executable steps (SOP/配置/操作手册)
├── 配置/     ← system architecture + agent profiles + memory map
├── 报告/     ← aggregated daily reports
├── Archive/  ← read-only old backups
└── .obsidian/
```

**Forbidden at root:** `Agents/`, `System/`, `Daily/`, `env/`, `docs/`, `scripts/`, `skills/`, `tools/`, `molib/`, `Makefile`, `README.md`

## Script → Directory Mapping

### sync_memory.py (v5.1)
- **Line 14-17**: VAULT path
- **Line 409**: `VAULT / category` — correct: 决策|知识|流程|成果
- **Old (v5.2):** `VAULT / "Agents" / agent_id / category` ❌
- **Fix date:** 2026-05-16

### obsidian_sync.py (v4)
- **Line 22-24**: VAULT path
- **Line 253**: `VAULT / category` — correct: 决策|知识|流程|成果
- **Line 289**: `VAULT / "报告"` — correct: aggregated daily files
- **Old (v5.2):** `VAULT / "Agents" / agent_id / category` ❌ + `VAULT / "Daily"` ❌
- **Fix date:** 2026-05-16

### collect_architecture.py (v5)
- **Line 21-26**: VAULT path
- **Line 190**: `VAULT / "配置"` — correct
- **Line 268**: writes `配置/architecture.md`
- **Line 274**: writes `配置/agents/<agent>.md`
- **Line 371**: writes `配置/memory-map.md`
- **Old (v5.2):** `VAULT / "System"` ❌
- **Fix date:** 2026-05-16

## Audit Command

```bash
VAULT="/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents"

# 1. Check forbidden dirs
for d in Agents System Daily env; do
  test -d "$VAULT/$d" && echo "⚠️ ROGUE: $d/"
done

# 2. Check unexpected top-level dirs
echo "=== All top-level dirs ==="
ls -d "$VAULT"/*/ 2>/dev/null

# 3. Verify script targets
echo "=== Script VAULT targets ==="
grep -n 'VAULT /' ~/Molin-OS/scripts/sync_memory.py | grep -v "os.environ\|HOME\|\"OBSIDIAN_VAULT\""
grep -n 'VAULT /' ~/Molin-OS/scripts/obsidian_sync.py | grep -v "os.environ\|HOME\|\"OBSIDIAN_VAULT\""
grep -n 'VAULT /' ~/Molin-OS/scripts/collect_architecture.py | grep -v "os.environ\|HOME\|\"OBSIDIAN_VAULT\""
```

## History

| Date | Change | Who |
|------|--------|-----|
| 2026-05-16 | Initial v5.3: 3 scripts repathed, vault structure standardized to 5 flat dirs | Hermes Agent |
