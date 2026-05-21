#!/usr/bin/env python3
"""
技能索引器 — 启动时或 Cron 调用，刷新 ChromaDB 技能向量库
用法: python3 scripts/index_skills.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'molib'))

from skill_retriever import SkillRegistry

def main():
    print("🔍 墨麟OS v7.0 · 技能索引器")
    print("=" * 40)

    reg = SkillRegistry()
    count = reg.index_all_skills()

    # 快速验证
    if count > 0:
        print("\n🧪 验证检索...")
        test_queries = [
            ("生成小红书爆款文案", "yinyue"),
            ("arXiv 论文搜索", "ziling"),
            ("Git 代码备份", "xuangu"),
            ("教育课程设计", "yuanyao"),
        ]
        for query, domain in test_queries:
            results = reg.retrieve_skills(query, top_k=2, domain_filter=domain)
            if results:
                top = results[0]
                print(f"  '{query}' → {top['name']} ({top['owner_worker']})")
            else:
                print(f"  '{query}' → 无结果")

    print(f"\n✅ 索引完成，共 {count} 个技能")

if __name__ == '__main__':
    main()
