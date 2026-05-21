# Vault Consolidation Workflow (v5.5)

## Full Automation Script

Run this script after any vault drift detection. It executes the 5-phase consolidation workflow.

```python
"""
Vault Consolidation — Automated cleanup script.
Run from Molin-OS root.
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict

VAULT = Path("/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents")
SCRIPTS = Path.home() / "Molin-OS" / "scripts"

VALID_DIRS = {"决策", "知识", "流程", "成果", "报告", "配置"}
ROGUE_NAMES = {"Agents", "agent-outputs", "Daily", "System", "env", "项目", "知识库", "产出"}

def phase_0_detect():
    """Detect drift."""
    issues = []
    # Rogue dirs
    for d in sorted(VAULT.iterdir()):
        if d.is_dir() and d.name in ROGUE_NAMES:
            files = len(list(d.rglob("*.md")))
            issues.append(f"ROGUE: {d.name}/ ({files} files)")
    
    # Root files
    for f in sorted(VAULT.glob("*.md")):
        issues.append(f"ROOT: {f.name}")
    for f in sorted(VAULT.glob("Makefile")):
        issues.append(f"ROOT: {f.name}")
    for f in sorted(VAULT.glob("README*")):
        issues.append(f"ROOT: {f.name}")
    
    # Duplicate filenames
    files_map = defaultdict(list)
    for root, dirs, fnames in os.walk(VAULT):
        for f in fnames:
            if f.endswith(".md") and not f.startswith("."):
                rel = os.path.relpath(os.path.join(root, f), VAULT)
                files_map[f].append(rel)
    for name, paths in sorted(files_map.items()):
        if len(paths) > 1:
            issues.append(f"DUP: {name}: {paths}")
    
    # Script path drift
    for script in ["sync_memory.py", "obsidian_sync.py", "collect_architecture.py", "relay_to_obsidian.py"]:
        sp = SCRIPTS / script
        if sp.exists():
            content = sp.read_text()
            import re
            matches = re.findall(r'VAULT / "([^"]+)"', content)
            for m in matches:
                if m not in VALID_DIRS:
                    issues.append(f"PATH: {script} writes to '{m}' (invalid)")
    
    if not issues:
        print("✅ Vault clean.")
    else:
        print(f"⚠️  {len(issues)} issues:")
        for i in issues:
            print(f"  {i}")
    return issues


def delete_rogue_dir(name: str):
    """Safely delete a rogue directory (cp first, then rm)."""
    target = VAULT / name
    if not target.exists():
        return
    # Copy files inside to appropriate category
    for f in target.rglob("*.md"):
        cat = "知识"  # default
        content = f.read_text()
        if "决策" in content[:200] or "决定" in content[:200]:
            cat = "决策"
        elif "SOP" in content[:200] or "步骤" in content[:200]:
            cat = "流程"
        dest = VAULT / cat / f.name
        shutil.copy2(f, dest)
        print(f"  → {cat}/{f.name}")
    shutil.rmtree(target)
    print(f"  ✅ {name}/ deleted")


if __name__ == "__main__":
    issues = phase_0_detect()
    if issues:
        print("\nRun manually per phase. Use cp+rm pattern.")
```

## Workflow Summary

| Phase | Action | Command |
|-------|--------|---------|
| 0 | Detect drift | Run the Python script above |
| 1 | Fix script paths | 4 files need path corrections (see SKILL.md) |
| 2 | Migrate rogue dirs | cp → rm for agent-outputs/, Agints/KPI看板/ |
| 3 | Clean root garbage | Delete Makefile/README. Move .md to correct dir |
| 4 | Merge duplicates | Read → merge → delete (3 outcomes per pair) |
| 5 | Final validation | Re-run phase 0 detection; expect 0 issues |

## Known Pitfalls

- **Never use `mv`** — user explicitly blocks it. Always `cp` then `rm`.
- **agent-outputs/ files are agent memory dumps** — they have no frontmatter and need manual classification when moved.
- **Same-named files can be different content** — always read before merging. profile.md appears in 决策/知识/成果/ with three different topics.
- **After script fixes, restart sync_all.sh** to verify the pipeline writes to correct paths.
