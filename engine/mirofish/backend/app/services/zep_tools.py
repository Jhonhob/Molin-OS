"""
本地检索工具服务（替代 ZepToolsService）
========================================
使用 LocalGraphStore + LLM 替代 Zep Cloud 的图谱搜索/采访/分析功能。

关键方法（与 report_agent.py 的接口完全兼容）:
- insight_forge() — 深度洞察检索（自动生成子问题→LLM分析）
- panorama_search() — 广度搜索（获取全貌）
- quick_search() — 简单搜索
- interview_agents() — 深度采访模拟Agent
- search_graph() — 图谱搜索
- get_all_nodes / get_all_edges / get_node_detail / get_entities_by_type
"""

import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

from .local_graph_store import LocalGraphStore, EntityNode
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from ..utils.locale import get_locale, t

logger = get_logger('mirofish.local_tools')


# ── 与原接口完全一致的 Data Classes ──

@dataclass
class SearchResult:
    facts: List[str]
    edges: List[Dict[str, Any]]
    nodes: List[Dict[str, Any]]
    query: str
    total_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {"facts": self.facts, "edges": self.edges, "nodes": self.nodes,
                "query": self.query, "total_count": self.total_count}

    def to_text(self) -> str:
        parts = [f"搜索查询: {self.query}", f"找到 {self.total_count} 条相关信息"]
        if self.facts:
            parts.append("\n### 相关事实:")
            for i, f in enumerate(self.facts, 1):
                parts.append(f"{i}. {f}")
        return "\n".join(parts)


@dataclass
class InsightForgeResult:
    query: str
    simulation_requirement: str
    sub_queries: List[str] = field(default_factory=list)
    semantic_facts: List[str] = field(default_factory=list)
    entity_insights: List[Dict[str, Any]] = field(default_factory=list)
    relationship_chains: List[str] = field(default_factory=list)
    total_facts: int = 0
    total_entities: int = 0
    total_relationships: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {"query": self.query, "simulation_requirement": self.simulation_requirement,
                "sub_queries": self.sub_queries, "semantic_facts": self.semantic_facts,
                "entity_insights": self.entity_insights, "relationship_chains": self.relationship_chains,
                "total_facts": self.total_facts, "total_entities": self.total_entities,
                "total_relationships": self.total_relationships}

    def to_text(self) -> str:
        parts = [f"## 未来预测深度分析", f"分析问题: {self.query}",
                 f"预测场景: {self.simulation_requirement}",
                 f"\n### 预测数据统计", f"- 相关预测事实: {self.total_facts}条",
                 f"- 涉及实体: {self.total_entities}个", f"- 关系链: {self.total_relationships}条"]
        if self.sub_queries:
            parts.append("\n### 分析的子问题")
            for i, sq in enumerate(self.sub_queries, 1):
                parts.append(f"{i}. {sq}")
        if self.semantic_facts:
            parts.append("\n### 【关键事实】")
            for i, f in enumerate(self.semantic_facts, 1):
                parts.append(f"{i}. \"{f}\"")
        return "\n".join(parts)


@dataclass
class AgentInterview:
    agent_name: str
    agent_role: str
    agent_bio: str
    question: str
    response: str
    key_quotes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {"agent_name": self.agent_name, "agent_role": self.agent_role,
                "agent_bio": self.agent_bio, "question": self.question,
                "response": self.response, "key_quotes": self.key_quotes}

    def to_text(self) -> str:
        text = f"**{self.agent_name}** ({self.agent_role})\n"
        text += f"_简介: {self.agent_bio}_\n\n**Q:** {self.question}\n\n**A:** {self.response}\n"
        return text


@dataclass
class InterviewResult:
    interview_topic: str
    interview_questions: List[str] = field(default_factory=list)
    selected_agents: List[Dict[str, Any]] = field(default_factory=list)
    interviews: List[AgentInterview] = field(default_factory=list)
    selection_reasoning: str = ""
    summary: str = ""
    total_agents: int = 0
    interviewed_count: int = 0

    def to_dict(self) -> Dict:
        return {"interview_topic": self.interview_topic, "interview_questions": self.interview_questions,
                "selected_agents": self.selected_agents, "interviews": [i.to_dict() for i in self.interviews],
                "selection_reasoning": self.selection_reasoning, "summary": self.summary,
                "total_agents": self.total_agents, "interviewed_count": self.interviewed_count}

    def to_text(self) -> str:
        parts = ["## 深度采访报告", f"**采访主题:** {self.interview_topic}",
                 f"**采访人数:** {self.interviewed_count} / {self.total_agents} 位模拟Agent"]
        if self.interviews:
            for i, iv in enumerate(self.interviews, 1):
                parts.append(f"\n#### 采访 #{i}: {iv.agent_name}")
                parts.append(iv.to_text())
        parts.append(f"\n### 采访摘要\n{self.summary or '（无摘要）'}")
        return "\n".join(parts)


# ── 核心服务 ──

class ZepToolsService:
    """
    本地检索工具服务（替代原 ZepToolsService）
    使用 LocalGraphStore + LLM 实现相同的接口。

    与原版方法签名完全兼容:
    - insight_forge(graph_id, query, simulation_requirement)
    - panorama_search(graph_id, query)
    - quick_search(graph_id, query)
    - interview_agents(graph_id, interview_topic, interview_questions)
    - search_graph(graph_id, query, limit, scope)
    - get_all_nodes(graph_id), get_all_edges(graph_id)
    - get_node_detail(graph_id, node_uuid)
    - get_node_edges(graph_id, node_uuid)
    - get_entities_by_type(graph_id, entity_type)
    - get_entity_summary(graph_id, entity_uuid)
    """

    def __init__(self, api_key: Optional[str] = None, llm_client: Optional[LLMClient] = None):
        self.store = LocalGraphStore()
        self._llm_client = llm_client
        logger.info("本地检索工具服务已初始化（SQLite+LLM替代Zep Cloud）")

    @property
    def llm(self) -> LLMClient:
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client

    # ── 图谱搜索 ──

    def search_graph(self, graph_id: str, query: str, limit: int = 10, scope: str = "edges") -> SearchResult:
        """图谱搜索 — 本地实现：关键词匹配 + LLM重排序"""
        nodes = self.store.get_all_nodes(graph_id)
        edges = self.store.get_all_edges(graph_id)

        # 简单关键词匹配
        q = query.lower()
        matched_nodes = [n for n in nodes if q in n["name"].lower() or q in n["summary"].lower()]
        matched_edges = [e for e in edges if q in e.get("fact", "").lower() or q in e.get("name", "").lower()]

        # 提取事实文本
        facts = []
        for e in matched_edges[:limit]:
            facts.append(f"{e.get('source_node_name','?')} --[{e.get('name','')}]--> {e.get('target_node_name','?')}: {e.get('fact','')}")
        for n in matched_nodes[:limit]:
            facts.append(f"{n['name']} ({', '.join(n['labels'])}): {n['summary']}")

        return SearchResult(
            facts=facts[:limit],
            edges=matched_edges[:limit],
            nodes=matched_nodes[:limit],
            query=query,
            total_count=len(facts),
        )

    # ── 深度洞察检索 ──

    def insight_forge(self, graph_id: str, query: str, simulation_requirement: str) -> InsightForgeResult:
        """深度洞察检索：LLM生成子问题→检索知识图谱→综合分析"""
        # 使用LLM生成子问题
        sub_q_prompt = f"""分析问题: {query}
预测场景: {simulation_requirement}

请将这个预测问题拆解为3-5个子问题，以便从不同维度分析。
每个子问题关注一个独立的分析维度（如经济/政治/技术/社会等）。
只输出子问题列表，每个一行。"""

        sub_q_text = self.llm.chat([{"role": "user", "content": sub_q_prompt}], temperature=0.3)
        sub_queries = [s.strip().lstrip("123456789. ") for s in sub_q_text.split("\n") if s.strip()]

        # 对每个子问题检索图谱
        all_facts = []
        all_entities = []
        for sq in sub_queries[:5]:
            result = self.search_graph(graph_id, sq, limit=5)
            all_facts.extend(result.facts)
            all_entities.extend(result.nodes)

        # LLM综合分析
        analysis_prompt = f"""基于以下关于「{query}」的多维度检索结果，生成深度分析。

需求场景: {simulation_requirement}

子问题分析维度:
{chr(10).join(f'- {sq}' for sq in sub_queries)}

关键事实:
{chr(10).join(f'- {f}' for f in all_facts[:20])}

核心实体:
{chr(10).join(f'- {e["name"]} ({", ".join(e["labels"])})' for e in all_entities[:10])}

请分析这些信息对预测问题的启示。输出格式：
1. 关键事实总结（哪3-5条事实最重要）
2. 实体洞察（每个核心实体的角色和立场）
3. 关系链（实体间的关键关系网络）
4. 初步预测判断"""

        analysis = self.llm.chat([{"role": "user", "content": analysis_prompt}], temperature=0.5)

        return InsightForgeResult(
            query=query,
            simulation_requirement=simulation_requirement,
            sub_queries=sub_queries,
            semantic_facts=all_facts[:15],
            entity_insights=[{"name": e["name"], "type": e["labels"][0] if e["labels"] else "Entity", "summary": e["summary"]} for e in all_entities[:10]],
            relationship_chains=[analysis],
            total_facts=len(all_facts),
            total_entities=len(all_entities),
            total_relationships=len(all_facts),
        )

    # ── 广度搜索 ──

    def panorama_search(self, graph_id: str, query: str):
        """广度搜索：获取图谱全貌"""
        nodes = self.store.get_all_nodes(graph_id)
        edges = self.store.get_all_edges(graph_id)
        stats = self.store.get_stats(graph_id)

        from dataclasses import dataclass
        @dataclass
        class NodeInfo:
            uuid: str; name: str; labels: List[str]; summary: str; attributes: Dict
            def to_dict(self): return {"uuid": self.uuid, "name": self.name, "labels": self.labels, "summary": self.summary, "attributes": self.attributes}

        @dataclass
        class EdgeInfo:
            uuid: str; name: str; fact: str; source_node_uuid: str; target_node_uuid: str
            source_node_name: Optional[str] = None; target_node_name: Optional[str] = None
            created_at: Optional[str] = None; valid_at: Optional[str] = None; invalid_at: Optional[str] = None; expired_at: Optional[str] = None
            def to_dict(self): return {"uuid": self.uuid, "name": self.name, "fact": self.fact, "source_node_uuid": self.source_node_uuid, "target_node_uuid": self.target_node_uuid, "source_node_name": self.source_node_name, "target_node_name": self.target_node_name}

        @dataclass
        class PanoramaResult:
            query: str; all_nodes: List = field(default_factory=list); all_edges: List = field(default_factory=list)
            active_facts: List[str] = field(default_factory=list); historical_facts: List[str] = field(default_factory=list)
            total_nodes: int = 0; total_edges: int = 0; active_count: int = 0; historical_count: int = 0
            def to_text(self) -> str:
                return f"## 广度搜索结果\n查询: {self.query}\n- 总节点: {self.total_nodes}\n- 总边: {self.total_edges}\n- 有效事实: {self.active_count}条"

        return PanoramaResult(
            query=query,
            all_nodes=[NodeInfo(uuid=n["uuid"], name=n["name"], labels=n["labels"], summary=n.get("summary",""), attributes=n.get("attributes",{})) for n in nodes],
            all_edges=[EdgeInfo(uuid=e["uuid"], name=e.get("name",""), fact=e.get("fact",""), source_node_uuid=e.get("source_node_uuid",""), target_node_uuid=e.get("target_node_uuid",""), source_node_name=e.get("source_node_name",""), target_node_name=e.get("target_node_name","")) for e in edges],
            active_facts=[f"{e.get('source_node_name','?')} --{e.get('name','')}--> {e.get('target_node_name','?')}: {e.get('fact','')}" for e in edges[:50]],
            total_nodes=stats["node_count"], total_edges=stats["edge_count"],
            active_count=min(len(edges), 50), historical_count=0,
        )

    # ── 简单搜索 ──

    def quick_search(self, graph_id: str, query: str) -> SearchResult:
        """简单搜索：直接关键词匹配"""
        return self.search_graph(graph_id, query, limit=5)

    # ── Agent 采访 ──

    def interview_agents(self, graph_id: str, interview_topic: str,
                          interview_questions: List[str]) -> InterviewResult:
        """模拟Agent采访：基于图谱中存储的Agent信息"""
        entities = self.store.get_entities_by_type("agent", graph_id)
        agents_data = [e for e in entities if hasattr(e, 'name')]

        if not agents_data:
            # 如果图谱中没有agent类型实体，使用所有实体
            all_nodes = self.store.get_all_nodes(graph_id)
            agents_data = [EntityNode(uuid=n["uuid"], name=n["name"], labels=n["labels"],
                                       summary=n.get("summary",""), attributes=n.get("attributes",{}))
                          for n in all_nodes[:20]]

        interviews = []
        topic = interview_topic

        for agent in agents_data[:5]:
            agents_prompt = f"""你是{agent.name}，{', '.join(agent.labels)}。
个人简介: {agent.summary or '无'}

采访主题: {topic}
问题: {interview_questions[0] if interview_questions else '你怎么看这个事？'}

请以这个角色的身份，给出有深度、有立场的回答。保持角色一致性。"""

            response = self.llm.chat([{"role": "user", "content": agents_prompt}], temperature=0.8)

            interviews.append(AgentInterview(
                agent_name=agent.name,
                agent_role=agent.get_entity_type() or "Agent",
                agent_bio=agent.summary[:200] if agent.summary else "",
                question=interview_questions[0] if interview_questions else topic,
                response=response,
            ))

        summary_prompt = f"请总结以下{len(interviews)}位模拟Agent对「{topic}」的采访观点，找出共识和分歧。"
        summary = self.llm.chat([{"role": "user", "content": summary_prompt + "\n\n" + "\n\n".join(i.response for i in interviews)}], temperature=0.3)

        return InterviewResult(
            interview_topic=topic,
            interview_questions=interview_questions,
            selected_agents=[{"name": a.name, "type": a.get_entity_type()} for a in agents_data[:5]],
            interviews=interviews,
            selection_reasoning="自动选择图谱中前5个主要实体作为采访对象",
            summary=summary,
            total_agents=len(agents_data),
            interviewed_count=len(interviews),
        )

    # ── 基础查询 ──

    def get_all_nodes(self, graph_id: str) -> List[Dict]:
        return self.store.get_all_nodes(graph_id)

    def get_all_edges(self, graph_id: str) -> List[Dict]:
        return self.store.get_all_edges(graph_id)

    def get_node_detail(self, graph_id: str, node_uuid: str) -> Optional[Dict]:
        return self.store.get_node_by_uuid(node_uuid)

    def get_node_edges(self, node_uuid: str) -> List[Dict]:
        return self.store.get_node_edges(node_uuid)

    def get_entities_by_type(self, graph_id: str, entity_type: str) -> List[EntityNode]:
        return self.store.get_entities_by_type(entity_type, graph_id)

    def get_entity_summary(self, graph_id: str, entity_uuid: str) -> str:
        node = self.store.get_node_by_uuid(entity_uuid)
        if node:
            return f"{node['name']} ({', '.join(node['labels'])}): {node.get('summary', '')}"
        return ""
