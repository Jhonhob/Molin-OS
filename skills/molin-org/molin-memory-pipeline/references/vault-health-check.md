# Vault Health Check — Root-Level Rogue Directory Diagnosis

## Symptom

Root-level directories like `银月/`, `agent-outputs/`, or any name that isn't `Agents`, `Daily`, or `System` appear in the vault root.

## Root Cause

`~/MolinOS-Wiki` is a symlink pointing to the vault root:
```
~/MolinOS-Wiki → /Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents/
```

When an agent or script writes to `~/MolinOS-Wiki/银月/`, the file lands at the vault root.

## Fix Procedure

When `银月/` appears at vault root:

1. **Identify source** — Check the file content for clues about which session or script created it
   ```bash
   head -20 Vault/银月/*.md
   ```

2. **Categorize** — Determine which new 4-category folder it belongs in:
   - Project-related → `Agents/media/项目/`
   - Knowledge/architecture → `Agents/media/知识库/`
   - Report/output → `Agents/media/产出/`
   - Conversation → `Agents/media/对话记录/`

3. **Move file** — Create target dir if needed, copy file, verify
   ```bash
   mkdir -p "Vault/Agents/media/知识库/"
   cp "Vault/银月/file.md" "Vault/Agents/media/知识库/file.md"
   ```

4. **Archive root directory**
   ```bash
   mv "Vault/银月" "Vault/Agents/media/.archives-v2/"
   ```

5. **Check memory for hardcoded paths**
   ```bash
   grep -r "MolinOS-Wiki/银月\|银月/" ~/.hermes/profiles/media/memories/ 2>/dev/null
   ```

## Prevention

- The `obsidian` skill's SKILL.md has a `⚠️ CRITICAL` section forbidding root-level agent dirs
- Before writing any file, construct the path as: `Vault/Agents/<agent_id>/<category>/<topic>.md`
- Never use `~/MolinOS-Wiki/<agent_name>/` as the base path

## Past Incidents

| Date | File | Cause | Fix |
|------|------|-------|-----|
| 2026-05-15 | 银月/小红书发布分发层-20260515.md | Agent session wrote to ~/MolinOS-Wiki/银月/ | Moved to Agents/media/知识库/小红书适配器方案.md |
| 2026-05-15 | 银月/ (17 files: adapters, scripts, relay) | ObsidianWiki merge → root-level dir | Classified to Agents/media/ + ~/Molin-OS/scripts/ |
