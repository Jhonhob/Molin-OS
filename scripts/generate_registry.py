#!/usr/bin/env python3
"""
墨麟OS v7.0 · 技能注册表自动生成器
扫描 skills/ 所有 SKILL.md，提取 Frontmatter，按六司+Worker 分类输出 Markdown 表格
"""
import os, yaml, json
from pathlib import Path
from collections import defaultdict

SKILLS_DIR = os.path.expanduser("~/Molin-OS/skills")
OUTPUT_FILE = os.path.expanduser("~/Molin-OS/docs/skills-registry-v7.md")
OUTPUT_JSON = os.path.expanduser("~/Molin-OS/docs/skills-registry-v7.json")

# ── 六司 → Worker 映射 ──
COMPANY_WORKERS = {
    "玄骨_xuangu": ["墨码", "墨维", "墨安", "墨梦", "墨算", "墨律", "墨人"],
    "紫灵_ziling": ["墨研", "墨数", "墨影", "墨嗅", "墨投"],
    "银月_yinyue": ["墨笔", "墨图", "墨剪", "墨链", "墨播", "墨星"],
    "元瑶_yuanyao": ["墨增", "墨销", "墨导", "墨学", "墨创", "墨域"],
    "梅凝_meining": ["墨译", "墨媒", "墨站", "墨航", "墨盾"],
    "宋玉_songyu": ["墨商", "墨案", "墨关", "墨聚", "墨采"],
}

def parse_skill(filepath):
    """Parse a SKILL.md and return (metadata, body, issues)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(3000)
    except:
        return None, None, ["READ_ERROR"]

    issues = []
    meta = {}
    body = ""

    if not content.startswith('---'):
        issues.append("NO_FRONTMATTER")
        # Try to extract title from first H1
        for line in content.split('\n')[:5]:
            if line.strip().startswith('# '):
                meta['name'] = line.strip('# ').strip()
                break
        return meta, content, issues

    # Parse YAML frontmatter
    end = content.find('---', 3)
    if end < 0:
        issues.append("BROKEN_FRONTMATTER")
        return meta, content, issues

    fm_text = content[3:end]
    body = content[end+3:].strip()

    try:
        parsed = yaml.safe_load(fm_text)
    except:
        issues.append("YAML_PARSE_ERROR")
        return meta, body, issues

    if not isinstance(parsed, dict):
        issues.append("YAML_NOT_DICT")
        return meta, body, issues

    meta = parsed

    # Check required fields
    required = ['name', 'description']
    optional = ['owner_domain', 'owner_worker', 'intent_tags', 'skill_id']
    
    for key in required:
        if key not in meta:
            issues.append(f"MISSING_{key.upper()}")
    
    for key in optional:
        if key in meta:
            continue  # has it
        # Don't flag missing optional fields as errors, just note
        pass

    # Check if it's a hub skill (has metadata.hermes section)
    if 'metadata' in meta and isinstance(meta['metadata'], dict):
        hermes_meta = meta['metadata'].get('hermes', {})
        if hermes_meta:
            meta['_source'] = 'hub'
            if 'tags' in hermes_meta:
                if 'intent_tags' not in meta:
                    meta['intent_tags'] = hermes_meta['tags']
        else:
            meta['_source'] = 'local'
    else:
        meta['_source'] = 'local'

    return meta, body, issues

def classify_domain_worker(meta, dirname):
    """Attempt to classify a skill into a company and worker based on metadata and directory."""
    name = str(meta.get('name', '')).lower()
    desc = str(meta.get('description', '')).lower()
    tags = [t.lower() for t in meta.get('intent_tags', [])] if isinstance(meta.get('intent_tags'), list) else []
    dir_lower = dirname.lower()
    source = meta.get('_source', 'local')

    all_text = f"{name} {desc} {' '.join(tags)} {dir_lower}"

    # ── 玄骨 (Infrastructure / System) ──
    xuanhu_keywords = [
        'git', 'github', 'code review', 'debug', 'deploy', 'backup',
        'security', 'audit', 'penetration', 'vulnerability', 'sql injection',
        'xss', 'ssh', 'firewall', 'encrypt', 'ssl', 'auth',
        'memory', 'chroma', 'vector', 'embedding', 'rag', 'index',
        'cli', 'terminal', 'shell', 'bash', 'command',
        'architecture', 'system design', 'c4-', 'infrastructure',
        'devops', 'docker', 'kubernetes', 'ci/cd', 'pipeline',
        'server', 'backend', 'api', 'rest', 'graphql',
        'database', 'sql', 'nosql', 'postgres', 'mysql',
        'python', 'node', 'rust', 'golang', 'java', 'typescript',
        'testing', 'tdd', 'unit test', 'integration test',
        'monitoring', 'logging', 'metrics', 'observability',
        'code quality', 'refactor', 'lint',
        'hermes', 'skill', 'mcp', 'agent framework',
        'plan', 'spike', 'writing-plans',
        'sop', 'compliance', 'governance',
        'mlops', 'fine-tuning', 'training', 'llama', 'vllm', 'ollama',
        'huggingface', 'weights', 'evaluation', 'benchmark',
        'finance', 'kpi', 'dashboard', 'analytics',
        'memor', 'obsidian', 'note-taking',
        'file', 'ocr', 'pdf', 'document',
        'webhook', 'cron', 'scheduler',
        'smart home', 'hue',
        'codex', 'claude code', 'opencode',
        'game', 'minecraft', 'pokemon',
    ]
    
    # ── 紫灵 (Intelligence / Research) ──
    ziling_keywords = [
        'research', 'intelligence', 'arxiv', 'paper', 'academic',
        'osint', 'investigation', 'scrape', 'crawl', 'web scraper',
        'search', 'rss', 'feed', 'blog', 'monitor',
        'trend', 'hot', 'news', 'sentiment',
        'market research', 'competitor', 'battlecard',
        'data analysis', 'data science', 'jupyter',
        'visualization', 'chart', 'dashboard', 'report',
        'last30days', 'polymarket', 'prediction',
        'world-monitor', 'mirofish',
        'llm-wiki', 'wikipedia',
        'domain', 'knowledge',
        'evaluate', 'evaluation', 'benchmark',
    ]

    # ── 银月 (Content / Media) ──
    yinyue_keywords = [
        'content', 'copywriting', 'writing', 'blog', 'article',
        'social media', 'xiaohongshu', 'xhs', 'tiktok', 'douyin',
        'youtube', 'bilibili', 'wechat', 'weibo',
        'image', 'photo', 'picture', 'comfyui', 'stable diffusion',
        'video', 'animation', 'manim', 'ffmpeg', 'ascii video',
        'audio', 'music', 'song', 'tts', 'voice', 'spotify',
        'design', 'svg', 'diagram', 'excalidraw', 'sketch',
        'pixel art', 'ascii art', 'p5js', 'creative',
        'infographic', 'comic', 'illustrator',
        'humanizer', 'text',
        'seo', 'keyword',
        'publish', 'post', 'schedule',
        'gif', 'meme',
        'presentation', 'powerpoint', 'slide',
        'newsletter', 'email marketing',
    ]

    # ── 元瑶 (Education / Growth) ──
    yuanyao_keywords = [
        'education', 'learning', 'course', 'student', 'teacher',
        'curriculum', 'pedagogy', 'tutor', 'quiz',
        'growth', 'marketing', 'conversion', 'funnel',
        'ab test', 'experiment', 'optimization',
        'user growth', 'acquisition', 'retention',
        'crm', 'customer', 'sales', 'deal', 'pricing',
        'product manager', 'prd', 'user story',
        'strategy', 'okr', 'kpi', 'planning',
        'cohort', 'segment', 'persona',
        'gtm', 'go-to-market',
        'business model', 'canvas',
        'ideation', 'brainstorm', 'creative idea',
        'copywriting', 'ad', 'campaign',
        'social media', 'influencer',
        'sprint', 'agile', 'scrum',
        'feedback', 'interview', 'survey',
        'analytics', 'google analytics',
    ]

    # ── 梅凝 (Global / Cross-border) ──
    meining_keywords = [
        'global', 'international', 'cross-border', 'overseas',
        'translation', 'localization', 'language', 'multilingual',
        'taiwan', 'china', 'asia', 'europe', 'america',
        'ecommerce', 'shopify', 'shopee', 'amazon', 'aliexpress',
        'supply chain', 'logistics', 'shipping',
        'trade', 'export', 'import',
        'legal', 'compliance', 'regulation', 'gdpr',
        'tax', 'accounting', 'invoice',
        'cultural', 'market entry',
        'payment', 'stripe', 'paypal',
        'domain', 'hosting',
    ]

    # ── 宋玉 (Business / Commerce) ──
    songyu_keywords = [
        'business', 'commerce', 'sales', 'b2b', 'enterprise',
        'startup', 'entrepreneur', 'founder', 'ceo',
        'pricing', 'revenue', 'monetization', 'profit',
        'investor', 'fundraising', 'pitch', 'vc',
        'partnership', 'negotiation', 'contract',
        'procurement', 'vendor', 'supplier',
        'project management', 'stakeholder',
        'risk', 'compliance', 'audit',
        'legal', 'contract', 'ip', 'trademark',
        'hiring', 'recruitment', 'hr', 'team',
        'office', 'productivity', 'notion', 'airtable',
        'linear', 'google workspace', 'calendar',
        'map', 'location', 'geocode',
        'email', 'imessage', 'messaging',
        'xianyu', 'zhubajie', 'side business',
        'trading', 'stock', 'crypto', 'freqtrade',
    ]

    scores = {
        '玄骨_xuangu': 0,
        '紫灵_ziling': 0,
        '银月_yinyue': 0,
        '元瑶_yuanyao': 0,
        '梅凝_meining': 0,
        '宋玉_songyu': 0,
    }

    for word in xuanhu_keywords:
        if word in all_text:
            scores['玄骨_xuangu'] += 1
    for word in ziling_keywords:
        if word in all_text:
            scores['紫灵_ziling'] += 1
    for word in yinyue_keywords:
        if word in all_text:
            scores['银月_yinyue'] += 1
    for word in yuanyao_keywords:
        if word in all_text:
            scores['元瑶_yuanyao'] += 1
    for word in meining_keywords:
        if word in all_text:
            scores['梅凝_meining'] += 1
    for word in songyu_keywords:
        if word in all_text:
            scores['宋玉_songyu'] += 1

    # Pick highest score
    best = max(scores, key=scores.get)
    best_score = scores[best]

    # If all zero, default to 玄骨 (global infrastructure)
    if best_score == 0:
        return '玄骨_xuangu', '墨维'

    # Get company key without _xxx suffix
    company = best
    
    # Pick worker
    worker = pick_worker_for_company(company, all_text)

    return company, worker

def pick_worker_for_company(company, text):
    """Assign a specific worker within a company based on skill content."""
    wmap = {
        '玄骨_xuangu': {
            '墨码': ['code', 'developer', 'git', 'github', 'python', 'javascript', 'api', 'cli', 'terminal'],
            '墨维': ['deploy', 'backup', 'docker', 'kubernetes', 'monitoring', 'ops', 'server', 'infrastructure', 'memory', 'chroma', 'vector'],
            '墨安': ['security', 'audit', 'vulnerability', 'penetration', 'encrypt', 'auth', 'firewall'],
            '墨梦': ['ml', 'fine-tuning', 'training', 'llama', 'model', 'huggingface', 'weights', 'research'],
            '墨算': ['kpi', 'dashboard', 'analytics', 'finance', 'metrics', 'data', 'report', 'evaluation'],
            '墨律': ['compliance', 'legal', 'governance', 'sop', 'audit'],
            '墨人': ['hr', 'team', 'communication', 'calendar', 'productivity'],
        },
        '紫灵_ziling': {
            '墨研': ['research', 'paper', 'academic', 'arxiv', 'knowledge', 'wiki'],
            '墨数': ['data', 'analysis', 'visualization', 'jupyter', 'dashboard', 'statistics'],
            '墨影': ['osint', 'scrape', 'crawl', 'web scraper', 'monitor'],
            '墨嗅': ['trend', 'hot', 'news', 'sentiment', 'market', 'competitor', 'price'],
            '墨投': ['prediction', 'polymarket', 'mirofish', 'trading signal', 'risk'],
        },
        '银月_yinyue': {
            '墨笔': ['copywriting', 'writing', 'content', 'blog', 'article', 'text', 'seo'],
            '墨图': ['image', 'design', 'photo', 'cover', 'comfyui', 'stable diffusion', 'illustration', 'svg', 'diagram'],
            '墨剪': ['video', 'animation', 'manim', 'ffmpeg', 'edit'],
            '墨链': ['social media', 'xiaohongshu', 'xhs', 'tiktok', 'douyin', 'publish'],
            '墨播': ['youtube', 'bilibili', 'stream', 'live'],
            '墨星': ['analytics', 'metrics', 'dashboard', 'report', 'performance'],
        },
        '元瑶_yuanyao': {
            '墨增': ['growth', 'acquisition', 'user growth'],
            '墨销': ['sales', 'conversion', 'deal', 'crm', 'pricing'],
            '墨导': ['strategy', 'okr', 'kpi', 'planning', 'sprint', 'roadmap'],
            '墨学': ['education', 'learning', 'course', 'student', 'teacher', 'curriculum'],
            '墨创': ['ideation', 'brainstorm', 'creative', 'innovation', 'product design'],
            '墨域': ['social media', 'community', 'wechat', 'private domain'],
        },
        '梅凝_meining': {
            '墨译': ['translation', 'localization', 'language', 'multilingual'],
            '墨媒': ['global', 'international', 'overseas', 'market entry'],
            '墨站': ['ecommerce', 'shopify', 'shopee', 'amazon', 'website'],
            '墨航': ['supply chain', 'logistics', 'shipping', 'trade'],
            '墨盾': ['compliance', 'regulation', 'legal', 'gdpr', 'risk'],
        },
        '宋玉_songyu': {
            '墨商': ['business', 'commerce', 'b2b', 'sales', 'enterprise'],
            '墨案': ['project', 'management', 'plan', 'proposal', 'document'],
            '墨关': ['government', 'public', 'relation', 'outreach'],
            '墨聚': ['event', 'conference', 'meeting', 'community'],
            '墨采': ['procurement', 'vendor', 'supplier', 'purchasing'],
        },
    }

    workers = wmap.get(company, {})
    best_worker = list(workers.keys())[0]
    best_score = 0

    for worker, keywords in workers.items():
        score = sum(1 for kw in keywords if kw in text.lower())
        if score > best_score:
            best_score = score
            best_worker = worker

    return best_worker


def main():
    print("🔍 扫描技能目录...")
    
    all_skills = []
    stats = defaultdict(int)
    domain_dist = defaultdict(int)
    worker_dist = defaultdict(int)
    
    for root, dirs, files in os.walk(SKILLS_DIR):
        for f in files:
            if f == 'SKILL.md':
                path = os.path.join(root, f)
                dirname = os.path.basename(root)
                meta, body, issues = parse_skill(path)
                
                entry = {
                    'filepath': os.path.relpath(path, SKILLS_DIR),
                    'dirname': dirname,
                    'meta': meta or {},
                    'issues': issues,
                    'has_fm': 'NO_FRONTMATTER' not in issues,
                    'has_owner_domain': bool(meta and meta.get('owner_domain')),
                    'has_intent_tags': bool(meta and meta.get('intent_tags')),
                }
                
                # Classify
                if meta:
                    company, worker = classify_domain_worker(meta, dirname)
                    entry['classified_company'] = company
                    entry['classified_worker'] = worker
                else:
                    # Try to classify just from directory name
                    _, content, _ = parse_skill(path)
                    company, worker = classify_domain_worker({}, dirname)
                    entry['classified_company'] = company
                    entry['classified_worker'] = worker
                
                for issue in entry['issues']:
                    if issue.startswith('MISSING_'):
                        stats['missing_fields'] += 1
                    elif issue == 'NO_FRONTMATTER':
                        stats['no_frontmatter'] += 1
                    elif issue == 'YAML_PARSE_ERROR':
                        stats['yaml_errors'] += 1
                
                domain_dist[entry['classified_company']] += 1
                worker_dist[entry['classified_worker']] += 1
                
                all_skills.append(entry)

    print(f"\n{'='*60}")
    print(f"  技能注册表扫描完成")
    print(f"{'='*60}")
    print(f"  总 SKILL.md: {len(all_skills)}")
    print(f"  有 Frontmatter: {len([s for s in all_skills if s['has_fm']])}/{len(all_skills)}")
    print(f"  已标注 owner_domain: {len([s for s in all_skills if s['has_owner_domain']])}/{len(all_skills)}")
    print(f"  缺 Frontmatter: {stats['no_frontmatter']}")
    print(f"  缺关键字段: {stats['missing_fields']}")
    print(f"  YAML 解析错误: {stats['yaml_errors']}")
    print(f"\n=== 自动分类结果 (六司) ===")
    for company, count in sorted(domain_dist.items()):
        print(f"  {company}: {count}")
    print(f"\n=== Worker 分布 (Top 15) ===")
    for worker, count in sorted(worker_dist.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {worker}: {count}")

    # Save JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_skills, f, ensure_ascii=False, indent=2)
    print(f"\n✅ JSON 已保存: {OUTPUT_JSON}")

    # Generate Markdown
    md = f"""# Molin-OS v7.0 · 技能注册表 (自动生成)

> 生成时间: 2026-05-21
> 数据来源: `skills/` 全量扫描
> 共计: {len(all_skills)} 个 SKILL.md

## 总览

| 指标 | 数值 |
|------|------|
| 技能总数 | {len(all_skills)} |
| 有 Frontmatter | {len([s for s in all_skills if s['has_fm']])} |
| 已标注 owner_domain | {len([s for s in all_skills if s['has_owner_domain']])} |
| 缺 Frontmatter | {stats['no_frontmatter']} |
| 缺关键字段 | {stats['missing_fields']} |

## 六司分布 (自动分类)

| 司 | 数量 | 说明 |
|----|------|------|
"""
    for company, count in sorted(domain_dist.items()):
        name_parts = company.split('_')
        emoji = {'玄骨': '💀', '紫灵': '🔮', '银月': '🌙', '元瑶': '🌸', '梅凝': '❄️', '宋玉': '🍃'}.get(name_parts[0], '📦')
        cn_name = name_parts[0]
        md += f"| {emoji} {cn_name} | {count} | |\n"

    md += f"""
## 技能清单（按六司分组）

"""
    # Group by company
    by_company = defaultdict(list)
    for s in all_skills:
        by_company[s['classified_company']].append(s)

    for company, skills in sorted(by_company.items()):
        name_parts = company.split('_')
        emoji = {'玄骨': '💀', '紫灵': '🔮', '银月': '🌙', '元瑶': '🌸', '梅凝': '❄️', '宋玉': '🍃'}.get(name_parts[0], '📦')
        cn_name = name_parts[0]
        
        md += f"### {emoji} {cn_name} ({len(skills)} 个)\n\n"
        md += "| 技能名 | Worker | Frontmatter | 意图标签 |\n"
        md += "|--------|--------|:-----------:|----------|\n"
        
        for s in sorted(skills, key=lambda x: x['dirname']):
            name = s['meta'].get('name', s['dirname'])
            if len(name) > 40:
                name = name[:37] + '...'
            worker = s['classified_worker']
            fm_status = '✅' if s['has_fm'] else '❌'
            tags = s['meta'].get('intent_tags', [])
            if isinstance(tags, list):
                tags_str = ', '.join(tags[:3])
            else:
                tags_str = str(tags)[:40]
            md += f"| {name} | {worker} | {fm_status} | {tags_str} |\n"
        md += '\n'

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"✅ Markdown 已保存: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
