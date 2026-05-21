# Cron Job Audit Checklist

## Current State Template

| # | Job Name | Type | Schedule | Last Run | Status |
|---|----------|------|----------|----------|--------|
| 1 | example | LLM/no_agent | `0 8 * * *` | 2026-05-16 | ✅ ok / ❌ error / ⏳ never |

## Verification Steps Per Job

### LLM-driven jobs (have prompt, use agent reasoning)

1. Read the prompt — does it include Obsidian sync steps?
2. Check `deliver` setting — `local` for internal, `origin` for user-facing
3. Verify output classification: 决策/知识/流程/配置/报告?
4. If missing sync, add file-write steps to the prompt

### no_agent script jobs (script-only, raw output)

1. Run the script manually: `bash <script_path>` or `python3 <script_path>`
2. Check exit code and output content
3. Verify the relay output file exists at expected path
4. Run `relay_to_obsidian.py` to confirm it picks up the new file
5. Check that the Obsidian living doc was created/updated

### Error jobs

1. Read the log file: `cat ~/.hermes/logs/<job-log>.log`
2. Check script syntax: `bash -n <script.sh>` or `python3 -m py_compile <script.py>`
3. Check Python version mismatch: `python3 --version` vs script syntax
4. Check PATH: cron runs with `/usr/bin:/bin` only
5. Fix → update script, re-run to verify

### Never-run jobs

1. Run manually to verify the script/prompt works
2. Check that no dependencies are missing
3. Confirm the timezone is correct (Asia/Shanghai for 墨麟OS)

## Classification Table

| Category | Vault Directory | Example Jobs |
|----------|----------------|--------------|
| 流程 (Process) | `流程/` | sync pipeline, git backup, cross-request polling |
| 知识 (Knowledge) | `知识/` | arxiv papers, price monitor, GitHub learning |
| 配置 (Config) | `配置/` | vault compliance, system audit |
| 报告 (Report) | `报告/` | daily aggregations |

## Sync Mechanism by Job Type

| Job Type | Sync Method | Key File |
|----------|-------------|----------|
| LLM-driven (has prompt) | Direct-write in cron prompt | prompt text includes file write |
| no_agent (script) | relay_to_obsidian.py (pipeline Step 4) | relay/ → Obsidian `知识/每日·*.md` |
| Error/status | Manual or status doc | `配置/Cron·Jobs运行状态.md` |

## Common Fixes Quick Reference

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `TypeError: unsupported operand type(s) for |` | Python 3.9 union syntax | `dict \| None` → `dict` or `Optional[dict]` |
| `! [rejected] (fetch first)` | Remote has newer commits | `git fetch origin main && git rebase origin/main` |
| exit 127 / command not found | Cron PATH doesn't include homebrew | Use absolute paths: `/opt/homebrew/bin/python3.11` |
| Works in terminal, fails in cron | PATH mismatch or shebang issue | Add `PATH="/opt/homebrew/bin:$PATH"` in script |
