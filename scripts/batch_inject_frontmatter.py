#!/usr/bin/env python3
"""
Phase 2: 批量 Frontmatter 注入器
读取 skills-registry-v7.json 的分类结果，为所有 646 个 SKILL.md 注入标准化 Frontmatter
"""
import os, json, re
from pathlib import Path

SKILLS_DIR = os.path.expanduser("~/Molin-OS/skills")
REGISTRY_JSON = os.path.expanduser("~/Molin-OS/docs/skills-registry-v7.json")

def load_registry():
    with open(REGISTRY_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_frontmatter(entry):
    """Build standardized YAML frontmatter from registry entry."""
    meta = entry['meta']
    dirname = entry['dirname']
    
    # Determine fields
    skill_id = meta.get('skill_id', f"{dirname}_v1")
    name = meta.get('name', dirname)
    desc = meta.get('description', '')
    if not desc and 'metadata' in meta:
        desc = meta['metadata'].get('description', desc)
    
    domain = entry.get('classified_company', '玄骨_xuangu').split('_')[1] if '_' in entry.get('classified_company', '') else 'xuangu'
    worker = entry.get('classified_worker', '墨维')
    
    # Extract or build intent_tags
    existing_tags = meta.get('intent_tags', [])
    if not isinstance(existing_tags, list):
        existing_tags = []
    hermes_tags = meta.get('metadata', {}).get('hermes', {}).get('tags', [])
    if isinstance(hermes_tags, list):
        existing_tags = list(set(existing_tags + hermes_tags))
    
    # Auto-generate tags if empty
    if not existing_tags:
        name_lower = name.lower() if name else ''
        desc_lower = desc.lower() if desc else ''
        # Extract capitalized words as tag candidates
        words = re.findall(r'[\u4e00-\u9fff]+|[A-Z][a-z]+|[a-z]+', f"{name_lower} {desc_lower}")
        existing_tags = [w for w in words[:5] if len(w) > 2 and w not in ['the', 'and', 'for', 'with', 'use', 'this']]
    
    # Build YAML
    lines = ['---']
    lines.append(f'skill_id: "{skill_id}"')
    lines.append(f'name: "{name}"')
    if desc:
        lines.append(f'description: "{desc[:120]}"')
    lines.append(f'owner_domain: "{domain}"')
    lines.append(f'owner_worker: "{worker}"')
    if existing_tags:
        tags_str = json.dumps(existing_tags, ensure_ascii=False)
        lines.append(f'intent_tags: {tags_str}')
    lines.append(f'version: "{meta.get("version", "1.0.0")}"')
    lines.append(f'status: "{meta.get("status", "active")}"')
    lines.append('---')
    
    return '\n'.join(lines)

def main():
    print("📋 加载注册表...")
    registry = load_registry()
    print(f"   总计 {len(registry)} 个技能")
    
    updated = 0
    created = 0
    skipped = 0
    
    for entry in registry:
        filepath = os.path.join(SKILLS_DIR, entry['filepath'])
        if not os.path.exists(filepath):
            print(f"   ⚠️ 文件不存在: {entry['filepath']}")
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_fm = build_frontmatter(entry)
        
        if content.startswith('---'):
            # Has existing frontmatter → replace it
            end = content.find('---', 3)
            if end < 0:
                print(f"   ⚠️ Broken FM: {entry['filepath']}")
                continue
            
            body = content[end+3:].strip()
            
            # Check if already has owner_domain
            if 'owner_domain' in content[:end]:
                skipped += 1
                continue
            
            new_content = new_fm + '\n\n' + body + '\n'
            updated += 1
        else:
            # No frontmatter → prepend
            new_content = new_fm + '\n\n' + content.strip() + '\n'
            created += 1
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    print(f"\n✅ 完成:")
    print(f"   追加 owner_domain: {updated}")
    print(f"   创建 Frontmatter: {created}")
    print(f"   已合规跳过: {skipped}")

if __name__ == '__main__':
    main()
