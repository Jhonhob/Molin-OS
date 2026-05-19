# Agent Chatter Garbage Audit Recipe

Used 2026-05-16 to detect 20 of 51 vault files with sync_memory.py v5 garbage extraction.
Fixed in v5.1 (Molin-OS:ede3327).

## Detection Script

```python
import os, re

VAULT = "/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents"

garbage = []
for agent in ['media', 'shared', 'edu', 'side', 'global']:
    for cat in ['决策', '知识', '流程', '成果']:
        cat_path = os.path.join(VAULT, 'Agents', agent, cat)
        if not os.path.exists(cat_path): continue
        for fname in os.listdir(cat_path):
            if not fname.endswith('.md'): continue
            fpath = os.path.join(cat_path, fname)
            with open(fpath) as f: content = f.read()
            issues = []
            if 'Let me ' in content[:500] and '### 结论' in content:
                issues.append('agent chatter as conclusion')
            if '[IMPORTANT:' in content:
                issues.append('system prompt in body')
            if '### 核心内容' in content:
                bp = content.split('### 核心内容')
                if len(bp) > 1 and (bp[1][:200].strip().startswith('- Let me') or bp[1][:200].strip().startswith('- Now')):
                    issues.append('agent chatter as core content')
            parts = content.split('---', 2)
            if len(parts) >= 3 and parts[2].count('---') > 2:
                issues.append('frontmatter-in-body')
            if issues:
                garbage.append((agent, cat, fname, issues))
```

## Garbage File Types

### Type A: Agent chatter as conclusion
- `### 结论` starts with "Let me start by...", "I'll clone...", "Now I have..."
- `### 核心内容` is bullet list of agent internal steps
- `### 下一步` has garbled fragments
- **Origin**: sync_memory.py v5 extracted first 3 lines of planning messages
- **Fix**: Delete file (content elsewhere) or rewrite with real conclusions

### Type B: Frontmatter-in-body
- Body contains stray `---` that parsers confuse with YAML delimiters
- From subagent-created files using `---` as horizontal rule
- **Fix**: Replace body `---` with `***`

### Type C: System prompt leakage
- `[IMPORTANT:...`, `--- name: skill-name`, `# Profile:` in body
- **Origin**: filter_noise() missed multi-line prompts
- **Fix**: Strip or rewrite

## v5.1 Fix
- 23 `AGENT_CHATTER_PATTERNS` (English + Chinese) added to sync_memory.py
- extract_conclusions() now scans from END, skips planning monologue
- Future sync runs no longer produce Type A garbage
