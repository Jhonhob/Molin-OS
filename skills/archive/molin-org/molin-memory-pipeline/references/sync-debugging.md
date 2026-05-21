# Sync Debugging Recipe

When memory files aren't syncing to Obsidian, follow these steps in order.

## Step 1: Check cron job status
```
cronjob(action='list')
```
Look for `last_status: "error"`. Common error: `python3.11: command not found` (exit 127).

## Step 2: Check sync tracker vs session files
```python
# Compare tracker entries with disk sessions
# Any session on disk but NOT in tracker = unsynced
```

## Step 3: Check Obsidian vault files
```
ls -la Agents/<agent>/{决策,知识,流程,成果}/
```
Verify files exist and have proper content.

## Step 4: Check Obsidian Git plugin
- Verify `.git` exists in vault root
- Verify `git remote -v` shows valid remote
- Check `data.json` for autoSaveInterval, autoPushInterval, autoBackupAfterFileChange

## Step 5: Run sync manually
```bash
bash ~/.hermes/scripts/molin-sync-all.sh
```

## Step 6: Agent-local output blind spot
If content exists in session but not in Obsidian after sync, check agent-local directories:
```bash
find ~/.hermes/profiles/<agent>/ -name "*.md" -not -path "*/sessions/*" -not -path "*/cache/*"
```
Common locations: `plans/`, `content/`, `agent-outputs/`, `relay/`, `curriculum/`

## Step 7: Vault structure compliance
Run the audit script: `python3 ~/Molin-OS/scripts/vault_compliance_check.py`
Verifies: directory classifications, file naming conventions, frontmatter integrity.

## Step 8: Obsidian Git init + remote setup
If plugin reports "not a git repository" or auth errors:

```bash
VAULT="/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents"
cd "$VAULT"

# 8a. Init git if missing
git init
git config user.email "fengye940708@gmail.com"
git config user.name "moye-tech"

# 8b. Create .gitignore
cat > .gitignore << 'EOF'
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/plugins/obsidian-git/data.json
.DS_Store
.trash/
EOF

# 8c. Initial commit
git add -A && git commit -m "vault backup: $(date '+%Y-%m-%d %H:%M:%S')"

# 8d. Set remote with token auth (GITHUB_TOKEN must be set)
git remote add origin "https://${GITHUB_TOKEN}@github.com/moye-tech/MolinOS-Ultra.git"

# 8e. Pull existing content then push
git pull origin main --allow-unrelated-histories --no-rebase
git push --set-upstream origin main
```

## Step 9: Garbage audit
Check for agent chatter as conclusions (sync_memory.py v5 bug, fixed in v5.1):
```python
# Run the garbage detection script from references/garbage-audit.md
```
If files have "Let me..." or "I'll..." as conclusions → run vault consolidation workflow.
