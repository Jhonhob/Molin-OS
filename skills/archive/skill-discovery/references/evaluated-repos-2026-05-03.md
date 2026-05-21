# Evaluated Repos — 2026-05-03 Session

Full evaluation of 24 GitHub repos requested by 尹建业 (Feishu DM). See conversation for context.

## Tier 1 — Directly Integrated (7)

| # | Repo | Converted To | Notes |
|---|------|-------------|-------|
| 1 | `shanraisshan/claude-code-best-practice` | `agentic-engineering` | Subagent patterns, skill composition, orchestration workflow |
| 2 | `forrestchang/andrej-karpathy-skills` | `karpathy-coding-principles` | 4 principles: think first, simplicity, surgical, goal-driven |
| 3 | `mvanhorn/last30days-skill` | `last30days` | Social engagement search across Reddit/HN/YT/TikTok/X |
| 4 | `phuryn/pm-skills` | 49 `pm-*` skills | Product management frameworks (PRD, SWOT, TAM/SAM/SOM, etc.) |
| 5 | `msitarzewski/agency-agents` | 23 `agent-*` skills | AI expert personas (marketing, engineering, product, sales) |
| 6 | `sickn33/antigravity-awesome-skills` | 39 `ag-*` skills | 1,443 skills → curated 39 most general-purpose |
| 7 | `VoltAgent/awesome-openclaw-skills` | `openclaw-skills-reference` | 5,400+ skills — reference catalog only (OpenClaw-specific) |

## Tier 2 — Reference Only (4)

| Repo | Value |
|------|-------|
| `Yeachan-Heo/oh-my-claudecode` | Multi-agent orchestration patterns |
| `Yeachan-Heo/oh-my-codex` | Codex workflow patterns ($ralplan, $team) |
| `moye-tech/GenericAgent` | Self-evolving agent architecture (~3K lines) |
| `KimYx0207/Claude-Code-x-OpenClaw-Guide-Zh` | Chinese tutorial reference (130K words) |

## Tier 3 — Skipped (13)

| Repo | Reason |
|------|--------|
| `openclaw/openclaw` | Direct Hermes competitor |
| `win4r/ClawTeam-OpenClaw` | OpenClaw ecosystem |
| `ultraworkers/claw-code` | OpenClaw sub-tool |
| `Panniantong/Agent-Reach` | OpenClaw extension |
| `claude-code-best/claude-code` | Unclear mirror/wrapper |
| `paperclipai/paperclip` | 404 — repo deleted |
| `thedotmack/claude-mem` | Hermes has built-in memory |
| `moye-tech/claude-mem` | Same — memory fork |
| `supermemoryai/supermemory` | External service — decommissioned |
| `NousResearch/hermes-agent` | The platform we run on |
| `jackwener/OpenCLI` | Alpha toy, 0 stars, no anti-bot |
| `jackwener/xiaohongshu-cli` | Beta, no DM support, last commit June 2025 |
| `lightpanda-io/browser` | Experimental, pre-1.0 |

## Previously Evaluated (from round 1)

| Tool | Verdict |
|------|---------|
| `hacksider/Deep-Live-Cam` | Works for face-swap video but needs GPU + manual GUI |
| `lightpanda-io/browser` | Experimental Zig browser, not production-ready |
| `jackwener/xiaohongshu-cli` | Beta, cookie-only auth, no DMs, stale since June 2025 |
| `jackwener/OpenCLI` | Alpha, 0 stars, dead since Dec 2025 |

## Key Lessons
- Large repos with SVGs/GIFs time out — use sparse checkout or API tree listing
- Xiaohongshu tools decay fast — anti-bot evolves weekly
- OpenClaw skills are not directly convertible — format differs from Hermes SKILL.md
- Batch import works best with execute_code, not subagents (subagents time out on 50+ file ops)
