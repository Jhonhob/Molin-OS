---
name: github-competitive-research
description: >-
  Find open-source alternatives to a specific tool/project on GitHub, evaluate
  them by stars, features, pricing, and platform fit. Produces a structured
  comparison with actionable recommendations.
---

# GitHub Competitive Research

Class-level skill for discovering and evaluating open-source alternatives to a given tool or project.

## When to Use

- User asks "Find alternatives to [project] on GitHub"
- User asks "What's the open-source version of [tool]?"
- Any request to compare multiple open-source projects against each other

## Step-by-Step Workflow

### 1. Locate the target project on GitHub
- Navigate to `github.com/search?q=<project-name>&type=repositories&s=stars&o=desc`
- Identify the canonical repo (highest stars, most active)
- Note if the project has moved orgs (e.g. dhravya/supermemory → supermemoryai/supermemory)

### 2. Discover alternatives
- Search GitHub with relevant keywords: `[category] alternative`, `[tool-name] alternative`, `open source [category]`
- Use star-sorted results to identify top players
- For each candidate, capture:
  - Stars count (proxy for community validation)
  - Description (what problem it solves)
  - Tech stack (Python/TypeScript/Rust)
  - License

### 3. Deep-dive evaluation
- Visit the project website (often linked in GitHub README or repo About section)
- Check pricing page for:
  - Free tier limits
  - Paid tiers and pricing
  - Self-hosted vs cloud offering
- Check for UI/UX:
  - Web dashboard?
  - Desktop client?
  - CLI tool?
  - SDK/API?

### 3a. SaaS dependency audit (critical)
Some projects claim "free & open-source" but depend on a paid cloud API to function:
- Check if the project is a thin wrapper/plugin around a commercial API (e.g. MCP server wrapping a cloud service)
- Look for terms like "API key required" in .env.example or setup docs
- Distinguish: "self-hosted" (no external dependency) vs "MCP/plugin wrapping a cloud API" (still dependent on cloud provider)
- When the README says "completely free", verify by checking the parent company's /pricing page — the free tier may have hard usage caps
- Example pattern: supermemory-mcp is itself free and open-source, but requires a Supermemory API key whose free tier ($5/mo built-in) is capped and can return 402 Payment Required

### 4. Synthesize comparison
- Structure by user interest (feature comparison, pricing, platform support)
- Star counts are rough proxies — note them but don't over-weigh
- When the user asks multiple direct questions, answer each clearly and separately

## Pitfalls

- Projects may rename or move orgs — always verify the current canonical URL
- Star counts can be gamed; cross-check commit frequency and issue activity
- Pricing pages change often — capture the current state but note "as of [date]"
- "Open source" can mean different things — check the LICENSE file
- Some projects offer a free tier that's too limited for production use
- README claims of "completely free" may omit cloud API dependency costs — always audit the pricing page of the parent SaaS
