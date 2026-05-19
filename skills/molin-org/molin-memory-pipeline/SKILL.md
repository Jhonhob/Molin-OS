---
name: molin-memory-pipeline
version: "5.12.0"
description: "Molin-OS memory sync pipeline v5.12 — 8 flat root directories (决策/知识/流程/成果/报告/配置/产出/学习档案), ZERO subdirectories, 业务线｜具体内容 naming, 5-layer write-source audit, YAML frontmatter validation, iCloud git mirror bridge, 5 scripts with validated path targets, vault hardening methodology."
allowed-tools: Terminal, Read, Write, ExecuteCode
trigger-keywords:
  - memory sync
  - 记忆同步
  - 记忆管道
  - sync_memory
  - obsidian_sync
  - collect_architecture
  - cron 记忆
  - cron 同步
  - cron obsidian
  - 定时任务 vault
  - pipeline
  - Supermemory
  - 同步脚本
  - Obsidian Git
  - git插件
  - vault compliance
  - vault整理
  - 整理vault
  - 重新整理
  - 重新分类
  - 流程文档
  - 核心文档
  - 文件夹太多
invocation-context: "Load this skill when running, debugging, or modifying the memory sync pipeline (sync_memory.py, obsidian_sync.py, collect_architecture.py), OR when creating/updating a cron job that needs to write output to the Obsidian vault directly (direct-write pattern). For vault structure, classification, or frontmatter questions → load note-taking/obsidian and read System/执行规范v4.md."
input:
  format: |
    Pipeline scripts in ~/Molin-OS/scripts/:
      1. sync_memory.py (v5.1)     — Extract conversation → classify → write Obsidian (living docs) + Supermemory
                                     写入目标: {决策|知识|流程|成果}/Agent·Topic.md（按分类）
      2. obsidian_sync.py (v4)      — Sync reports → 报告/<date>.md (aggregated daily) + {分类}/
                                     写入目标: 报告/<date>.md（聚合日报），{分类}/<filename>（Molín产出）
      3. collect_architecture.py    — Collect system state → 配置/ + Supermemory containers
                                     写入目标: 配置/系统｜架构.md, 配置/系统｜记忆映射.md

    Orchestrated by: ~/Molin-OS/scripts/sync_all.sh
    Cron schedule: hourly (script: molin-sync-all.sh at ~/.hermes/scripts/)
output:
  format: |
    Results in Obsidian vault (v5.7 flat structure):
      - 决策/业务线｜主题.md   — irreversible choices
      - 知识/业务线｜主题.md   — learnings + report + research
      - 流程/业务线｜主题.md   — SOPs + configs + checklists
      - 配置/业务线｜主题.md   — system architecture + agent profiles
      - 报告/业务线｜主题.md   — daily/weekly aggregated reports
      - 产出/业务线｜主题.md   — agent execution outputs
      - 学习档案/业务线｜主题.md — learning absorption
    Results in Supermemory: per-agent containers with category metadata
---

# Molin-OS Memory Pipeline (v5.2)

## Vault Structure (v5.7 — 2026-05-17)

**Final directory structure — 8 flat root directories, ZERO subdirectories:**

```
Vault/
├── 决策/     ← Irreversible decisions
├── 知识/     ← Learning & research
├── 流程/     ← SOPs, configs, toolchains
├── 成果/     ← Deliverables
├── 报告/     ← Daily/weekly reports & KPI dashboards
├── 配置/     ← System architecture metadata
├── 产出/     ← All Agent execution outputs (flat, NO profile subdirs)
├── 学习档案/  ← GitHub learning & deep notes (flat, NO agent subdirs)
└── Archive/  ← Read-only old backups
```

**ZERO subdirectories.** `产出/<profile>/`, `学习档案/<agent>/github-absorb/`, `报告/KPI看板/` are all **eliminated**. File naming alone disambiguates.

**业务线 = 系统/元瑶(edu)/银月(media)/梅凝(global)/宋玉(side)/玄骨(shared+finance)/KPI.**
Root directory carries the type — never repeat it in the filename.

**System vs Agent test**: "If I delete this agent, is this file still needed by other agents?" → Yes = `系统`. No = that agent's 业务线. Infrastructure (Relay, CronJob, toolchain, Obsidian, Feishu, memory structure, agent profiles, execution specs) = `系统`. Agent-domain output (education, media, side projects, finance, research) = respective agent.

**Rolling daily files**: `银月｜日报`, `宋玉｜日报`, `系统｜日报`, `玄骨｜日报` — single persistent file per agent, updated daily. No timestamped daily files.

**3 scripts → their vault paths:**
| Script | Writes to | Purpose |
|--------|-----------|---------|
| `sync_memory.py` | `{分类}/` | Conversation memory by MECE category |
| `obsidian_sync.py` | `报告/` + `{分类}/` | Aggregated daily + Molin outputs |
| `collect_architecture.py` | `配置/` | System architecture + agent profiles + memory map |
| `relay_to_obsidian.py` | `知识/` | no_agent cron script relay outputs → living docs |

**File naming**: `业务线｜具体内容.md` with full-width pipe. 业务线 = 系统/元瑶/银月/梅凝/宋玉/玄骨/KPI. Root directory = type, never repeat it in filename.

**Classification**: 方案/策略/规划 → 决策 | 报告/日报/调研/方法论 → 知识 | SOP/配置/系统文档 → 流程 | 系统架构/Agent配置 → 配置 | 每日聚合 → 报告

For full vault structure rules, load `note-taking/obsidian` skill.

## ⚠️ Vault Structure and Standards (delegated)

This skill manages the **operational pipeline** (scripts, cron, Supermemory). For **vault structure, classification rules, frontmatter spec, and writing standards**, load:

1. `obsidian` skill — vault structure (8-dir flat) + writing rules + file operations
2. `流程/系统｜执行规范.md` — classification decision tree, quality gate, format templates

Both are the authoritative sources. This skill does NOT duplicate them.

## v5 Sync Rules (sync_memory.py v5)

### Filename Sanitization
All filenames are now aggressively cleaned before writing:
- Special chars stripped: `[](){}#·*|:<>"'!?@$%^&=+\\/`
- Whitespace normalized to single spaces
- Max 24 chars, truncated at UTF-8 boundary
- Min 2 meaningful chars; falls back to "对话记录"
- NO agent names or category prefixes in filenames (those are encoded by directory path)

### Content Quality
Every synced entry follows pyramid format:
```
## YYYY-MM-DD
### 结论      ← one-sentence conclusion, extracted from assistant response
### 背景      ← user's intent/context
### 核心内容   ← key points (max 8, deduplicated)
### 下一步     ← next steps or "待补充"
```

- System prompt noise (`[IMPORTANT:`, `# Profile:`, etc.) is filtered
- Duplicate conclusions across sessions are merged
- Same-topic entries append to existing files (living document mode)

### Session Dedup
- `~/.hermes/profiles/{agent}/sync_tracker.json` tracks synced sessions by (filename, mtime, size)
- Already-synced sessions are skipped
- Stale tracker entries (>30 days) auto-purged

## v5.2 Sync Rules

When the user asks to "整理" (reorganize/consolidate) the vault — merge duplicates, delete garbage, fix structure:

### Phase 1: Full Audit
Run a comprehensive scan across all 5 agents × 4 categories:
```python
for each file:
    check: size < 600B (THIN), has_结论结构, agent chatter in body,
           frontmatter completeness, duplicate topic across agents/categories
```

### Phase 2: Merge Duplicates
Rules:
- Same topic across categories → keep the largest/most complete, merge others in
- Delete source files after merge (content is preserved in destination)
- Example: 小红书 in 决策 + 知识 + 成果 → merge into 知识/银月｜小红书.md, delete other two
- Example: GitHub in 成果 + 决策 → merge into 决策/系统｜GitHub.md, delete 成果 copy（v3.0: 必须含业务线｜前缀）

### Phase 3: Delete Garbage
Files meeting ANY of these criteria → delete (merge unique content first):
- Size < 600B with no unique content
- `### 结论` starts with English agent chatter ("Let me", "I'll", "Now I")
- Body contains leaked system prompts ("[IMPORTANT:", "--- name:")
- "报告" files that just have bare headers and no substance

### Phase 4: Fix Garbage
For files with minor garbage but unique content:
- Replace `---` body separators with `***` (avoids frontmatter-in-body)
- Rewrite agent-chatter conclusions with real summaries
- Fix `### 下一步` with garbled text

### Phase 5: Parallel Execution
For bulk fix across multiple agents, use `delegate_task`:
```
tasks = [
  {goal: "Fix <agent> files: merge duplicates, delete garbage, fix structure",
   toolsets: ["terminal","file"]},
  ...  # one per agent, up to 3 parallel
]
```

### Post-consolidation Checklist
- [ ] No agent chatter in any `### 结论`
- [ ] No `---` inside body (only frontmatter uses it)
- [ ] No files < 600B without unique content
- [ ] No duplicate topics across categories within same agent
- [ ] All files have v5 frontmatter
- [ ] Daily/2026-05-15.md updated with consolidation summary
- [ ] Git commit + push

### Every file must have body text

**Never write a file that is only a title.** Every document must have at least one meaningful paragraph of content. A file with only `# Title` and no body text is a "空壳" (empty shell) and will be rejected.

### Living documents replace disposable files

When completing work on a topic:
- **Do NOT** create a new timestamped file
- **DO** append to the existing topic file in the correct category
- Update the `updated` date in frontmatter

Example living document structure (v4):
```markdown
---
created: 2026-05-15
updated: 2026-05-15
agent: media
category: 决策
status: 活跃
confidence: 已验证
importance: ⭐⭐⭐
source: 实践
tags: [cloakserve, CDP, 技术选型]
---

# CloakServe集成

## 方案定稿（Time: 2026-05-15）

### 结论
选用 cloakserve v0.25，5 种子池 + launchd 守护。

### 理由
- 池化比单实例稳定，CDP 端口冲突减少 80%

### 下一步
- [ ] 压测
```

### What belongs where

- **Python scripts** (`.py`) and **JSON outputs** → NOT in Obsidian
  - Scripts → `~/Molin-OS/scripts/`
  - Relay outputs → `~/Molin-OS/data/relay/`
  - Only markdown files in the vault
- **Conversation memory** → 对话记录/ (cache, 7-day retention) — auto-deleted by script
- **Architecture decisions** → 决策/ with topic name

### Vault root must be spotless (v5.3)

Only these entries allowed at vault root:
`决策/`, `知识/`, `流程/`, `配置/`, `报告/`, `Archive/`, `.obsidian/`, `.git/`, `.gitignore`, `.DS_Store`

**No code directories.** Code files from MolinOS-Ultra (molib/, scripts/, skills/, tools/, docs/, Makefile, README.md, env/) that leaked into the vault during git merge must be removed. They belong in their own repo, not the Obsidian vault.

**No nested folders.** All 8 root directories contain only `.md` files — ZERO subdirectories. The `业务线｜具体内容.md` naming convention alone disambiguates agent ownership. `产出/` and `学习档案/` are flat — no `产出/<profile>/` or `学习档案/<agent>/github-absorb/` subdirectories.

**Check for rogue dirs regularly.** Any subdirectory under the 8 root dirs is a violation. Known offenders that sync scripts may create: `产出/edu/`, `产出/finance/`, `学习档案/media/github-absorb/`, `报告/KPI看板/`. Audit command:
```bash
# Check for forbidden dirs at vault root
for d in Agents System Daily env; do
  test -d "$VAULT/$d" && echo "⚠️  ROGUE: $d/ still exists"
done
# Check for extra top-level dirs
ls -d "$VAULT"/*/ 2>/dev/null | grep -vE '(决策|知识|流程|配置|报告|Archive|\.obsidian|\.git)' && echo "⚠️  Unexpected dir found"
```

## Pipeline Scripts

Located in `~/Molin-OS/scripts/`:

### 1. sync_memory.py (v5.1) — Conversation Memory Sync
- Reads session conversations, classifies by v4 MECE categories, writes to Obsidian (living docs: topic-based append, not timestamped files) + Supermemory
- Duration: ~15-20s (bottleneck: Supermemory API write)
- Fallback: if Supermemory unreachable, logs warning and continues to Obsidian write

### 2. obsidian_sync.py (v4) — Report Sync
- Syncs reports to `报告/<date>.md` (single aggregated daily, all agents in one file)
- Also syncs to `{决策|知识|流程}/` based on filename mapping (Molin产出)
- Dry-run mode: `--dry-run`
- Duration: ~2-5s

### 3. collect_architecture.py — System Architecture Collector
- Collects all 5 agent configs, writes to `配置/` (architecture.md + agents/<agent>.md + memory-map.md) + 15 Supermemory documents
- Has 5s connectivity pre-check for Supermemory (skips if unreachable)
- Duration: ~25-35s

### 4. relay_to_obsidian.py (v1) — Relay Output Sync
- Scans `~/Molin-OS/relay/shared/results/` and `~/Molin-OS/relay/side/results/` for new files from no_agent cron scripts
- For each new file: parses content, creates/updates a living document in Obsidian `知识/`
- Uses fingerprint tracker at `~/.hermes/relay_sync_tracker.json` to avoid re-processing
- Currently handles: arxiv daily papers → `知识/每日·Arxiv论文.md`, side price monitor → `知识/每日·副业价格监控.md`
- Extensible: add new handlers in the script for new relay file types
- Dry-run mode: `--dry-run`
- Duration: ~1-3s (no network I/O)

### 5. vault_git_sync.py — Vault Git Sync Bridge
- Bridges iCloud Drive git mmap conflict by maintaining a mirror repo at `~/Molin-OS/.vault-git-mirror/`
- rsync vault ↔ mirror, all git operations happen on the mirror (普通文件系统，无 mmap 冲突)
- Modes: push (default), pull (`--pull`), dry-run (`--dry-run`)
- Idempotent — skips git commit/push when no changes detected
- Duration: ~5-10s (rsync + git status)
- Cron: every 15 minutes (`*/15 * * * *`)

### Orchestration
```bash
# Manual:
cd ~/Molin-OS && bash scripts/sync_all.sh

# Cron (hourly at HH:00):
~/.hermes/scripts/molin-sync-all.sh

# Pipeline executes 4 scripts in order:
# 1. sync_memory.py      — conversation → Obsidian + Supermemory
# 2. obsidian_sync.py    — reports → 报告/ + {分类}/
# 3. collect_architecture.py — system state → 配置/ + Supermemory
# 4. relay_to_obsidian.py    — no_agent cron relay outputs → 知识/

# Git sync runs independently (iCloud mmap conflict → needs separate mirror):
# Crontab: */15 * * * * cd ~/Molin-OS/scripts && /usr/bin/python3 vault_git_sync.py >> /tmp/vault-git-sync.log 2>&1
```

## Pitfalls (v4)

### MolinOS-Wiki symlink silently redirects old-path writes (v5.10)

**Root cause:** `~/MolinOS-Wiki → iCloud vault` symlink. Any script still writing to `~/MolinOS-Wiki/产出/edu/` silently writes to `iCloud vault/产出/edu/`. The write succeeds — no error, no warning. The ghost directory reappears and you can't tell which script caused it.

**Fix:** Delete the symlink FIRST, then audit all scripts:
```bash
rm ~/MolinOS-Wiki
# Now old-path writes will FAIL with FileNotFoundError instead of silently polluting vault
```

**Detection after deletion:**
```bash
# Find all scripts that would have written through the symlink
grep -rn 'MolinOS-Wiki\|Molin_OS_Wiki' ~/.hermes/scripts/ ~/.hermes/profiles/*/scripts/ ~/Molin-OS/scripts/ --include='*.py'
```

### Two copies of same script in different locations (v5.10)

**Root cause:** Some scripts exist in both `~/.hermes/scripts/` and `~/Molin-OS/scripts/` (duplicates created during earlier reorganization). Patching one location leaves the other still writing old paths.

**Known duplicates:**
- `relay_to_obsidian.py` — in BOTH `~/.hermes/scripts/` and `~/Molin-OS/scripts/`
- `sync_memory_edu.py` — in BOTH `~/.hermes/scripts/` and `~/.hermes/profiles/edu/scripts/`

**Fix:** When patching a path, always check for duplicate copies first:
```bash
find ~/.hermes/ ~/Molin-OS/ -name "relay_to_obsidian.py" 2>/dev/null
```

### 银月/ keeps reappearing at vault root (OBSOLETE in v5.10 — MolinOS-Wiki symlink deleted)

### Old structure files being written instead of v4
**Root cause:** sync_memory.py hadn't been updated, or agent is running old cached logic.
**Fix:** Verify `~/Molin-OS/scripts/sync_memory.py` has v4 classifier and living-doc write mode.
**Check:** Files should go to `{决策|知识|流程|成果}/`, never to `项目/` or `知识库/`.

### Content is too thin / conversation dumps
- User: "要精华部分，不是流水账"
- Fix: The v4 sync_memory.py strips emoji prefixes, extracts conclusion lines, and rejects pure conversation dumps.
- If content still looks like raw chat, the classifier lost context — manually extract the conclusion and re-write.

### Too many folders / hard to find things
- User: "文件夹过多，不容易查找"
- Fix: Each agent should have exactly 4 categories (决策/知识/流程/成果). Old `项目/知识库/产出/` dirs are read-only reference. If more dirs appear, archive them.

### Emoji in filenames or folder names
- User explicitly rejected emoji. Use clean Chinese: `决策/`, `知识/`, `流程/`, `成果/`.
- Fix: Rename or move files out of emoji-named dirs.

### v4 Garbage in Files (post-v5 upgrade)
After upgrading to v5, old files may have v4-formatted noise:
- `[IMPORTANT:...` system prompts in body
- `### 关键信息` sections with raw chat dumps
- Old titles like `## 银月传媒 · xxx（Time: 2026-05-15）`
- Agent name prefixes in filenames (`银月传媒 · [IMPO.md`)
Fix: Run the v5 cleanup script or manually delete + let v5 regenerate clean entries.

### Agent-local output bypasses sync pipeline (BLIND SPOT) — v5.3 fix

**Root cause:** When an agent writes output files to its own local directories (`~/.hermes/profiles/<agent>/plans/`, `content/`, `agent-outputs/`, `relay/`, `curriculum/`), these are NOT visible to sync_memory.py which only scans session JSONs. Additionally, sync scripts may write to `Agents/` or `System/` paths if not kept in sync with the current vault structure.

**Symptoms:** User asks "why isn't X in Obsidian?" — the content exists as a file in the agent profile but never made it to the vault. Or rogue directories (Agents/, System/, env/) appear at vault root.

**Vault structure drift — most common cause:**
```bash
# Check ALL 3 scripts write to correct paths (v5.3 targets)
# sync_memory.py:  VAULT / category
# obsidian_sync.py: VAULT / category     (not VAULT / "Agents" / agent_id / category)
#                   VAULT / "报告"       (not VAULT / "Daily")
# collect_architecture.py: VAULT / "配置" (not VAULT / "System")
grep 'VAULT /' ~/Molin-OS/scripts/sync_memory.py ~/Molin-OS/scripts/obsidian_sync.py ~/Molin-OS/scripts/collect_architecture.py
```

**Fix for one file:**
1. Read the local file, classify by topic into {决策|知识|流程|成果|配置|报告}
2. Write to `{category}/Agent·Topic.md` with v5 frontmatter + pyramid format
3. Append to existing file if topic already has one (living document)

**Fix for rogue directory at vault root:**
1. Check if any files inside need migrating
2. Copy files to correct {分类}/ directory
3. Delete rogue directory (`rm -rf`)
4. Then fix the script that created it (update its `VAULT` target path)

### sync_memory.py extracts agent chatter as conclusions (GARBAGE EXTRACTION) — FIXED in v5.1

**Root cause:** sync_memory.py v5's `extract_conclusions()` took the first 3 lines of EVERY assistant message as a "conclusion". When the assistant responded with internal planning chatter — "Let me start by exploring the codebase...", "Now I have all the context I need...", "I'll clone the repo and examine...", "找到了！第14行已经是正确的 key" — these were written as `### 结论` into Obsidian files.

**Symptoms (20 of 51 files affected in May 16 audit):**
- `### 结论` contains English planning language: "Let me start by...", "Now I have...", "I'll clone..."
- `### 核心内容` is a raw bullet list of agent internal steps: "Let me check the existing skill structure..."
- `### 下一步` has garbled text like "reply generation), retrieve the last **10** turns"
- File body reads like raw conversation transcript, not knowledge

**v5.1 Fix (committed 2026-05-16 to Molin-OS:ede3327):**

1. Added `AGENT_CHATTER_PATTERNS` — 23 regex patterns detecting internal monologue:
   - English: `Let me (start|explore|check|see|...)`, `I('ll| will) (clone|read|...)`, `Now I (have|understand|...)`, `Let's (start|...)`, `I need to`, `(Step|Phase) \\d`
   - Chinese: `(好|好的|明白|嗯)我先`, `(现在|让我|我先|我来|我看看|我查)`, `(找到了|拿到了|看到了)[，,]`, `(先|再|然后)(让我|我来|查看|检查)`
   - Others: ``` (code blocks at message start), `(The|This) (file|code|repo)`, `I have (read|examined|...)`

2. Rewrote `extract_conclusions()`:
   - Scans from **end to start** (later assistant messages contain summaries, not planning)
   - Skips messages whose first meaningful line matches any chatter pattern
   - Prefers Chinese-first lines and messages containing `结论|总结|发现|核心|学到|关键|完成|方案`
   - Fallback: if ALL messages were filtered, re-scan skipping only chatter lines (not whole messages)

**Impact:** 20 garbled files cleaned from 51-file vault. Future hourly sync runs now produce real conclusions instead of agent monologue.

**Detection →** `references/garbage-audit.md`
**Fix workflow →** see §Vault Consolidation Workflow below

### Supermemory API unreachable
- API may time out from China (GFW). collect_architecture.py has 5s pre-check.
- sync_memory.py v5 has `timeout=10, max_retries=1` on Supermemory client, catches Exception, logs warning, continues to Obsidian write.

### Cron PATH: python/python3.11 not found (exit 127)

**Root cause:** cron daemon runs with minimal PATH (`/usr/bin:/bin`). Homebrew-installed binaries at `/opt/homebrew/bin/` (python3.11, etc.) are invisible to cron scripts.

**Fix:** Always use absolute paths in cron-invoked scripts. In `~/.hermes/scripts/molin-sync-all.sh`:
```bash
/opt/homebrew/bin/python3.11 "$SCRIPTS_DIR/sync_memory.py"    # ✅
python3.11 "$SCRIPTS_DIR/sync_memory.py"                      # ❌ fails in cron
```

**Verification recipe →** `references/sync-debugging.md`

### Obsidian Git plugin: "not a git repository"

**Root cause:** The vault directory has no `.git`. Obsidian Git plugin cannot operate without a git repo.

**Fix:** Initialize git in the vault root, add `.gitignore`, and make an initial commit. Full recipe in `references/sync-debugging.md` Step 6.

**Verification recipe →** `references/sync-debugging.md`

**Verification recipe →** `references/sync-debugging.md`

### Git operations fail on iCloud Drive: "mmap failed: Resource deadlock avoided" (v5.12)

**Root cause:** macOS iCloud Drive 文件锁与 git mmap 系统调用互斥。git pack 文件读取使用 `mmap()` 映射内存，iCloud 守护进程同时持有文件锁——两者冲突，kernel 返回 `EDEADLK`。没有任何 git config (`packedGitLimit`, `pack.threads`, `preloadIndex`) 能根治。

**Symptoms:** `git fetch/push/status` 全部失败，报 `fatal: mmap failed: Resource deadlock avoided`。

**Fix — 镜像桥方案：** 维护一个在普通文件系统上的 git 镜像 (`~/Molin-OS/.vault-git-mirror/`)，所有 git 操作在镜像上执行，rsync 负责 vault ↔ 镜像文件同步。自动化脚本：`~/Molin-OS/scripts/vault_git_sync.py`。

**Cron 自动推送：** `*/15 * * * *` — 独立于 molin-sync-all.sh pipeline，因为 git 操作不能直接在 iCloud 目录进行。

**关联问题 — SSH remote 被封：** vault remote 不能用 `git@github.com:...` (SSH port 22 在多处网络环境被封)。必须用 `https://github.com/...`。修复：`git remote set-url origin https://...`。

**完整细则 →** `obsidian` skill `references/git-icloud-mmap-workaround.md`

### iCloud ghost directory resurrection
iCloud Drive re-creates deleted directories even after `rm -rf`. This happens when iCloud's directory index has a conflict with the local filesystem state. Symptoms: empty directory shell keeps reappearing with only `.` and `..`.

**Workaround sequence:**
```bash
# 1. Empty all files first (prevents iCloud from re-downloading content)
echo "" > agent-outputs/edu/curriculum/*.md
# 2. chflags to mark as immutable
chflags -R uchg agent-outputs
# 3. Remove
rm -rf agent-outputs
# 4. If still reappears, rename outside iCloud scope
mv agent-outputs /tmp/agent-outputs-to-delete && rm -rf /tmp/agent-outputs-to-delete
```
If nothing works, **add the ghost dir to `ALLOWED_DIRS` in `vault_health_check.py`** so it doesn't trigger warnings. The directory will be empty (all files migrated or emptied), so it's a cosmetic iCloud issue, not a data issue.

### YAML frontmatter breaks Obsidian indexing (v5.11 — 2026-05-18)

**Root cause:** Auto-generated .md files from `sync_memory.py`, agent scripts, and `collect_architecture.py` produce YAML frontmatter values with special characters (`:`, `,`, `|`, `[[`) that aren't quoted. Obsidian's YAML parser fails silently on these, causing red error popups on every vault open. Files with broken YAML are excluded from Obsidian search, graph, and Dataview queries.

**5 patterns discovered in 2026-05-18 audit (39 files affected):**
1. `source: 对话: session_xxx` — unquoted colon (33 files)
2. `source: 系统审计: 2026-05-16 17:38 + 仓库标准化: 18:00` — multiple colons (1 file)
3. `source: repo1, repo2 | 对话: xxx` — pipe + colon (1 file)
4. `related: [[wiki-link]], [[wiki-link]]` — unquoted wiki-links with commas (2 files)
5. Entire file is one line with `\n` escapes — `collect_architecture.py` bug (2 files)

**Detection →** `scripts/validate_vault_yaml.py` (standalone, `--fix` mode) + `vault_health_check.py` (integrated, runs as part of directory audit)
**Fix recipes →** `references/yaml-frontmatter-pitfalls.md`
**Auto-fix →** `python3 scripts/validate_vault_yaml.py --fix`

**Prevention rule:** Any YAML frontmatter value containing `:`, `,`, `|`, `[`, `]`, or `{` MUST be double-quoted. Unquoted single-line YAML strings are only safe for alphanumeric values without these characters.

**Fix pattern for sync scripts:**
```python
# ❌ Broken — will crash YAML parser
f"{source_type}: {session_id}"

# ✅ Safe — always quote values with special chars
f'"{source_type}: {session_id}"'
```

### Vault naming convention
All vault top-level directory names must be clean Chinese with no numbered prefixes. User explicitly rejected `02_Agent_Outputs` — renamed to `产出/`.

**File naming**: `业务线｜具体内容.md` — full-width pipe `｜`, never middle dot `·`. 业务线 = 系统/元瑶/银月/梅凝/宋玉/玄骨/KPI. Root directory is the type — do not repeat it in filename. Rolling daily files (日报) use a single persistent file with no date suffix.

**Rule**: `决策/`, `知识/`, `流程/`, `成果/`, `报告/`, `配置/`, `产出/`, `学习档案/`. No English, no numbering, no emoji. ZERO subdirectories under any root dir. If a tool or script creates a subdirectory, eliminate it immediately.

### Agent output writer (output_writer.py)
File: `~/Molin-OS/molib/memory/output_writer.py`

All Agent outputs now go through a standard 8-section template:
```
Metadata → 任务目标 → 核心结果 → 详细分析 → 执行动作 → 风险异常 → 可复用知识 → 关联知识
```

Dual-writes to:
- **Obsidian**: `产出/业务线｜{type}·{date}.md`（v3.0 flat vault，零子目录，agent_id → 业务线前缀自动映射）
- **Supermemory**: semantic blocks (summary / insight / action as separate recall-optimized entries)

Import from any Agent:
```python
from molib.memory.output_writer import write_agent_output
result = write_agent_output(agent_id="finance", output_type="daily", ...)
```

### Memory retriever module
Files: `~/Molin-OS/molib/memory/retriever.py`, `obsidian_reader.py`, `ranker.py`

Unified retrieval entry point. Dual-source search:
- Obsidian: structured knowledge from `产出/{agent_id}/{date}.md` 
- Supermemory: semantic vectors

Agent integration:
```python
from molib.memory.retriever import retrieve_context
ctx = retrieve_context(query="转化率提升", agent_name="edu", section_filter=["洞察", "可复用知识"])
```

Supports section-level filtering (only return Insights/Actions/Learnings), dedup, recency scoring.

### Agent skill-level dual-write to agent-outputs/ (v5.6 — 2026-05-18)

**Root cause:** After fixing pipeline scripts (sync_memory.py, obsidian_sync.py, collect_architecture.py), `agent-outputs/` still kept reappearing. The fix was incomplete — agent-profile skills, memories, scripts, and plans under `~/.hermes/profiles/{edu,shared,side}/` still hardcode `agent-outputs/` as their write destination. Because `~/MolinOS-Wiki` is a symlink to the iCloud vault, any `cp` or `write_file` targeting `MolinOS-Wiki/agent-outputs/` recreates the rogue directory at vault root.

**21 active write sources across 3 profiles (edu / shared / side) + Molin-OS shared tools:**

| # | File | Line | Writes to |
|---|------|------|-----------|
| 1 | `edu/skills/workflow/edu-operations-pipeline/SKILL.md` | 221 | `agent-outputs/edu/curriculum/` |
| 2 | `edu/skills/.../growth-strategy-upgrade-pattern.md` | 85,114 | `agent-outputs/edu/curriculum/` |
| 3 | `edu/skills/workflow/edu-github-trend-research/SKILL.md` | 159,171,204 | `agent-outputs/edu/memory/` |
| 4 | `edu/skills/.../memory-automation-rules.md` | 50 | `agent-outputs/edu/memory/` |
| 5 | `tools/memory_bridge.py` (Molin-OS) | 164 | `agent-outputs/{profile}/experiences/` |
| 6 | `shared/skills/research/intelligence-automation/SKILL.md` | 50,211 | `agent-outputs/shared/intelligence/` |
| 7 | `side/skills/xianyu-automation-v2/SKILL.md` | 101 | `agent-outputs/side/` |
| 8 | `side/skills/side-research-pipeline/SKILL.md` | 270 | `agent-outputs/side/daily-evolution/` |
| 9 | `side/skills/knowledge-management-agent/SKILL.md` | 82 | `agent-outputs/side/daily-evolution/` |
| 10 | `edu/memories/MEMORY.md` | 3 | `agent-outputs/edu/memory/` |
| 11 | `side/memories/MEMORY.md` | 9 | `agent-outputs/side/` |

**Fix pattern — replace `agent-outputs/` → `产出/` in all three layers:**

```bash
# Three-layer audit (catches pipeline scripts, Molin-OS tools, AND agent-profile instructions):
grep -rn 'agent-outputs' ~/Molin-OS/scripts/ ~/Molin-OS/tools/ ~/Molin-OS/skills/ \
  ~/.hermes/profiles/{edu,shared,side}/skills/ \
  ~/.hermes/profiles/{edu,shared,side}/memories/ \
  ~/.hermes/profiles/{edu,shared,side}/scripts/ \
  ~/.hermes/profiles/{edu,shared,side}/plans/ \
  | grep -v 'cron/output' | grep -v 'sessions/' | grep -v 'iCloud 幽灵'

# Fix: agent-outputs/X/Y/ → 产出/X/Y/ (产出/ is the unified Agent output directory)
```

**Critical:** Unlike the "Hardcoded script paths" pitfall above, this fix targets **three layers** — (1) pipeline scripts in ~/Molin-OS/scripts/, (2) Molin-OS shared tools/skills in ~/Molin-OS/tools/ and ~/Molin-OS/skills/, (3) agent-profile instructions in ~/.hermes/profiles/. Fixing only layer 1 leaves layers 2 and 3 as silent recurrence vectors. Full audit reference → `references/agent-outputs-dual-write-audit.md`.

### Hardcoded script paths causing rogue directories
Multiple scripts had hardcoded legacy paths that kept recreating rogue dirs. Common culprits:
- `sync_memory_edu.py` line 26: `OBSIDIAN_MEMORY_DIR = ... / "agent-outputs" / "edu" / "memory"` → was writing to agent-outputs/ even after migration
- `sync_memory_edu.py` line 25: `MolinOS-Wiki` symlink path instead of direct iCloud path

**Fix pattern**: After any vault restructure, `grep -rn` all scripts in `~/Molin-OS/scripts/` and `~/Molin-OS/molib/` for the old path name to find stale references. A script writing to a wrong path will silently recreate the rogue directory on next cron run.

### Archive has old versions of same data
- After v4 migration, the old `项目/`, `知识库/`, `产出/` dirs contain the original copies. They are read-only reference. Do NOT delete them until user confirms.
- `.archives-v2` and `⚙️系统与配置` dirs have been copied to `Archive/` and removed from Agent dirs.

## Vault Consolidation Workflow (v5.5)

When vault becomes messy — rogue directories, duplicate files across categories, root-level garbage, scripts writing to wrong paths — use this repeatable 8-step process:

### Phase 0: Detect drift
```bash
VAULT="/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents"

# 1. Rogue dirs
for d in Agents agent-outputs Daily System env 项目 知识库 产出; do
  test -d "$VAULT/$d" && echo "ROGUE: $d/"
done

# 2. Root-level garbage
find "$VAULT" -maxdepth 1 \( -name '*.md' -o -name 'Makefile' -o -name 'README*' \) | wc -l

# 3. Duplicate filenames across categories
python3 -c "
from collections import defaultdict; import os
files = defaultdict(list)
for root, dirs, fnames in os.walk('$VAULT'):
    for f in fnames:
        if f.endswith('.md'):
            files[f].append(os.path.relpath(os.path.join(root, f), '$VAULT'))
for name, paths in sorted(files.items()):
    if len(paths) > 1: print(f'DUP: {name}: {paths}')
"

# 4. Script path drift (Molin-OS layer)
for s in sync_memory.py obsidian_sync.py collect_architecture.py relay_to_obsidian.py; do
  grep -oP 'VAULT / \"[^\"]+\"' ~/Molin-OS/scripts/$s | grep -vE '决策|知识|流程|成果|报告|配置'
done

# 5. Agent-profile instruction drift (three-layer check — v5.6)
grep -rn 'agent-outputs' ~/.hermes/profiles/{edu,shared,side}/skills/ \
  ~/.hermes/profiles/{edu,shared,side}/memories/ \
  ~/.hermes/profiles/{edu,shared,side}/scripts/ \
  ~/.hermes/profiles/{edu,shared,side}/plans/ \
  ~/Molin-OS/tools/ ~/Molin-OS/skills/ \
  | grep -v 'cron/output' | grep -v 'sessions/' | grep -v 'iCloud 幽灵'
# If output: agent-level write instructions still point to old paths
```

### Phase 1: Fix script paths (root cause)
The most common vault drift cause — sync scripts writing to legacy paths (Agents/, Daily/, System/). Apply these four fixes:

| Script | Fix | What to change |
|--------|-----|----------------|
| `obsidian_sync.py` | `init_vault()` | Remove Agents/ / Daily/ / System/ creation; only create 6 flat dirs (决策/知识/流程/成果/报告/配置) |
| `collect_architecture.py` | `collect_vault_state()` | Change `VAULT.glob("Agents/*")` to iterate 6 flat category dirs |
| `sync_memory.py` | dedup check | Change `(VAULT / "Agents" / agent_id / ...).exists()` to `filepath.exists()` |
| `generate_dashboard.py` | OUTPUT_DIR | Change `Agents/KPI看板` to `报告/KPI看板` |

After each fix, validate: `python3 -c "import py_compile; py_compile.compile('script.py', doraise=True)"`

### Phase 2: Migrate rogue dirs
| Source | Target | Content type |
|--------|--------|-------------|
| `agent-outputs/<agent>/memory/*.md` | `知识/` | Agent persistent memory dumps |
| `agent-outputs/<agent>/intelligence/*.md` | `知识/` | Intel reports by cron |
| `Agents/KPI看板/*` | `报告/KPI看板/` | Dashboard outputs |

Use `cp` then `rm` (never `mv` — user blocks it).

### Phase 3: Clean root-level garbage
Delete code artifacts (Makefile, README.md, Python files). Move root-level `.md` files into correct category based on content:
- Decision records → 决策/
- Research/analysis → 知识/
- SOP/guide → 流程/

### Phase 4: Merge duplicate filenames
Read content of same-named files across categories. Three outcomes:
- **Same content** → keep one, delete rest
- **Related topic** → merge into single file in most appropriate category, append unique sections
- **Unrelated content** → keep both files, optionally disambiguate with a comment

See `references/vault-consolidation-workflow.md` for full automation script.

### Phase 5: Final validation
```bash
# Run the automated health check script (created 2026-05-17)
cd ~/Molin-OS && python3 scripts/vault_health_check.py
# Returns exit 0 = clean, exit 1 = issues found

# Run YAML frontmatter validation (added 2026-05-18)
python3 scripts/validate_vault_yaml.py
# Returns exit 0 = clean, exit 1 = YAML issues found
# Auto-fix mode: python3 scripts/validate_vault_yaml.py --fix

# Manual alternative:
# 8 directories only
ls -d "$VAULT"/*/ | grep -v -E '\\.obsidian|\\.git' | wc -l  # should be 8

# 0 root files
find "$VAULT" -maxdepth 1 -name '*.md' | wc -l  # should be 0

# 0 duplicate filenames (run the Python check from Phase 0 again)

# All scripts write only to valid paths
for s in sync_memory.py obsidian_sync.py collect_architecture.py relay_to_obsidian.py; do
  grep -oP 'VAULT / "[^"]+"' ~/Molin-OS/scripts/$s
done
# Acceptable patterns: 决策|知识|流程|成果|报告|配置|产出|学习档案
```

### Phase 6: Downstream Skills & Docs Audit ⚠️ CRITICAL

After any vault restructure (flattening, renaming, reclassifying), **all downstream references must be audited**. Scripts in `~/Molin-OS/scripts/` are only the first layer. The following layers also hardcode vault paths and will silently recreate old structures or cause agents to write to wrong locations:

**Layer 1 — System docs (Molin-OS brain docs):**
| File | Paths to audit |
|------|---------------|
| `Molin-OS/SYSTEM.md` | `产出/{agent_id}/{date}.md`, `学习档案/{agent_id}/github-absorb/` |
| `Molin-OS/产出写入规范.md` | All agent write paths, output templates |

**Layer 2 — Hermes skills (~/.hermes/skills/):**
| Skill | Paths to audit |
|-------|---------------|
| `kpi-tracker` | `报告/KPI看板/`, `02_Agent_Outputs/`, `Agents/` |
| `kpi-dashboard` | `Agents/KPI看板/` |
| `vertical-learning-sop` | `学习档案/{agent_id}/github-absorb/`, init scripts |
| `gatekeeper-sop` | `02_Agent_Outputs/`, vault compliance rules |
| `agent-sop-template` | `02_Agent_Outputs/`, vault structure reference |
| `molin-ops` | `agent-outputs/`, iCloud ghost handling |
| `obsidian` | Old filenames (`System/执行规范v4.md` → `流程/系统｜执行规范.md`) |
| `molin-memory-pipeline` | `配置/agents/`, old filenames |

**Layer 3 — Agent profile skills (~/.hermes/profiles/{agent}/skills/):**
```bash
grep -rn 'agent-outputs|产出/(edu|content|side)/|学习档案/(edu|media|side)/' \\
  ~/.hermes/profiles/{edu,shared,side}/skills/ \\
  ~/.hermes/profiles/{edu,shared,side}/memories/ \\
  | grep -v 'cron/output' | grep -v 'sessions/'
```

**Layer 4 — Global scripts (~/.hermes/scripts/) ⚠️ NEW in v5.10:**
This directory was missed in all previous audits. It contains cron-invoked scripts that live OUTSIDE the profile structure.

```bash
# Audit ~/.hermes/scripts/ for old-path references
grep -rn 'MolinOS-Wiki\|agent-outputs\|产出/edu\|产出/shared\|Daily/' \\
  ~/.hermes/scripts/ --include='*.py' --include='*.sh'
```

Common offenders: `relay_to_obsidian.py`, `sync_memory_edu.py`, `sync_growth_full.py`, `molin-sync-all.sh`

**Layer 5 — MolinOS-Wiki symlink ⚠️ NEW in v5.10:**
```bash
test -L ~/MolinOS-Wiki && echo "⚠️ DELETE THIS SYMLINK — it silently redirects old-path writes to iCloud vault"
```
This symlink is the #1 root cause of ghost directory resurrection. Any old-path write targeting `~/MolinOS-Wiki/产出/edu/` silently lands in `iCloud vault/产出/edu/`. Delete it first, then fix the writers — otherwise you cannot detect which scripts are still writing to old paths.

**Detection command (run after every restructure):**
```bash
# Search all 3 layers for old path patterns
for pattern in 'agent-outputs' 'MolinOS-Wiki' '02_Agent_Outputs' 'Agents/KPI' '报告/KPI看板' \
               '产出/(content|edu|finance|hermes|side|research)/' \
               '学习档案/(edu|media|global|shared|autodream)/' \
               'System/执行规范v4' 'System·' 'edu·' 'media·'; do
  echo "=== $pattern ==="
  rg -l "$pattern" ~/Molin-OS/*.md ~/.hermes/skills/*/SKILL.md \
    ~/.hermes/profiles/{edu,shared,side}/skills/*/SKILL.md 2>/dev/null
done
```

**⚠️ PITFALL: Also search `MolinOS-Wiki` alongside `agent-outputs`.** The agent-outputs path is sometimes written as `MolinOS-Wiki/agent-outputs/...` (full symlink path) rather than bare `agent-outputs/`. A grep for `agent-outputs` misses entries that use the symlink-resolved form. The 2026-05-17 follow-up found 2 such missed entries in `edu-operations-pipeline/SKILL.md` and its reference file — they used `MolinOS-Wiki/agent-outputs/edu/curriculum/` which only `MolinOS-Wiki` matched. Add `MolinOS-Wiki` to the audit pattern list.

**Also search `references/` files inside skills.** The audit patterns above only scan `SKILL.md` files, but SKILL.md's `references/<topic>.md` files can also contain old path references. Extend the search to `references/*.md` inside each skill directory.

**⚠️ PITFALL: Skipping this phase is the #1 cause of vault regression.** Fixing scripts alone is insufficient — agent skills and system docs continue to reference old paths, causing agents to recreate old directory structures on their next execution. The user explicitly asked to "清除掉旧的配置，避免重新引用" — this phase addresses that requirement.

### Daily prevention: vault_health_check.py

A reusable watchdog script at `~/Molin-OS/scripts/vault_health_check.py` enforces the final structure. It checks:

- No rogue top-level dirs (Agents/, Daily/, System/, env/)
- No root-level .md or non-md files
- No unexpected nested subdirs under category dirs
- No duplicate filenames across categories (with known-name exceptions)
- Allowed dirs match the 9 approved: 决策/知识/流程/成果/报告/配置/产出/学习档案/Archive + agent-outputs (iCloud ghost)

Run: `cd ~/Molin-OS && python3 scripts/vault_health_check.py`
Return code: 0 = clean, 1 = issues found

Since v5.11, this script ALSO runs YAML frontmatter validation (uses PyYAML to parse every .md file's frontmatter). The `skip_yaml` parameter controls this: `check(skip_yaml=True)` skips YAML for fast directory-only checks.

Wire into the 22:00复盘 cron for automatic daily enforcement, or run manually after any vault operation.
## Changelog

### v5.12 (2026-05-18)

- **Vault Git 同步桥**：解决 iCloud Drive 下 git mmap 冲突（`fatal: mmap failed: Resource deadlock avoided`）。新增 `vault_git_sync.py` 脚本（镜像桥方案 — `~/Molin-OS/.vault-git-mirror/` + rsync + 15分钟 cron）。Vault remote 从 `git@github.com` 切到 `https://github.com`（SSH port 22 被封）。
- **Pitfall 新增**：Git operations fail on iCloud Drive — 根因、症状、镜像桥方案、关联 SSH 问题。
- **参考文件更新**：`obsidian` skill `references/git-icloud-mmap-workaround.md` 新增自动化方案章节。

### v5.11 (2026-05-18)

- **YAML frontmatter validation**: Discovered 39 files with broken YAML causing Obsidian error popups (5 distinct patterns). Root-cause fixed 6 bugs across 4 write scripts (sync_memory.py source quoting, media/edu per-profile sync_memory.py frontmatter structure, collect_architecture.py `\n` escapes + v3.0 naming + overwrite bug). Added integrated YAML scan to `vault_health_check.py` (PyYAML check now runs alongside directory checks) + standalone `scripts/validate_vault_yaml.py` (with `--fix` mode) + `references/yaml-frontmatter-pitfalls.md`.
- **Phase 5 validation updated**: YAML check now runs alongside `vault_health_check.py` in the final validation step.
- **Prevention rule codified**: All YAML values with `:`, `,`, `|`, `[`, `]`, `{` must be double-quoted. Sync scripts must quote `source:` and `related:` values.

### v5.10 (2026-05-18)

- **Layer 4 audit：`~/.hermes/scripts/` 全局脚本目录** — 之前的审计遗漏此层，导致 `relay_to_obsidian.py`、`sync_memory_edu.py`、`sync_growth_full.py`、`molin-sync-all.sh` 四个写入源未被发现
- **MolinOS-Wiki symlink 删除**：symlink 将旧路径静默重定向到 iCloud vault，是 ghost 目录复活的核心机制。只要 symlink 存在，任何残留旧路径引用都会继续污染 vault
- **sync_memory.py v5.1 管道引擎升级**：添加 `BIZ_PREFIX` 映射 (`edu→元瑶, media→银月, global→梅凝, shared→玄骨, side→宋玉`)，文件名改为 `业务线｜topic.md`
- **双副本陷阱**：`relay_to_obsidian.py` 同时存在于 `~/.hermes/scripts/` 和 `~/Molin-OS/scripts/`，两处都需 patch。`sync_memory_edu.py` 同理（`~/.hermes/scripts/` vs `~/.hermes/profiles/edu/scripts/`）
- **两个旧脚本禁用**：`obsidian_sync.py` 和 `vault_compliance_check.py` → `.disabled_*`（写 `Daily/` 与 v3.0 冲突）
- **10个垃圾文件删除 + 5个文件重命名**：含 prompt 碎片文件名（`从以下URL提取文章的核心要点，返回.md`）和 `每日·` 格式文件 → 统一加 `玄骨｜` 前缀
- **参考文件新增**：`references/vault-hardening-2026-05-18.md` — 五层写入源全量审计法 + 五阶段硬化流程 + 双副本陷阱 + 13处修复清单
- **vault_health_check.py 已验证**：8目录、0子目录、0无｜文件、0旧路径引用 — ✅

### v5.9 (2026-05-17)
- **v3.0 vault 硬化完成**：8平坦目录，88文件，零不合规，零无效目录，零子目录。
- **第四层审计发现**：三层审计（Molin-OS 脚本 + Hermes 技能 + Agent 技能）不足 — `shared/bin/memory_sync.py` 和 `side/scripts/memory_sync.py` 构成被遗漏的第四层（profile bin/scripts），写入 `MolinOS-Wiki/产出/side/` 和 `MolinOS-Wiki/产出/shared/` 子目录。
- **13个活跃写入源根除**：output_writer.py（去子目录，改为 `产出/业务线｜type·date.md` 的 agent_id→业务线映射）、memory_bridge.py（iCloud 路径）、memory_sync(side/shared)（flat 命名）、start_all.sh、obsidian_reader.py、sync_memory_edu.py、vault_health_check.py（去跨目录同名误报）、5个 SKILL 文件。
- **vault_health_check.py 升级**：移除跨目录同名重复检测（v3.0 中 `决策/系统｜GitHub.md` 和 `成果/系统｜GitHub.md` 合法 — 目录即命名空间）。
- **防复发**：全量排查→根因封堵→防复发 五阶段方法论文档化（`references/vault-hardening-methodology.md` in agent-sop-template）。
- **关键反模式教训**："修一个漏一个" 是常见陷阱 — 第一次修 output_writer + memory_bridge，再扫描发现 side/shared sync，再扫描发现 start_all/sync_edu，再扫描发现 5个 SKILL。正确做法：一次性全量扫描后批量修复。

### v5.8 (2026-05-17)
- **Phase 6: Downstream Skills & Docs Audit** added to Vault Consolidation Workflow — the #1 cause of vault regression after restructuring. Covers 3 layers: Molin-OS system docs, Hermes skills, and agent profile skills.
- **YAML frontmatter repaired**: Fixed malformed `input:` block that prevented patch operations.
- **Fix audit from 2026-05-17 flattening session**: Updated 10 downstream references across 2 system docs + 8 skills after vault flattening (产出写入规范.md, SYSTEM.md, kpi-tracker, kpi-dashboard, vertical-learning-sop, gatekeeper-sop, agent-sop-template, obsidian, molin-ops, molin-memory-pipeline).

### v5.7 (2026-05-17)
- **Flat structure enforced**: All subdirectories eliminated — `产出/<profile>/`, `学习档案/<agent>/github-absorb/`, `报告/KPI看板/` are gone. 8 root dirs only, zero nesting.
- **Naming convention upgraded**: `Agent·Topic.md` → `业务线｜具体内容.md` (full-width pipe). Root directory = type, never repeated in filename. 业务线 = 系统/元瑶/银月/梅凝/宋玉/玄骨/KPI.
- **Rolling daily files**: `银月｜日报`, `宋玉｜日报`, `系统｜日报` — single persistent file per agent, updated daily. No timestamped daily files.
- **Reference added in obsidian skill**: `references/vault-naming-convention-v6.md` — authoritative naming standard.

### v5.6 (2026-05-17)

- **Agent skill-level dual-write audit**: Discovered 21 `agent-outputs/` write sources across three layers — agent-profile skills/memories/scripts/plans in edu/shared/side (15), Molin-OS shared tools/skills (3), and agent-bin scripts (3). Initial fix identified 11 sources in skills/memories; follow-up search found 10 more in scripts and plans that were missed in the first pass. All 21 fixed: `agent-outputs/` → `产出/`.
- **Three-layer audit requirement**: Vault structure fixes must now audit (1) pipeline scripts (~/Molin-OS/scripts/), (2) Molin-OS shared tools/skills (~/Molin-OS/tools/, ~/Molin-OS/skills/), and (3) agent-profile instructions (~/.hermes/profiles/{X}/skills/, memories/, scripts/, plans/). Fixing only layer 1 leaves layers 2 and 3 as silent recurrence vectors via the MolinOS-Wiki symlink.
- **Reference file updated**: `references/agent-outputs-dual-write-audit.md` — complete audit of all 21 sources with three-layer prevention pattern.

### v5.5 (2026-05-17)

- **4 script path fixes applied**: obsidian_sync.py (init_vault no longer creates Agents/Daily/System), collect_architecture.py (changed Agents/* glob to flat category iteration), sync_memory.py (changed old Agents/ dedup path to direct filepath check), generate_dashboard.py (OUTPUT_DIR from Agents/KPI看板 to 报告/KPI看板)
- **Vault consolidation workflow documented**: Added full 8-step repeatable process (Phase 0-5) with automation commands for detecting drift, fixing scripts, migrating rogue dirs, cleaning root garbage, merging duplicates, and final validation.
- **Classification boundary enforced**: All vault writes now constrained to 6 flat directories only (决策/知识/流程/成果/报告/配置).

### v5.4 (2026-05-16)

- **Cron audit & repair**: Full 7-job audit. Fixed `cross_request_worker.py` Python 3.9 `dict|None` syntax crash. Fixed `git-backup.sh` push rejection (v2.1 → fetch+rebase, v3.0 → retarget to Molin-OS main repo, remove redundant script-copy steps).
- **Step 4: Relay sync pipeline**: Added `relay_to_obsidian.py` as Step 4 of the hourly pipeline. Scans `relay/shared/results/` and `relay/side/results/` for no_agent cron outputs, parses them, and writes living documents to `知识/每日·*.md`. Uses fingerprint tracker at `~/.hermes/relay_sync_tracker.json`.
- **Cron Job Direct-Write Pattern**: Documented pattern for LLM-driven cron jobs to write directly to Obsidian vault (instead of relying on pipeline). Key: `deliver=local`, embed vault path in prompt, append to existing living docs.
- **Supported relay handlers**: arxiv daily papers (`知识/每日·Arxiv论文.md`) and side price monitor (`知识/每日·副业价格监控.md`).

### v5.3 (2026-05-16)
- **Vault structure expanded**: Added 配置/ (system architecture) and 报告/ (daily reports) as official directories alongside 决策/知识/流程/. Total 5 flat directories.
- **3 scripts repathed**:
  - `collect_architecture.py`: System/ → 配置/ (architecture.md, agents/*.md, memory-map.md)
  - `obsidian_sync.py`: Daily/ → 报告/, Agents/{agent}/category/ → {category}/
  - `sync_memory.py`: Agents/{agent}/category/ → {category}/
- **Path drift detection**: Added vault structure audit script to catch rogue dirs (Agents, System, env, Daily).
- **Reference file added**: `references/vault-path-map.md` — authoritative script-to-directory mapping for the 3 sync scripts.

### v5.2 (2026-05-16)
- **Vault restructure**: User chose 3 flat top-level directories (决策/知识/流程/) — no Agents/, Daily/, or System/. All files renamed to `Agent·Topic.md` format. Code directories (molib, scripts, skills, tools) removed from vault.
- **obsidian skill updated**: Structure description, frontmatter schema, and classification rules now reflect 3-directory layout with agent-prefixed filenames.
- **Daily/ and System/ merged**: Content from Daily/ → 知识/Daily·*.md, System/ → 流程/System·*.md.

### v5.1 (2026-05-16)
- **Agent chatter filter**: Added 23 `AGENT_CHATTER_PATTERNS` (English + Chinese) to `extract_conclusions()`. Now scans from END of conversation, skips planning monologue, prefers user-facing summaries. Fixed 20 garbled files across the vault.
- **Vault consolidation workflow**: Added 5-phase process for bulk cleanup — audit → merge duplicates → delete garbage → fix structure → parallel execution via delegate_task.
- **Cron PATH fix**: `molin-sync-all.sh` now uses absolute path `/opt/homebrew/bin/python3.11` (cron's minimal PATH can't find homebrew binaries).
- **Obsidian Git init**: Added recipe for initializing `.git` in vault when plugin reports "not a git repository".

### v5 (2026-05-15)

### sync_memory.py v5
- **Filename**: 3-tier topic extraction (专有名词 → 中英混合词提取 → 18字中文截断)，文件名非法字符自动剥离
- **Content**: 金字塔格式（结论→背景→核心内容→下一步），系统提示噪声过滤（`[IMPORTANT:`、`# Profile:` 等）
- **Session filter**: 只处理 `session_*.json` 文件，排除 `sessions.json` 和 `request_dump_*`
- **Dedup**: `sync_tracker.json` 按 (filename, mtime, size) 去重，30天过期
- **Full mode**: `SYNC_FULL=1 python3 scripts/sync_memory.py` 处理全量 session（日常模式只检查最近 10 个）
- **SM rebuild**: `/tmp/sm_rebuild.py` — 从 Obsidian 文件反向重建 Supermemory（当 SM 数据不一致时使用）

### Process
本次 v5 升级完成了：
1. 删除所有被 v4 污染的 Obsidian 文件（72+52=124 个文件修/删）
2. 清除 Supermemory 486 条旧数据
3. 处理全部 101 个 session 文件，生成 29 条规范化笔记
4. Supermemory 双写验证：29 条 v5 条目与 Obsidian 29 个文件一一对应

## Script Timing Reference

| Script | Duration | Bottleneck |
|--------|----------|------------|
| sync_memory.py | ~15-20s | Supermemory API |
| obsidian_sync.py | ~2-5s | File I/O |
| collect_architecture.py | ~25-35s | Supermemory API |
| relay_to_obsidian.py | ~1-3s | File I/O |
| Full pipeline | ~45-65s | Sum |

## Cron Job Direct-Write Pattern

For cron jobs that produce content for Obsidian (e.g. daily learning, research digests), the **direct-write pattern** is preferred over relying on the 3-script pipeline. The pipeline only scans session JSONs — if a cron job's output is delivered as a new conversation rather than a JSON session file, the pipeline won't catch it.

### When to use direct-write
- Cron job produces a **living document update** (append to existing topic file)
- Cron job generates **topical research/learning** that should go in 决策/ or 知识/
- The job's output IS the content that belongs in Obsidian

### When NOT to use (use pipeline instead)
- The output is raw data/JSON/script output
- The content needs post-processing (classification, dedup, chatter filtering)
- Multiple conversational sessions need to be aggregated

### Pattern: embed file write in cron prompt

The cron prompt itself handles both content generation AND vault write, using `deliver=local` to suppress spam delivery:

```yaml
# cronjob create example:
name: "某Agent每日学习"
schedule: "0 8 * * *"          # daily 08:00
deliver: "local"               # output stays in system, never delivered to user
prompt: |
  1. 生成每日学习内容（研究/分析/总结）
  2. 写入 Obsidian vault 对应文件：
     - Vault 路径：/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents/
     - 目标文件：{分类}/{Agent}·{Topic}.md
     - 先读取现有文件确认 frontmatter + 最新内容
     - 追加新条目（living document 模式）
     - 更新 frontmatter `updated` 日期
     - 使用金字塔格式（结论→背景→核心内容→下一步）
  3. 不输出任何内容到对话（deliver=local 已处理）
```

### Pitfalls

**Don't overwrite — append.** Always read the existing file first and append a new entry under the current date. Living document = one file per topic, growing over time.

**Frontmatter intact.** Never modify `created`, `agent`, `category`, `tags` — only update `updated`.

**deliver=local is mandatory.** Without it, the raw cron output (agent internal monologue) gets delivered to the user every run, which would become noise. `local` keeps it in the DB for debugging without spamming the user.

**Vault path hardcoding.** The vault is at iCloud path `/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents/` — always use the absolute path in the prompt, not a shell variable or alias. The cron agent has no memory, so the full path must be embedded in the prompt itself.

## Relay Output Sync Pattern

For **no_agent cron jobs** (script-only, no LLM), the direct-write pattern doesn't apply — these jobs produce raw data files in `relay/` directories. Their output reaches Obsidian through the **relay sync pipeline** (Step 4 of `molin-sync-all.sh`).

### How it works

```
no_agent cron job → writes relay/XX.json → relay_to_obsidian.py (hourly) → Obsidian living doc
```

The relay sync script (`~/Molin-OS/scripts/relay_to_obsidian.py`):
1. Scans `relay/shared/results/` and `relay/side/results/` for new JSON/text files
2. Compares each file's fingerprint (mtime_ns + size) against `~/.hermes/relay_sync_tracker.json`
3. For new/changed files: parses content, classifies it, writes/updates an Obsidian living doc
4. Updates the tracker so the same file isn't re-processed

### Supported relay types

| Relay file pattern | Handler | Obsidian target | Agent |
|-------------------|---------|-----------------|-------|
| `daily_papers_*.json` | Arxiv text parser | `知识/每日·Arxiv论文.md` | 梅凝 |
| `price_monitor_*.json` | JSON pricing parser | `知识/每日·副业价格监控.md` | 宋玉 |

### Extending for new relay types

Add a new handler function in `relay_to_obsidian.py` following the pattern:

```python
def handle_my_type(filepath: Path, tracker: dict) -> bool:
    fingerprint = file_fingerprint(filepath)
    key = f"mytype::{filepath.name}"
    if tracker.get(key) == fingerprint:
        return False
    
    # Parse file, build Obsidian entry
    # Write to VAULT / "知识" / "每日·MyType.md"
    # Return True if synced
    
    return True
```

Then register it in `main()`:
```python
for f in sorted(SOURCE_DIR.glob("mytype_*.json")):
    if handle_my_type(f, tracker):
        synced += 1
```

### Pitfalls

**Overwriting vs appending.** The first run creates the file; subsequent runs append new entries under the current date. The append logic strips the frontmatter and "# Title" header before merging, so no duplicate headers accumulate.

**Living document titles use `每日·` prefix.** Relay outputs are daily-by-nature (arxiv papers, price snapshots), so they go in `知识/每日·{Topic}.md`. This naming distinguishes them from persistent topic files in the same directory.

**File fingerprint dedup.** The tracker uses `st_mtime_ns:st_size` as fingerprint. If the same relay file is regenerated daily by cron with new content, the fingerprint changes automatically and the new content gets synced.

**Tracker file location.** `~/.hermes/relay_sync_tracker.json` — separate from `sync_memory.py`'s tracker (`~/.hermes/profiles/{agent}/sync_tracker.json`) because it tracks file outputs, not session outputs.

## Support Files

| File | Purpose |
|------|---------|
| `references/vault-path-map.md` | Authoritative script-to-directory mapping + audit commands |
| `references/vault-blueprint.md` | Complete directory tree reference |
| `references/vault-health-check.md` | Root-level rogue directory diagnosis |
| `references/sync-debugging.md` | Step-by-step debugging recipe when sync pipeline stops |
| `references/garbage-audit.md` | Detection script + fix patterns for agent-chatter-as-conclusion garbage |
| `references/memory-taxonomy.md` | L1-L4 memory taxonomy — classification, distillation path, tagging rules |
| `references/vault-naming-convention.md` | Vault root directory naming rules — Chinese-only, no numbered prefixes |
| `references/cron-audit-2026-05-16.md` | Full cron job audit: 7 jobs checked, 2 fixes applied, relay sync pattern added |
| `references/vault-consolidation-workflow.md` | Repeatable 5-phase vault cleanup with automation script |
| `references/vault-flattening-2026-05-17.md` | Complete before/after mapping of 88→75 file vault flattening (2026-05-17) — all file moves, merges, deletes, and user corrections |
| `references/vault-hardening-2026-05-18.md` | Five-layer audit methodology for comprehensive vault hardening — Layer 4 (~/.hermes/scripts/) discovery, MolinOS-Wiki symlink deletion, dual-copy trap, 13 fixes applied |
| `references/yaml-frontmatter-pitfalls.md` | 5 YAML error patterns from auto-generated files — detection regex, batch fix scripts, root cause prevention (2026-05-18) |
\n## Scripts\n
| File | Purpose |
|------|---------|
| `scripts/validate_vault_yaml.py` | Standalone YAML frontmatter validator — checks all vault .md files, supports --fix mode, exit 0=clean (2026-05-18) |

## Cross-reference

- CloakServe stealth browser: `molin-org/cloakserve`
- Cron job management: `cronjob(action='list')`