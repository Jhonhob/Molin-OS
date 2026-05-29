# Hacker News & Product Hunt Daily Report
**Date**: Tuesday, May 26, 2026
**Focus**: AI/ML, Software Development, Programming Tools

---

## HACKER NEWS — Top Technical Stories

### 1. [488 pts | 192 comments] Using AI to Write Better Code More Slowly
**URL**: https://nolanlawson.com/2026/05/25/using-ai-to-write-better-code-more-slowly/
**HN**: https://news.ycombinator.com/item?id=48272984

Nolan Lawson argues LLMs are not just for fast slop-code — they can write higher-quality code more deliberately. Key insight: run multiple AI agents (Claude, Codex, Cursor Bugbot) to review PRs for bugs ranked by severity. Challenges the "AI = speed over quality" narrative.

### 2. [236 pts | 142 comments] Norway's 2PB Huawei Flash Storage for LLM Training
**URL**: https://www.blocksandfiles.com/flash/2026/05/22/norways-2-petabytes-of-huawei-flash-storage-and-llm-training/5244910
**HN**: https://news.ycombinator.com/item?id=48270770

Norway deploying 2PB of Huawei flash storage for LLM training. Intersection of geopolitics, hardware infrastructure, and large-scale ML.

### 3. [162 pts | 195 comments] Nobody Cracks Open a Programming Book Anymore
**URL**: https://unix.foo/posts/nobody-cracks-open-a-programming-book/
**HN**: https://news.ycombinator.com/item?id=48273030

Reflection on how modern devs learn — moving from in-depth books to quick tutorials, AI chat, and Stack Overflow. Sparks debate on depth vs. speed in developer education.

### 4. [150 pts | 52 comments] C Extensions, Portability, and Alternative Compilers
**URL**: https://lemon.rip/w/6-c-extensions-compilers/
**HN**: https://news.ycombinator.com/item?id=48267126

Deep technical dive on challenges of writing a C compiler that can process real-world code. Examines how glibc and system headers rely on GCC/Clang-specific extensions (packed structs, builtins, inline assembly). Very relevant for language tooling work.

### 5. [149 pts | 186 comments] Does Anybody Like React?
**URL**: https://jsx.lol
**HN**: https://news.ycombinator.com/item?id=48274074

Curated collection of React criticism: JS-heavy approaches hurting performance, CVE-2025-55182 (React Server Components RCE), hydration anti-patterns, and the argument that React "won by default" stifling frontend innovation.

### 6. [129 pts | 59 comments] CVE-2026-28952 — macOS Kernel Vuln Found by Claude
**URL**: https://support.apple.com/en-us/127115
**HN**: https://news.ycombinator.com/item?id=48273169

A macOS kernel vulnerability discovered by Claude (Anthropic's AI model). Significant milestone — an AI finding a real kernel-level CVE in a major OS. Raises questions about AI-assisted vulnerability research and automated security auditing.

### 7. [79 pts | 34 comments] Show HN: Write BPF Programs in Go, Not C
**URL**: https://github.com/boratanrikulu/gobee
**HN**: https://news.ycombinator.com/item?id=48225338

Gobee lets developers write eBPF programs using Go instead of C. Lowers barrier for kernel-level programming with Go's tooling and safety guarantees.

### 8. [68 pts | 35 comments] The User Is Visibly Frustrated — Coding Agent UX
**URL**: https://pscanf.com/s/354/
**HN**: https://news.ycombinator.com/item?id=48275059

Analysis of why coding agents are infuriating: they behave enough like human colleagues to trigger social expectations, but don't learn from mistakes or take responsibility. Repeated errors feel personally frustrating despite them being just algorithms. Essential reading for AI tool builders.

### 9. [54 pts | 32 comments] Performance of Rust Language [PDF]
**URL**: https://github.com/yugr/rust-slides/
**HN**: https://news.ycombinator.com/item?id=48273147

Technical presentation on Rust performance: zero-cost abstractions, compile-time optimizations, benchmark comparisons.

### 10. [50 pts | 7 comments] Show HN: OpenBrief — Local-First Video Summarizer
**URL**: https://github.com/tantara/openbrief
**HN**: https://news.ycombinator.com/item?id=48272393

Privacy-preserving, local-first tool for downloading and generating AI summaries of video content.

---

## SHOW HN — Notable Tech Projects (Today)

| Project | Pts | Description |
|---------|-----|-------------|
| Geomatic — command-driven geometry studio with autodiff | 65 | https://www.tinyvolt.com/geomatic |
| OpenBrief — local-first video downloader/summarizer | 51 | https://github.com/tantara/openbrief |
| Volt — frontend tooling for Phoenix running inside BEAM | 19 | https://github.com/elixir-volt/volt |
| Fungible — terminal personal finance app | 11 | https://github.com/tomfunk/fungible |
| PhoneDiffusion — local AI image generation for iOS | 10 | Apple App Store (id6762061991) |
| YourMemory — persistent memory layer for AI agents | 9 | HN item 48270325 |
| Cursed Browser — VLM reads HTML, hallucinates page | 6 | https://github.com/scosman/cursed_browser |
| Debugging Challenge for the AI Coding Age | 5 | https://theincidentchallenge.com/ |
| docs-cli — project state for coding agents | 5 | https://artrichards.github.io/agent-playbook-suite/blog/ |
| skills-for-humanity — 171 reasoning skills for Claude Code | 4 | https://github.com/human-avatar/skills-for-humanity |

---

## PRODUCT HUNT
**Could not access** — Product Hunt is fully behind Cloudflare challenge pages. API requires OAuth authentication not available in this environment.

**Attempted**: GraphQL API v2 (401 Unauthorized), REST API v1 (Cloudflare), homepage (Cloudflare), daily leaderboard (Cloudflare), RSS feed (stale entries only).

**Recommendation**: Provide a Product Hunt API OAuth token or use a headless browser/rendering service for future runs.

---

## KEY TAKEAWAYS

1. **AI finding kernel CVEs**: Claude discovered CVE-2026-28952 — a real macOS kernel vulnerability. This is a milestone for AI-assisted security research.

2. **AI coding quality debate**: "Using AI to Write Better Code More Slowly" (488 pts) argues AI can write quality code deliberately, challenging the slop-generation narrative. Heavy HN discussion.

3. **Coding agent UX is broken**: "The User Is Visibly Frustrated" (68 pts) diagnoses the social-illusion problem — coding agents trigger human expectations but can't meet them.

4. **BPF in Go**: Gobee brings eBPF to Go developers, lowering the barrier for kernel-level tooling. Important for observability and networking tooling.

5. **React backlash**: "Does Anybody Like React?" (149 pts) is a major debate on frontend framework fatigue, with a cited RCE vulnerability in React Server Components.

6. **New AI agent tooling**: YourMemory (persistent memory for agents), skills-for-humanity (171 reasoning skills for Claude Code), and docs-cli (project state for coding agents) all target the growing AI agent ecosystem.

7. **C compiler portability**: Deep technical article on C extensions and alternative compilers — shows how even basic system headers break on non-GCC/Clang compilers.
