#!/usr/bin/env python3
"""
validate_vault_yaml.py — Validate YAML frontmatter in all Obsidian vault .md files.

Checks:
  1. All .md files have valid YAML frontmatter (no parse errors)
  2. No unquoted wiki-links in `related:` field
  3. No `\n` escape artifacts (single-line files)
  4. No duplicate frontmatter keys

Usage:
  python3 scripts/validate_vault_yaml.py
  python3 scripts/validate_vault_yaml.py --quiet   # exit code only
  python3 scripts/validate_vault_yaml.py --fix      # auto-fix known patterns

Exit: 0 = clean, 1 = issues found
"""
import os, sys, re, glob, yaml

VAULT = os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents")

def find_files():
    """Return list of .md files in vault, excluding .obsidian/ and .trash/."""
    files = []
    for f in glob.glob(f"{VAULT}/**/*.md", recursive=True):
        rel = os.path.relpath(f, VAULT)
        if rel.startswith('.obsidian/') or rel.startswith('.trash/'):
            continue
        files.append(f)
    return files

def check_file(filepath, quiet=False, fix=False):
    """Check one file. Returns list of (type, message) issues."""
    rel = os.path.relpath(filepath, VAULT)
    issues = []
    
    try:
        with open(filepath, 'r') as f:
            raw = f.read()
    except Exception as e:
        return [("READ_ERROR", str(e))]
    
    # Check for \n escapes (file is mostly on one line with literal \n)
    newline_count = raw.count('\n')
    esc_count = raw.count('\\n')
    if esc_count > 10 and newline_count < esc_count // 2:
        if fix:
            fixed = raw.replace('\\n', '\n')
            with open(filepath, 'w') as f:
                f.write(fixed)
            issues.append(("ESCAPED", "FIXED — unescaped \\n"))
        else:
            issues.append(("ESCAPED", f"Literal \\n escapes ({esc_count} found, {newline_count} real newlines)"))
        return issues
    
    if not raw.startswith('---'):
        return issues  # no frontmatter
    
    end = raw.find('\n---\n', 1)
    if end == -1:
        end = raw.find('\n---', 3)
    if end == -1:
        issues.append(("NO_CLOSE", "No closing ---"))
        return issues
    
    fm = raw[4:end]
    
    # Check YAML validity
    try:
        yaml.safe_load(fm)
    except yaml.YAMLError as e:
        msg = str(e).split('\n')[0][:120]  # first line only
        issues.append(("YAML_ERROR", msg))
    
    # Check for unquoted related: with wiki-links
    if re.search(r'^related:\s*(?!["\'])\[\[', fm, re.MULTILINE):
        if fix:
            # Apply fix: wrap entire related value in quotes
            with open(filepath, 'r') as f:
                full = f.read()
            new = re.sub(r'^(related:\s*)(?!["\'])(\[\[.+)$', r'\1"\2"', full, flags=re.MULTILINE)
            with open(filepath, 'w') as f:
                f.write(new)
            issues.append(("RELATED_UNQUOTED", "FIXED — quoted wiki-link value"))
        else:
            issues.append(("RELATED_UNQUOTED", "Wiki-link in related: field not quoted"))
    
    # Check for unquoted source: with value containing : or |
    if re.search(r'^source:\s*(?!["\']).*[:|].*$', fm, re.MULTILINE):
        if fix:
            with open(filepath, 'r') as f:
                full = f.read()
            new = re.sub(r'^(source:\s*)(?!["\'])(.+[:|].+)$', r'\1"\2"', full, flags=re.MULTILINE)
            with open(filepath, 'w') as f:
                f.write(new)
            issues.append(("SOURCE_UNQUOTED", "FIXED — quoted source value with special chars"))
        else:
            issues.append(("SOURCE_UNQUOTED", "source: field contains : or | without quotes"))
    
    # Check duplicate keys
    keys = re.findall(r'^(\w[\w_-]*)\s*:', fm, re.MULTILINE)
    seen = set()
    for k in keys:
        if k in seen:
            issues.append(("DUP_KEY", f"Duplicate key '{k}'"))
            break
        seen.add(k)
    
    return issues

def main():
    quiet = '--quiet' in sys.argv
    fix = '--fix' in sys.argv
    
    if not os.path.isdir(VAULT):
        print(f"ERROR: Vault not found at {VAULT}")
        sys.exit(2)
    
    files = find_files()
    if not quiet:
        print(f"Scanning {len(files)} .md files in vault...")
    
    total_issues = 0
    files_with_issues = 0
    
    for f in sorted(files):
        issues = check_file(f, quiet=quiet, fix=fix)
        if issues:
            files_with_issues += 1
            for typ, msg in issues:
                total_issues += 1
                if not quiet:
                    rel = os.path.relpath(f, VAULT)
                    print(f"  [{typ}] {rel}: {msg}")
    
    if total_issues == 0:
        if not quiet:
            print(f"✅ All {len(files)} files have valid YAML frontmatter")
        sys.exit(0)
    else:
        if not quiet:
            print(f"\n❌ {total_issues} issues in {files_with_issues} files")
        sys.exit(1)

if __name__ == '__main__':
    main()
