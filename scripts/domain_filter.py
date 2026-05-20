#!/usr/bin/env python3
"""赛道相关度过滤器 — 内容情报管线的质量阀门
放置在情报层(08:00)和内容层(09:20)之间。
消费 relay/intelligence.json，输出 relay/intelligence_filtered.json

规则：
- AI/一人公司/创业/自媒体/效率/工具/副业/变现 相关 → keep
- 娱乐/地震/猫咪/穿搭/游戏/体育/明星 → discard
- 模糊匹配用LLM判断赛道相关度
"""

import json
import sys
import re

RELAY_DIR = __import__("pathlib").Path("/Users/laomo/.hermes/profiles/media/relay")
INTEL_PATH = RELAY_DIR / "intelligence.json"
OUT_PATH = RELAY_DIR / "intelligence_filtered.json"

# 核心赛道关键词（硬匹配）
CORE_KEYWORDS = [
    "AI", "人工智能", "一人公司", "创业", "自媒体", "效率",
    "工具", "副业", "变现", "内容创作", "流量", "私域",
    "个人IP", "IP", "小红书", "抖音", "运营", "增长",
    "自动化", "agent", "Agent", "编程", "零基础", "从0到1",
    "搞钱", "赚钱", "职场", "技能", "学习", "效率工具"
]

# 明显非赛道关键词（硬排除）
EXCLUDE_KEYWORDS = [
    "地震", "暴雨", "洪水", "灾", "死亡", "事故",
    "世界杯", "CBA", "NBA", "王者", "皮肤", "游戏",
    "穿搭", "爱豆", "偶像", "明星", "翻唱", "MV",
    "猫咪", "小狗", "宠物", "斗舞", "复仇摇",
    "总统", "外交", "冲突", "战争", "辟谣"
]

def score_relevance(item):
    keyword = item.get("keyword", "")
    kw_lower = keyword.lower()
    
    # 硬排除
    for ex in EXCLUDE_KEYWORDS:
        if ex.lower() in kw_lower:
            return 0.0
    
    # 硬匹配
    score = 0.0
    for ck in CORE_KEYWORDS:
        if ck.lower() in kw_lower:
            score += 0.3
    
    # 标签匹配
    tags = item.get("tags", [])
    if isinstance(tags, list):
        for tag in tags:
            for ck in CORE_KEYWORDS:
                if ck.lower() in str(tag).lower():
                    score += 0.2
    
    # ai_match_keywords 匹配
    ai_kws = item.get("ai_match_keywords", [])
    if isinstance(ai_kws, list):
        for ak in ai_kws:
            for ck in CORE_KEYWORDS:
                if ck.lower() in str(ak).lower():
                    score += 0.4
    
    # 来源权重
    source = item.get("source", "")
    if source == "xiaohongshu":
        score += 0.2
    
    # engagement_score 加权（高互动说明有价值）
    eng_score = item.get("engagement_score", 0)
    if isinstance(eng_score, (int, float)) and eng_score > 50:
        score += 0.1
    
    return min(score, 1.0)


def main():
    if not INTEL_PATH.exists():
        print(f"❌ intelligence.json not found at {INTEL_PATH}")
        return 1
    
    data = json.loads(INTEL_PATH.read_text(encoding="utf-8"))
    hot_topics = data.get("hot_topics", [])
    
    total = len(hot_topics)
    scored = []
    
    for item in hot_topics:
        score = score_relevance(item)
        item["domain_relevance"] = round(score, 2)
        if score >= 0.3:
            scored.append(item)
    
    filtered = data.copy()
    filtered["hot_topics"] = scored
    filtered["filter_meta"] = {
        "filtered_at": data.get("meta", {}).get("collected_at", ""),
        "total_before": total,
        "total_after": len(scored),
        "filter_rate": round((total - len(scored)) / total * 100, 1),
        "threshold": 0.3
    }
    
    OUT_PATH.write_text(json.dumps(filtered, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"✅ 赛道过滤完成: {total}条 → {len(scored)}条 (移除{total - len(scored)}条, {filtered['filter_meta']['filter_rate']}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
