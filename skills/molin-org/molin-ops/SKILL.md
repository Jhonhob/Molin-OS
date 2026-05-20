---
name: molin-ops
version: "1.0.0"
description: "墨麟OS 系统运维工作流 — 状态检查、端口同步、组件更新、故障排查"
allowed-tools: Terminal, Read, ExecuteCode, CronJob
trigger-keywords:
  - 运维
  - ops
  - 系统状态
  - 端口
  - 同步
  - 更新
  - 重启
  - status
  - 维护
  - maintenance
invocation-context: "Load this skill when the user asks to check system status, sync components across profiles, update infrastructure, or run maintenance workflows"
input:
  format: |
    User requests: "<specific maintenance action>"
    Common actions: status, sync, restart, update, troubleshoot
output:
  format: |
    Status report with: running services + ports, cron job health, update availability, actionable issues
---

# 墨麟OS 系统运维 (molin-ops)

## Overview

Standard operating procedure for maintaining the Molin-OS multi-agent system. Run this workflow when the user says "记得同步各个端口，更新内容和状态" or any maintenance request.

## Maintenance Checklist

### 1️⃣ Service Status

```bash
# All gateways
hermes gateway list

# CloakServe CDP pool
curl -s http://localhost:9222/

# System processes (grep for running gateways)
ps aux | grep "hermes_cli.*gateway"
ps aux | grep "cloakserve"

# Web UI
ps aux | grep "hermes-web-ui"
```

### 2️⃣ Cron Job Health

```bash
# List all jobs
hermes cron list
```

Key indicators:
- `last_status: ok` → healthy
- `last_status: error` → investigate
- `last_delivery_error` set → delivery problem
- Run a manual trigger with `cronjob(action='run', job_id='...')` to verify

### 2b️⃣ Systematic Cron Audit

When performing a full cron audit ("排查每个agent的Cronjob Response"), follow this process:

**Phase 1: Inventory**
```bash
# List all jobs, note their type and status
cronjob(action='list')
# Classify each job:
# - no_agent (script-only): stdout IS the output
# - LLM-driven (has prompt): agent generates response
# - never run: last_run_at = null
# - has error: last_status = error
```

**Phase 2: Verify each job**
- For **no_agent jobs**: run the script manually (`bash <script_path>`), check exit code and output
- For **LLM-driven jobs**: check the prompt preview, verify it includes Obsidian sync steps if needed
- For **error jobs**: read the log file, identify root cause
- For **never-run jobs**: test manually to verify they work before their scheduled time

**Phase 3: Classify output types**

Each cron job's output belongs to one of these vault categories:
| Category | Content | Example |
|----------|---------|---------|
| 流程 (Process) | Sync pipelines, backups, request polling | memory sync, git backup, cross-request worker |
| 知识 (Knowledge) | Research, learning, market data | arxiv papers, price monitoring, GitHub learning |
| 配置 (Config) | System audits, compliance checks | vault-compliance |

**Phase 4: Sync mechanism selection**

| Cron type | Sync approach | How |
|-----------|---------------|-----|
| LLM-driven | Direct-write in prompt | Embed file write in the cron prompt with `deliver=local` |
| no_agent script | Relay pipeline | `relay_to_obsidian.py` (hourly pipeline Step 4) reads relay/ files → Obsidian living docs |
| Error/status info | Manual or dedicated script | Write status doc to `配置/` directory |

**Phase 5: Document findings**

Create a living status document in Obsidian `配置/Cron·Jobs运行状态.md`:
```markdown
## 分类总表
| 分类 | Job | 输出目标 |
|------|-----|---------|
| 流程 | backup, sync, poll | Obsidian `流程/` |
| 知识 | arxiv, price, learning | Obsidian `知识/` |
| 配置 | compliance, audit | Obsidian `配置/` |
```

### 2c️⃣ Common Cron Fixes

**`dict | None` type hint syntax error (Python 3.9)**
- Symptom: `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`
- Root cause: Script uses `python3` which is 3.9, but `dict | None` requires 3.10+
- Fix: Replace `-> dict | None` with `-> Optional[dict]` or just `-> dict`
- Prevention: Always check `python3 --version` before using union type syntax

**Git push rejected (remote has newer commits)**
- Symptom: `! [rejected] main -> main (fetch first)`
- Root cause: Another process pushed to the same remote between commit and push
- Fix: Use `git fetch origin main && git rebase origin/main` instead of `git pull --rebase` (more controllable)
- Script pattern:
  ```bash
  git fetch origin main >> "$LOG" 2>&1
  git rebase origin/main >> "$LOG" 2>&1 || {
      echo "rebase conflict, skipping backup commit"
      git rebase --abort 2>/dev/null
      git reset --soft HEAD~1 2>/dev/null
  }
  ```
- Prevention: Ensure all backup scripts use exclusive push logic, or use different branches

**Script not found / wrong PATH**
- Symptom: exit code 127, "command not found" for `python3.11`, `node`, etc.
- Root cause: Cron runs with minimal PATH (`/usr/bin:/bin`). Homebrew binaries invisible.
- Fix: Always use absolute paths in cron scripts: `/opt/homebrew/bin/python3.11`
- Check: `grep '^#!/' ~/.hermes/scripts/*.sh ~/.hermes/scripts/*.py | head -10`

**Output delivered to wrong channel**
- Symptom: Cron job response arrives in an unexpected conversation
- Fix: Set `deliver=local` for internal jobs, `deliver=origin` only for user-facing jobs
- Rule of thumb: If the cron output is just data/status (not actionable for the user), use `deliver=local`

**Python version mismatch between script and cron**
- Symptom: Script works in terminal but fails in cron
- Check: Compare `which python3` vs the shebang in the script
- Fix: Either use `#!/opt/homebrew/bin/python3.11` or configure cron's PATH in the script:
  ```bash
  PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
  ```

**`execute_code` terminal() fails on complex shell commands**
- Symptom: `hermes cron create` returns empty output when called from `execute_code`'s `terminal()`
- Root cause: `execute_code`'s `terminal()` wraps commands through Python's subprocess, and multi-line prompts with quotes/backslashes get mangled by shell escaping layers
- Fix: Use **direct `terminal()` tool calls** (not from within `execute_code`) for `hermes cron create` with multi-line prompts. Direct tool calls preserve shell quoting.
- Rule: If a shell command uses nested quotes, backslashes, or multi-line arguments, prefer direct `terminal()` over `execute_code` wrapping.

### 3️⃣ Component Updates

```bash
# Hermes Agent
hermes --version  # check "up to date" line

# CloakBrowser binary
python3 -m cloakbrowser info  # check "Installed: True"
python3 -m cloakbrowser update  # check for binary update

# pip packages
pip3 list --outdated 2>/dev/null | grep -v "^Package\|^──\|^$\|WARNING"

# macOS + Homebrew
brew outdated 2>/dev/null | head -10
softwareupdate -l 2>/dev/null | grep -v "No new\|Software Update\|Finding"
```

### 4️⃣ Vault Health Check

```bash
cd ~/Molin-OS && python3 scripts/vault_health_check.py
# Expected: ✅ Vault 健康检查通过
```

**允许的根目录**: 决策/ 知识/ 流程/ 成果/ 报告/ 配置/ 学习档案/ 产出/ Archive/

**vault_health_check.py** 自动检测：
- 禁止的根目录（Agents/ Daily/ System/ 等）
- 根级杂文件（.md / Makefile / README 等）
- 嵌套子目录违反白名单
- 同名文件冲突

### 4b️⃣ iCloud 幽灵目录删除

当 Vault 中出现不应存在的空目录（如 iCloud Drive 自动恢复的旧路径），`rm -rf` 可能无效。

**根因**: iCloud Drive 的同步引擎在云端有目录记录，本地删除后云端恢复。

**修复步骤**:
1. 确认目录内文件已迁移或清空
2. 暂停 iCloud 文件提供者服务：
   ```bash
   launchctl bootout gui/$(id -u)/com.apple.cloudd 2>/dev/null
   ```
3. 删除目标目录：
   ```bash
   rm -rf "/path/to/target"
   ```
4. 恢复 iCloud 服务：
   ```bash
   launchctl bootstrap gui/$(id -u) /System/Library/LaunchAgents/com.apple.cloudd.plist 2>/dev/null
   ```

**陷阱**: 不要先设置 `chflags -R uchg`（这会锁定目录导致不可删除），然后发现删不掉又用 `chflags -R nouchg` 解锁。正确的顺序是：直接暂停 iCloud → 删除 → 恢复 iCloud。

**预防**: 写入脚本应使用正确的 vault 路径，避免创建不合规的目录结构。

### 5️⃣ Sync Pipeline

```bash
# Memory + Obsidian + Architecture sync
bash ~/Molin-OS/scripts/sync_all.sh
```

If the pipeline fails at step 3 (collect_architecture.py timeout):
> ⚠️ Supermemory has been decommissioned. The connectivity pre-check note below is kept for historical awareness.

### 5️⃣ Profile Skills Sync

When skills are created or updated, sync to all 5 agent profiles:

```bash
for p in edu global media shared side; do
  rsync -a ~/.hermes/skills/molin-org/<skill>/ ~/.hermes/profiles/$p/skills/molin-org/<skill>/
done
```

List profiles needing restart (if the skill is referenced in prefill):
- `prefill_feishu_format.md` — shared across all 5 profiles via `prefill_messages_file`

### 6️⃣ Gateway Restart (when needed)

#### Normal restart
```bash
for p in edu global media shared side; do
  cd ~/.hermes/profiles/$p && hermes gateway restart
  sleep 2
done
```

#### Gateway process accumulation (UI unresponsive)

**Symptom**: Web UI loads but doesn't respond (SSE streaming broken, chat stuck, login succeeds but no conversation flow). `ps aux | grep "hermes gateway" | grep -v grep` shows 3+ gateway processes all started at the same time.

**Root cause**: `hermes gateway run --replace` sometimes fails to kill the old process, especially when multiple instances were started in rapid succession. Processes accumulate and compete for ports (8642) and the IPC socket (`/tmp/hermes-agent-bridge.sock`).

**Diagnosis**:
```bash
# Count gateway processes
ps aux | grep "hermes gateway" | grep -v grep | wc -l
# Inspect PIDs and start times
ps aux | grep "hermes gateway" | grep -v grep | awk '{print $2, $11, $12, $13}'
# Check which one actually has the port
lsof -i :8642 | grep LISTEN
```

**Fix**:
```bash
# 1. Kill all gateway processes
ps aux | grep "hermes gateway" | grep -v grep | awk '{print $2}' | xargs kill
sleep 2
# Force-kill survivors
ps aux | grep "hermes gateway" | grep -v grep | awk '{print $2}' | xargs kill -9
```

**Web UI recovery** follows a strict sequence after gateway restart:

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Kill ALL old gateway processes | `grep count` = 0 |
| 2 | Start fresh gateway: `hermes gateway run --replace` (background) | Wait 5s, check `grep count` ≥ 1 |
| 3 | Kill old web UI server + bridge | `ps aux | grep hermes-web-ui` = 0, `ps aux | grep hermes_bridge` = 0 |
| 4 | Remove dead IPC socket: `rm -f /tmp/hermes-agent-bridge.sock` | Socket gone |
| 5 | Start fresh web UI: use background shell | Wait 8s |
| 6 | Verify gateway API: `curl http://127.0.0.1:8642/health` → `{"status":"ok"}` |
| 7 | Verify web UI: `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000` → `200` |
| 8 | Verify IPC socket: `ls -la /tmp/hermes-agent-bridge.sock` | Socket exists |
| 9 | Verify web UI + bridge processes running | Both node process + hermes_bridge.py present |

**Trap**: Don't just restart the gateway without also restarting the web UI. The old bridge process stays connected to the dead gateway instance. Both must be restarted.

**Prevention**: When running `hermes gateway run --replace` repeatedly, add a 3-5s delay between attempts. Don't run gateway starts in parallel.

### 6c️⃣ Web UI Credentials

The web UI login page asks for "访问令牌" (access token). The token is stored at:

```
~/.hermes-web-ui/.token
```

In a headless/script context, the token can be injected as an env var `AUTH_TOKEN` or auth can be disabled entirely with `AUTH_DISABLED=1`.

### 6d️⃣ Repo Completeness Audit

When the user asks whether the running system is fully synced to the GitHub repo ("现在的系统是完全同步至GitHub吗"), this is not a git-only question. Run a full multi-dimensional audit.

See `references/repo-completeness-audit.md` for the complete step-by-step covering all 9 dimensions: git base state, submodule health, script/skill completeness vs ~/.hermes, Obsidian vault location and remote, cron health, system deps, Hermes config, runtime data.

Categorize findings into: In-Sync, Out-of-Sync, Missing from Repo, External (independent git repos).

**Key pitfalls**: scripts used by cron may be outside both repo and ~/.hermes/scripts/; the Obsidian vault lives in iCloud Drive not in the repo; .vault-git-mirror may point to the old MolinOS-Ultra remote.

## Port Map

| Port | Service | PID File / Detection |
|------|---------|---------------------|
| 9222 | CloakServe CDP pool | `curl localhost:9222/` |
| 5100+ | Chrome CDP (per seed) | `curl localhost:9222/` |
| — | Hermes edu gateway | `ps aux | grep "hermes_cli.*--profile edu"` |
| — | Hermes global gateway | `ps aux | grep "hermes_cli.*--profile global"` |
| — | Hermes media gateway | `ps aux | grep "hermes_cli.*--profile media"` |
| — | Hermes shared gateway | `ps aux | grep "hermes_cli.*--profile shared"` |
| — | Hermes side gateway | `ps aux | grep "hermes_cli.*--profile side"` |
| — | hermes-web-ui | `ps aux | grep hermes-web-ui` |

## Known Issues & Fixes

### collect_architecture.py times out

**Symptoms**: `sync_all.sh` or `molin-sync-all.sh` hangs at "🏗️ [3/3] 采集系统架构..."

**Root cause**: Supermemory API connectivity issue (service has been decommissioned).

**Fixes**: Supermemory has been decommissioned. The historical fixes are no longer relevant.

### CloakServe binary download slow

**Issue**: The ~200MB Chromium binary download from `cloakbrowser.dev` or GitHub can be very slow from China (~40-260 KB/s), frequently timing out.

**Fix**: Manual download with resume:
```bash
curl -L -C - --connect-timeout 10 --max-time 600 \
  "https://cloakbrowser.dev/chromium-v{version}/{archive}" \
  -o /tmp/cloakbrowser-{archive}.tar.gz
tar xzf /tmp/cloakbrowser-{archive}.tar.gz -C ~/.cloakbrowser/chromium-{version}/
```

See `cloakserve` skill's `references/installation-notes.md` for platform-specific URLs.

### Hermes update hangs

**Issue**: `hermes update` may appear to hang with no output (background process with empty output stream).

**Fix**: Kill the stuck `hermes update` process, then manually:
```bash
cd ~/.hermes/hermes-agent && git pull
```
This updates the code. The version string doesn't change if it's an intermediate CI/small commit.

### GitHub connectivity failure (HTTPS → SSH migration)

**Symptoms**: `git fetch/push` to GitHub times out with `Recv failure: Operation timed out`, but `curl https://github.com` returns 200 and `nc -z github.com 22` succeeds.

**Root cause**: GFW DPI blocks git pack data transfer on HTTPS while allowing TCP + TLS handshake. HTTP/1.1 config is insufficient.

**Fix**: Migrate remote from HTTPS to SSH. See `github-auth` skill → "GFW / China-Specific Connectivity Issues" for the complete diagnostic flow and SSH setup recipe, or `references/gfw-github-connectivity.md` for the session log.

## Prefill

All 5 agent profiles share one global prefill file:
`~/.hermes/profiles/prefill_feishu_format.md`

This file has sections for:
- 飞书回复格式规范
- 委派优先 🧠
- 共享隐形浏览器池 (CloakServe) 🕵️

Append new sections here when adding cross-agent capabilities.

## 7️⃣ Evolution Upgrade Deployment

When deploying a Molin-OS evolution upgrade package (SOP files, cron configs, scripts, learning subscriptions), follow this phased workflow. This standard was established during the v3.0 flat vault upgrade.

### Phase 1: Pre-Deployment Audit

```bash
# Check current vault state
python3 ~/Molin-OS/scripts/vault_health_check.py

# List existing CronJobs (check for conflicts)
hermes cron list 2>&1 | grep "Name:"

```

### Phase 2: Path Compatibility Analysis

Compare every path in the upgrade package against the current vault structure. Key mapping:

| Old Path Pattern | v3.0 Equivalent | Location |
|---|---|---|
| `~/MolinOS-Wiki` | Full iCloud vault path | All configs |
| `知识库/方法论/{agent}/{topic}.md` | `知识/业务线｜方法论·{topic}.md` | SOP definitions |
| `学习吸收/GitHub精读/{agent}/` | `学习档案/业务线｜{项目}·{date}.md` | Scripts + Configs |
| `业务数据/月度复盘/` | `报告/系统｜日报·{date}.md` | Cron prompts |
| `Agent档案/{agent}/能力版本.md` | `流程/业务线｜能力版本.md` | SOP definitions |
| `产出/{agent_id}/` | `产出/业务线｜{内容}.md` | All outputs |

**Principle**: 8 root dirs, zero subdirectories, `业务线｜内容.md` naming.

### Phase 3: Batch Upgrade & Deploy

```bash
# 1. Upgrade package files in isolation
OUT=/tmp/molinos_upgrade_v3
mkdir -p $OUT/{scripts,config/learning,sop/definitions}

# 2. Apply path replacements to each file
# Use execute_code for batch string replacements
# Key replacements:
#   MolinOS-Wiki → actual iCloud vault path
#   old-subdir-paths → flat dir + 业务线｜ prefix

# 3. Deploy to Molin-OS
cp $OUT/scripts/*.py ~/Molin-OS/scripts/
cp $OUT/config/learning/*.yaml ~/Molin-OS/config/learning/
cp $OUT/sop/definitions/*.yaml ~/Molin-OS/sop/definitions/
cp $OUT/config/cron_evolution_plan.yaml ~/Molin-OS/config/
```

### Phase 4: CronJob Creation with Conflict Detection

**PITFALL**: `execute_code`'s `terminal()` cannot handle `hermes cron create` with multi-line prompts or nested quotes. Use **direct `terminal()` tool calls** instead.

```bash
# For each new CronJob:
# 1. Check if a job with same name AND same schedule already exists
hermes cron list 2>&1 | grep -E "Name:|Schedule:"

# 2. Check for time conflicts with existing jobs
#    (two jobs at exact same minute = conflict)
#    If conflict: shift by 30 minutes

# 3. Create (using direct terminal, not execute_code)
hermes cron create \
  --name "Job Name" \
  --deliver local \
  --skill relevant-skill \
  --workdir "/Users/laomo/Molin-OS" \
  "cron_expression" \
  "prompt_text"
```

### Phase 5: Post-Deployment Verification

```bash
# Vault health
python3 ~/Molin-OS/scripts/vault_health_check.py

# CronJob count audit
hermes cron list 2>&1 | grep "Name:" | wc -l

# Scan for residual old paths in vault
grep -rn 'MolinOS-Wiki\|agent-outputs\|02_Agent_Outputs' \
  "/path/to/vault/" --include="*.md" | grep -v '.git/'

# Supermemory has been decommissioned — cleanup steps below are no longer applicable

```

### Common Pitfalls

- **init_obsidian_taxonomy.py is deprecated**: Creates old subdirectory structure incompatible with v3.0 flat vault. Skip it.
- **Duplicate CronJobs**: Check both name AND schedule before creating. If name is different but schedule is identical, it may still be a functional duplicate (e.g., "月度规划生成" and "plan_b3_monthly_plan" both targeting 1st of month 09:00).
- **SOP files still reference old paths**: Always scan SOP YAML files for `obsidian_path`, `obsidian_base`, and hardcoded directory references before deploying.

## Reference Files

| File | Purpose |
|------|---------|
| `references/cron-audit-checklist.md` | Step-by-step cron job audit checklist with common fixes table |
| `references/icloud-ghost-directory.md` | iCloud Drive 幽灵目录删除（当 rm -rf 无效时） |
| `references/v3.0-path-mapping.md` | v3.0 平坦 vault 完整路径映射表（旧→新，供升级部署使用） |
