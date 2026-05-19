# iCloud Ghost Directory Handling

When deleting files/directories inside the iCloud-synced Obsidian vault, iCloud Drive may restore deleted content because it treats the deletion as a sync conflict. This produces persistent "ghost" directories that resist `rm -rf`.

## Symptoms
- `rm -rf` exits successfully but the directory immediately reappears (empty or with restored content)
- `mv` to /tmp fails with "Operation not permitted" (iCloud sandbox blocks moving out)
- `ls -la` shows the directory with 0 files but `3` entries (`.` and `..` and hidden .DS_Store)
- Running `chflags -R uchg` (user immutable) temporarily locks the directory

## Root Cause
iCloud Drive maintains its own file index. When a synced directory is deleted locally, iCloud's cloud-side copy still has the directory indexed. It restores the empty shell during the next sync cycle.

This is different from "user blocked mv" — that's a user preference to use `cp + rm` instead of `mv` for safety. iCloud ghosts are a macOS iCloud Drive behavior.

## Detection
```bash
# Test if a directory is an iCloud ghost
test -d "$VAULT/agent-outputs" && \
  find "$VAULT/agent-outputs" -type f | wc -l
# If 0 files but directory exists → likely ghost

# Compare with authoritative destination
md5 -q "$VAULT/agent-outputs/edu/curriculum/file.md" \
  "$VAULT/02_Agent_Outputs/edu/file.md"
# If MD5 matches → ghost contains stale copies, safe to ignore
```

## Resolution Strategy (tiered)

### Tier 1: Empty + Lock (quick, may not stick)
```bash
# Empty the files first, then delete
for f in /path/to/ghost/*.md; do echo "" > "$f"; done
rm -rf /path/to/ghost
```

### Tier 2: chflags lock + delete
```bash
chflags -R uchg /path/to/ghost      # lock
rm -rf /path/to/ghost                # delete
chflags -R 0 /path/to/ghost         # unlock (may fail if deleted)
```

### Tier 3: Whitelist in health check (fallback)
If iCloud persistently restores the empty directory shell:
1. Verify all files have been migrated to the correct location (MD5 checksums)
2. Delete the original files inside the ghost directory (echo "" > each)
3. Add the directory name to `ALLOWED_DIRS` in `vault_health_check.py`
4. Verify `vault_health_check.py` exits with 0 (clean)

### Tier 4: Break iCloud sync (nuclear)
```bash
# Turn off iCloud Drive sync temporarily
brctl log -w  # Watch iCloud sync activity
# Or use: sudo killall -STOP bird  (freeze iCloud sync daemon)
# Then delete the directory while sync is paused
# WARNING: This affects ALL iCloud Drive content
```

## Prevention
- Fix writing scripts to point to `02_Agent_Outputs/` instead of old paths
- After migrating files from a rogue directory, always verify with `md5` that content is intact
- Then use `echo "" > file` to empty each original file before `rm -rf`
- Run `vault_health_check.py` after each migration to confirm clean state
