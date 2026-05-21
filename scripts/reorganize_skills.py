#!/usr/bin/env python3
"""
Phase 1: 技能目录重组器
读取 skills-registry-v7.json，将 646 技能分流到 global/domains/workers/archive 四层目录
"""
import os, json, shutil
from collections import defaultdict

SKILLS_DIR = os.path.expanduser("~/Molin-OS/skills")
REGISTRY_JSON = os.path.expanduser("~/Molin-OS/docs/skills-registry-v7.json")

# ── 引用清单：这些技能被系统明确引用，必须保留 ──
REFERENCED_SKILLS = {
    # 从 SOUL.md 触发表提取 + Cron Job 引用 + Agent Persona 引用
    'content-sop-pack', 'content-sop-growth', 'content-sop-lead', 'content-sop-crisis',
    'gatekeeper-sop', 'kpi-tracker', 'kpi-dashboard',
    'obsidian', 'obsidian-deep-writing', 'obsidian-wiki-reader',
    'mempalace', 'molin-memory-pipeline', 'memory-bridge',
    'vertical-learning-sop',
    'finance-sop-pack', 'data-sop-pack', 'ops-sop-pack',
    'security-sop-pack', 'legal-sop-pack',
    'research-sop-pack', 'developer-sop-pack', 'design-sop-pack',
    'video-sop-pack', 'voice-sop-pack', 'service-sop-pack',
    'education-sop-pack', 'ecommerce-sop-pack', 'ip-sop-pack',
    'bd-sop-pack', 'global-marketing-sop-pack', 'crm-sop-pack',
    'molin-github', 'molin-system-architecture', 'molin-ops',
    'autodream-sop-pack',
    'agent-sop-template',
    'hermes-agent', 'hermes-agent-skill-authoring',
    'xiaohongshu-content-engine', 'xhs-ai-publisher',
    'xianyu-automation', 'zhubajie-automation',
    'baoyu-article-illustrator', 'baoyu-comic', 'baoyu-infographic',
    'humanizer', 'ideation',
    'feishu-cli', 'feishu-message-formatter', 'feishu-card-router',
    'cli-anything',
    'heartmula', 'songwriting-and-ai-music',
    'youtube-content', 'ascii-art', 'ascii-video', 'pixel-art',
    'excalidraw', 'sketch', 'claude-design',
    'comfyui', 'manim-video',
    'arxiv', 'blogwatcher', 'last30days', 'polymarket',
    'mirofish-engine', 'mirofish-trends',
    'trading-agents-pattern', 'freqtrade-trading-engine',
    'notebooklm-integration', 'gateway-connectivity-diagnostics',
    'free-proxy-aggregation',
    'systematic-debugging', 'writing-plans', 'plan',
    'spike', 'test-driven-development', 'subagent-driven-development',
    'requesting-code-review', 'python-debugpy', 'node-inspect-debugger',
    'codebase-inspection',
    'github-auth', 'github-code-review', 'github-issues',
    'github-pr-workflow', 'github-repo-management',
    'huggingface-hub', 'llama-cpp', 'ollama', 'vllm',
    'nano-pdf', 'ocr-and-documents', 'powerpoint',
    'airtable', 'linear', 'notion', 'google-workspace',
    'maps', 'spotify', 'gif-search',
    'himalaya', 'imessage', 'apple-notes', 'apple-reminders', 'findmy',
    'open-hue', 'pokemon-player', 'minecraft-modpack-server',
    'songsee',
    'jupyter-live-kernel', 'dspy', 'evaluating-llms-harness',
    'weights-and-biases',
    'segment-anything-model', 'audiocraft-audio-generation',
    'godmode', 'darwinian-evolver',
    'pretext', 'design-md', 'popular-web-designs',
    'molin-org', 'cloakserve', 'crm-private-domain',
    'kanban-orchestrator', 'kanban-worker', 'kanban-codex-lane',
    'webhook-subscriptions',
}

# ── 墨麟定制技能 (molin-* / edu / media / side / global dirs) ──
MOLIN_CUSTOM_PREFIXES = (
    'molin-', 'molin_',
    'edu/', 'media/', 'side/', 'global/',
    'feishu-', 'feishu_',
    'baoyu-', 'baoyu_',
    'autodream-',
    'cloakserve',
    'crm-private-domain',
    'content-sop-', 'data-sop-', 'design-sop-', 'developer-sop-',
    'education-sop-', 'ecommerce-sop-', 'finance-sop-', 'gatekeeper-sop-',
    'ip-sop-', 'legal-sop-', 'ops-sop-', 'research-sop-',
    'security-sop-', 'service-sop-', 'video-sop-', 'voice-sop-',
    'bd-sop-', 'global-marketing-',
    'agent-sop-template',
    'harmonist-stop-gate',
    'ouroboros-spec-engine',
    'agentic-stack-portable-brain',
    'molin-', 'notebooklm-integration',
    'free-proxy-aggregation',
    'mirofish-',
    'trading-agents-', 'freqtrade-trading-engine',
    'mempalace',
    'integuru-har-agent',
    'project-selfhost-analysis',
    'macos-computer-use',
    'xhs-ai-publisher',
    'xianyu-automation',
    'zhubajie-automation',
    'taiwan-',
    'xiaohongshu-content-engine',
    'cli-anything',
    'kanban-',
    'cron-output-formatter',
    'heartmula',
    'hermes-agent-skill-authoring',
    'debugging-hermes-tui-commands',
    'batch-yaml-frontmatter-injection',
    'feishu-card-router',
    'feishu-cli-shared',
)

# ── Company directory mapping ──
COMPANY_DIRS = {
    '玄骨_xuangu': 'global',
    '紫灵_ziling': 'domains/ziling_intelligence',
    '银月_yinyue': 'domains/yinyue_content',
    '元瑶_yuanyao': 'domains/yuanyao_education',
    '梅凝_meining': 'domains/meining_outbound',
    '宋玉_songyu': 'domains/songyu_business',
}


def is_referenced(entry):
    """Check if a skill is in the referenced list."""
    dirname = entry['dirname']
    return dirname in REFERENCED_SKILLS


def is_molin_custom(entry):
    """Check if a skill is Molin-OS custom (not hub-installed)."""
    dirname = entry['dirname']
    filepath = entry['filepath']
    
    # Check by directory prefix
    if dirname.startswith(MOLIN_CUSTOM_PREFIXES):
        return True
    if filepath.startswith(MOLIN_CUSTOM_PREFIXES):
        return True
    
    # Check by metadata source
    source = entry['meta'].get('_source', '')
    if source == 'local':
        return True
    
    return False


def main():
    registry_path = REGISTRY_JSON
    if not os.path.exists(registry_path):
        print(f"❌ 注册表不存在: {registry_path}")
        print("   请先运行: python3 scripts/generate_registry.py")
        return
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    print(f"📋 加载 {len(registry)} 个技能")
    
    # Categorize
    active = []
    archive = []
    
    for entry in registry:
        if is_referenced(entry) or is_molin_custom(entry):
            active.append(entry)
        else:
            archive.append(entry)
    
    print(f"\n{'='*50}")
    print(f"  分类结果:")
    print(f"  🟢 活跃 (保留): {len(active)}")
    print(f"  🟡 归档 (archive/): {len(archive)}")
    print(f"{'='*50}")
    
    # Create target directories
    os.makedirs(os.path.join(SKILLS_DIR, 'archive'), exist_ok=True)
    for comp_dir in COMPANY_DIRS.values():
        os.makedirs(os.path.join(SKILLS_DIR, comp_dir), exist_ok=True)
    # workers/ will be created on demand
    
    # DRY RUN first
    print("\n🔍 模拟执行 (DRY RUN) — 不实际移动文件\n")
    
    moves = []
    for entry in active:
        company = entry.get('classified_company', '玄骨_xuangu')
        target_dir = COMPANY_DIRS.get(company, 'global')
        worker = entry.get('classified_worker', '墨维')
        
        # For skills that map to specific workers (not generic), put in workers/
        generic_workers = {'墨维', '墨码'}
        if worker not in generic_workers and company == '玄骨_xuangu':
            target_dir = f'workers/{worker}'
        
        src = entry['filepath']
        dst = f"{target_dir}/{entry['dirname']}"
        moves.append(('🟢', src, dst))
    
    for entry in archive:
        src = entry['filepath']
        dst = f"archive/{entry['dirname']}"
        moves.append(('🟡', src, dst))
    
    # Show preview
    for tag, src, dst in sorted(moves, key=lambda x: x[2])[:30]:
        print(f"  {tag} {src} → {dst}")
    
    print(f"\n  ... 共 {len(moves)} 次移动操作")
    
    # Confirm
    print(f"\n⚠️  将移动 {len(moves)} 个技能目录。")
    response = input("   继续? (y/N): ").strip().lower()
    if response != 'y':
        print("   已取消。")
        return
    
    # Execute moves
    print("\n🚀 执行移动...")
    for tag, src, dst in sorted(moves, key=lambda x: x[2]):
        src_path = os.path.join(SKILLS_DIR, src)
        dst_path = os.path.join(SKILLS_DIR, dst)
        
        if not os.path.exists(src_path):
            print(f"   ⚠️ 源不存在: {src}")
            continue
        
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        
        if os.path.exists(dst_path):
            print(f"   ⚠️ 目标已存在: {dst}")
            continue
        
        shutil.move(src_path, dst_path)
        print(f"   {tag} {src} → {dst}")
    
    print(f"\n✅ 完成! {len(active)} 活跃 + {len(archive)} 归档")
    
    # Clean up empty parent dirs
    for root, dirs, files in os.walk(SKILLS_DIR, topdown=False):
        if root == SKILLS_DIR:
            continue
        if not dirs and not files:
            try:
                os.rmdir(root)
            except:
                pass


if __name__ == '__main__':
    main()
