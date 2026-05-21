"""
墨麟OS v7.0 · 技能 RAG 检索引擎
基于 ChromaDB 实现技能的语义检索，替代手动的 skill_view()
依赖: chromadb (已在 MemPalace 中安装), pyyaml
"""
import os
import yaml
from pathlib import Path
from typing import Optional

try:
    import chromadb
except ImportError:
    chromadb = None


class SkillRegistry:
    """技能注册中心 — 扫描 skills/ 目录，向量化后提供语义检索。"""

    def __init__(self, skills_dir: str = None, db_path: str = None):
        self.skills_dir = Path(skills_dir or os.path.expanduser("~/Molin-OS/skills"))
        self.db_path = db_path or os.path.expanduser("~/.hermes/mempalace/chroma_db")
        self.collection_name = "molin_skills_v7"
        
        if chromadb:
            self.chroma_client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.chroma_client = None
            self.collection = None
            print("⚠️ ChromaDB 不可用，降级为关键词检索")

    # ── 解析 Frontmatter ──
    def _parse_skill(self, file_path: Path) -> tuple:
        """解析 SKILL.md 的 YAML Frontmatter，返回 (metadata, body)。"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(3000)
        except Exception:
            return None, None

        if not content.startswith('---'):
            return None, None

        end = content.find('---', 3)
        if end < 0:
            return None, None

        fm_text = content[3:end]
        body = content[end + 3:].strip()

        try:
            meta = yaml.safe_load(fm_text)
        except Exception:
            return None, None

        if not isinstance(meta, dict):
            return None, None

        return meta, body

    # ── 构建可检索文本 ──
    def _build_searchable_text(self, meta: dict) -> str:
        """将技能元数据拼接为可向量化的文本。"""
        name = str(meta.get('name', ''))
        desc = str(meta.get('description', ''))
        tags = meta.get('intent_tags', [])
        if isinstance(tags, list):
            tags_str = ', '.join(tags)
        else:
            tags_str = str(tags)
        return f"{name} - {desc} - 标签: {tags_str}"

    # ── 索引全部技能 ──
    def index_all_skills(self) -> int:
        """扫描 skills/ 下所有 SKILL.md，批量写入 ChromaDB。"""
        if not self.collection:
            print("❌ ChromaDB 不可用，跳过索引")
            return 0

        docs, metadatas, ids = [], [], []
        count = 0

        for md_file in self.skills_dir.rglob("SKILL.md"):
            meta, body = self._parse_skill(md_file)
            if not meta:
                continue

            skill_id = meta.get('skill_id', md_file.parent.name)
            domain = meta.get('owner_domain', 'unknown')
            worker = meta.get('owner_worker', 'unknown')
            rel_path = str(md_file.relative_to(self.skills_dir))

            searchable = self._build_searchable_text(meta)
            docs.append(searchable)
            metadatas.append({
                "skill_id": skill_id,
                "name": meta.get('name', ''),
                "owner_domain": domain,
                "owner_worker": worker,
                "file_path": rel_path,
            })
            ids.append(skill_id)
            count += 1

        if ids:
            # 清空旧索引后重新写入
            try:
                existing = self.collection.get()['ids']
                if existing:
                    self.collection.delete(ids=existing)
            except Exception:
                pass

            self.collection.add(documents=docs, metadatas=metadatas, ids=ids)
            print(f"✅ 索引完成: {count} 个技能")

        return count

    # ── 语义检索 ──
    def retrieve_skills(
        self,
        user_intent: str,
        top_k: int = 3,
        domain_filter: Optional[str] = None,
    ) -> list:
        """
        根据用户意图检索最相关的技能。

        Args:
            user_intent: 用户意图描述，如 "生成小红书爆款标题"
            top_k: 返回技能数
            domain_filter: 只检索指定领域 + global 公用技能，如 "yinyue"

        Returns:
            [{skill_id, name, owner_domain, owner_worker, file_path}, ...]
        """
        if not self.collection:
            return self._fallback_keyword_search(user_intent, top_k, domain_filter)

        where_clause = None
        if domain_filter:
            where_clause = {
                "owner_domain": {"$in": ["global", "xuangu", domain_filter]}
            }

        try:
            results = self.collection.query(
                query_texts=[user_intent],
                n_results=top_k,
                where=where_clause,
            )
        except Exception as e:
            print(f"⚠️ ChromaDB 查询失败: {e}，回退关键词检索")
            return self._fallback_keyword_search(user_intent, top_k, domain_filter)

        if not results or not results.get('metadatas') or not results['metadatas'][0]:
            return []

        output = []
        for meta in results['metadatas'][0]:
            output.append({
                "skill_id": meta.get('skill_id', ''),
                "name": meta.get('name', ''),
                "owner_domain": meta.get('owner_domain', ''),
                "owner_worker": meta.get('owner_worker', ''),
                "file_path": str(self.skills_dir / meta.get('file_path', '')),
                "distance": meta.get('distance', None),
            })

        return output

    # ── 降级：关键词检索 ──
    def _fallback_keyword_search(
        self, user_intent: str, top_k: int = 3, domain_filter: Optional[str] = None
    ) -> list:
        """ChromaDB 不可用时的关键词降级检索 — 优先匹配 intent_tags 和目录名。"""
        results = []
        intent_lower = user_intent.lower()
        
        # Split intent into keywords (handle both Chinese and English)
        keywords = [w for w in intent_lower.split() if len(w) > 1]
        # Also add the full intent as a single key for Chinese matching
        keywords.append(intent_lower.replace(' ', ''))

        for md_file in self.skills_dir.rglob("SKILL.md"):
            meta, body = self._parse_skill(md_file)
            if not meta:
                continue

            name = str(meta.get('name', '')).lower()
            desc = str(meta.get('description', '')).lower()
            tags = [t.lower() for t in meta.get('intent_tags', [])] if isinstance(
                meta.get('intent_tags'), list
            ) else []
            domain = meta.get('owner_domain', '')
            dirname = md_file.parent.name.lower()

            # Domain filter
            if domain_filter and domain not in ('global', 'xuangu', domain_filter):
                continue

            # Score: intent_tags (weight 5) > directory name (3) > name (2) > description (1)
            score = 0
            for kw in keywords:
                for tag in tags:
                    if kw in tag:
                        score += 5
                if kw in dirname:
                    score += 3
                if kw in name:
                    score += 2
                if kw in desc:
                    score += 1

            if score > 0:
                results.append({
                    "skill_id": meta.get('skill_id', md_file.parent.name),
                    "name": meta.get('name', ''),
                    "owner_domain": domain,
                    "owner_worker": meta.get('owner_worker', ''),
                    "file_path": str(md_file),
                    "score": score,
                })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    # ── 获取技能统计 ──
    def stats(self) -> dict:
        """返回技能体系统计。"""
        domains = {}
        total = 0
        for md_file in self.skills_dir.rglob("SKILL.md"):
            meta, _ = self._parse_skill(md_file)
            if not meta:
                continue
            total += 1
            d = meta.get('owner_domain', 'unknown')
            domains[d] = domains.get(d, 0) + 1

        return {"total": total, "domains": domains}


# ── CLI ──
if __name__ == "__main__":
    import sys

    reg = SkillRegistry()

    if len(sys.argv) > 1 and sys.argv[1] == "index":
        reg.index_all_skills()

    elif len(sys.argv) > 1 and sys.argv[1] == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else "内容生成"
        domain = sys.argv[3] if len(sys.argv) > 3 else None
        results = reg.retrieve_skills(query, top_k=5, domain_filter=domain)
        for i, r in enumerate(results):
            print(f"{i+1}. [{r['owner_domain']}/{r['owner_worker']}] {r['name']} — {r['skill_id']}")

    elif len(sys.argv) > 1 and sys.argv[1] == "stats":
        s = reg.stats()
        print(f"技能总数: {s['total']}")
        for d, c in sorted(s['domains'].items()):
            print(f"  {d}: {c}")

    else:
        print("用法: python -m molib.skill_retriever [index|search|stats]")
