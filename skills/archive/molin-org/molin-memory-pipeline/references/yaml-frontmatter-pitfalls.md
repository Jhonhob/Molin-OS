# YAML Frontmatter Pitfalls — Obsidian Vault

> Discovered 2026-05-18 during comprehensive audit. All patterns come from auto-generated
> files produced by sync_memory.py, collect_architecture.py, or agent-level scripts.

## 5 YAML Error Patterns (ranked by frequency)

### Pattern 1: Unquoted colon in value (33 files)
```yaml
# ❌ YAML sees "对话" as a key and "session_xxx" as a block mapping continuation
source: 对话: session_20260518_090239_
# ✅ Fix: quote the entire value
source: "对话: session_20260518_090239_"
```
**Detection regex**: `^source:\s*对话:` (any line with two unquoted `:` in value)

### Pattern 2: Multiple colons in value (1 file)
```yaml
# ❌ Multiple colons break YAML mapping
source: 系统审计: 2026-05-16 17:38 + 仓库标准化: 18:00
# ✅ Fix: quote
source: "系统审计: 2026-05-16 17:38 + 仓库标准化: 18:00"
```

### Pattern 3: Pipe + colon in value (1 file)
```yaml
# ❌ YAML interprets `|` as literal block scalar, then `:` breaks again
source: repo1, repo2 | 对话: session_20260515_181347
# ✅ Fix: quote
source: "repo1, repo2 | 对话: session_20260515_181347"
```

### Pattern 4: Wiki-links in related field (2 files)
```yaml
# ❌ Wiki-link `[[...]]` with commas breaks YAML block mapping
related: [[KPI｜日报·2026-05-17]], [[银月｜内容经营复盘·2026-05-17]]
# ✅ Fix: quote entire value
related: "[[KPI｜日报·2026-05-17]], [[银月｜内容经营复盘·2026-05-17]]"
```
**Detection regex**: `^related:\s*(?!["\'])\[\[` (unquoted `related:` with wiki-link)

### Pattern 5: Single-line \n escapes (2 files)
```
---\ndate: 2026-05-17\nagent: system\n...
```
The entire file is one line with literal `\n` strings. Caused by collect_architecture.py writing
a JSON-escaped string instead of actual newlines.

**Fix**: `content.replace('\\n', '\n')` — unescape all literal `\n` to real newlines.

## Detection Script

```bash
cd "$VAULT" && python3 << 'PYEOF'
import os, yaml, glob

for f in glob.glob("**/*.md", recursive=True):
    with open(f) as fh:
        raw = fh.read()
    
    # Check for \n escapes (file is mostly on one line)
    if raw.count('\\n') > 10 and raw.count('\n') < 5:
        print(f"[ESCAPED] {f}")
        continue
    
    if not raw.startswith('---'):
        continue
    
    end = raw.find('\n---\n', 1)
    if end == -1:
        end = raw.find('\n---', 3)
    if end == -1:
        print(f"[NO_CLOSE] {f}")
        continue
    
    fm = raw[4:end]
    try:
        yaml.safe_load(fm)
    except yaml.YAMLError as e:
        print(f"[YAML] {f}: {e}")
PYEOF
```

## Batch Fix Script

```bash
cd "$VAULT" && python3 << 'PYEOF'
import os, re, glob

for f in glob.glob("**/*.md", recursive=True):
    with open(f) as fh:
        content = fh.read()
    
    if not content.startswith('---'):
        continue
    
    end = content.find('---', 3)
    if end == -1:
        continue
    
    fm = content[3:end]
    body = content[end+3:]
    changed = False
    
    # Fix 1: source: 对话: → "对话:"
    new_fm, n = re.subn(r'^(source:\s*)(对话:.+)$', r'\1"\2"', fm, flags=re.MULTILINE)
    if n > 0:
        fm, changed = new_fm, True
    
    # Fix 2: related: [[...]] → "[[...]]"
    new_fm, n = re.subn(r'^(related:\s*)(?!["\'])(\[\[.+)$', r'\1"\2"', fm, flags=re.MULTILINE)
    if n > 0:
        fm, changed = new_fm, True
    
    if changed:
        with open(f, 'w') as fh:
            fh.write('---' + fm + '---' + body)
        print(f"Fixed: {f}")

# Fix 3: \n-escaped files
for f in glob.glob("**/*.md", recursive=True):
    with open(f) as fh:
        raw = fh.read()
    if raw.count('\\n') > 10 and raw.count('\n') < 5:
        fixed = raw.replace('\\n', '\n')
        with open(f, 'w') as fh:
            fh.write(fixed)
        print(f"Unescaped: {f}")
PYEOF
```

## Root Cause Prevention

The auto-generation scripts that produce files with YAML-unfriendly values need quoting:

| Script | Field | Fix |
|--------|-------|-----|
| `sync_memory.py` | `source: "{type}: {session_id}"` | Already fixed in most cases; check if quoting wraps the full value |
| `collect_architecture.py` | File write uses `\n` | Write with real newlines, not escaped strings |
| Any script writing `related:` | Wiki-link values | Always quote values containing `[[`, `]]`, or `,` |
| Any script writing `source:` | Any value | Always quote if value contains `:`, `|`, or `,` |

## Key Principle

**Any YAML frontmatter value containing `:`, `,`, `|`, `[`, `]`, or `{` must be quoted with double quotes.** Single-line unquoted strings in YAML are only safe for simple alphanumeric values.
