#!/usr/bin/env python3
"""
飞轮配置读取器 — 根据 domain YAML 返回语义检索后的技能列表
供 Cron Job prompt 注入使用

用法:
  python3 scripts/flywheel_skills.py yinyue content_factory
  → 返回: skill_retriever 检索到的技能名列表 (JSON)
"""
import sys, os, yaml, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'molib'))
from skill_retriever import SkillRegistry

DOMAINS_DIR = os.path.join(os.path.dirname(__file__), '..', 'config', 'domains')

def load_domain_config(domain: str) -> dict:
    """Load a domain YAML by short name."""
    mapping = {
        'ziling': 'ziling_intelligence.yaml',
        'yinyue': 'yinyue_media.yaml',
        'yuanyao': 'yuanyao_edu_growth.yaml',
        'meining': 'meining_global.yaml',
        'songyu': 'songyu_innovation.yaml',
        'xuangu': 'xuanhu_infrastructure.yaml',
    }
    filename = mapping.get(domain)
    if not filename:
        raise ValueError(f"未知领域: {domain}")
    
    path = os.path.join(DOMAINS_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_flywheel_skills(domain: str, flywheel_name: str) -> dict:
    """
    读取 domain YAML 中的飞轮配置，执行语义检索，返回技能列表。
    
    Returns:
        {
            "flywheel": "content_factory",
            "domain": "yinyue",
            "intent": "生成小红书公众号短视频内容",
            "semantic_skills": [{"name": "...", "skill_id": "..."}],
            "fallback_skills": ["content-sop-pack", "gatekeeper-sop"],
            "output_target": "relay/contentmorning.json"
        }
    """
    config = load_domain_config(domain)
    flywheel = config.get('flywheel', {}).get(flywheel_name)
    
    if not flywheel:
        return {"error": f"飞轮 '{flywheel_name}' 不存在于 {domain} 配置中"}
    
    sr = flywheel.get('skill_retrieval', {})
    intent = sr.get('intent', '')
    domain_filter = sr.get('domain_filter', domain)
    top_k = sr.get('top_k', 3)
    fallback = flywheel.get('fallback_skills', [])
    output = flywheel.get('output_target', '')
    
    # Attempt semantic retrieval
    reg = SkillRegistry()
    semantic_skills = reg.retrieve_skills(intent, top_k=top_k, domain_filter=domain_filter)
    
    # If semantic retrieval failed, use fallback
    if not semantic_skills:
        semantic_skills = [
            {"name": s, "skill_id": s, "source": "fallback"}
            for s in fallback
        ]
    
    return {
        "flywheel": flywheel_name,
        "domain": domain,
        "intent": intent,
        "semantic_skills": [
            {"name": s.get('name', ''), "skill_id": s.get('skill_id', '')}
            for s in semantic_skills
        ],
        "fallback_skills": fallback,
        "output_target": output,
    }

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python3 scripts/flywheel_skills.py <domain> <flywheel_name>")
        print("示例: python3 scripts/flywheel_skills.py yinyue content_factory")
        sys.exit(1)
    
    domain = sys.argv[1]
    flywheel = sys.argv[2]
    
    result = get_flywheel_skills(domain, flywheel)
    print(json.dumps(result, ensure_ascii=False, indent=2))
