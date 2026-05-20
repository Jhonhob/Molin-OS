"""
墨研竞情 - MiroFish 群体智能预测引擎（完整版）
=================================================
共享层Worker，使用本地MiroFish引擎进行群体智能推演。
接入阿里百炼 qwen-plus（用户提供的API Key）。

管线:
  话题+种子材料 → 实体提取(LocalGraphStore) → OASIS模拟 → 本地检索分析 → 报告输出
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# ── MiroFish 引擎路径 ──
MIROFISH_ROOT = Path(os.path.expanduser("~/Molin-OS/engine/mirofish"))
MIROFISH_BACKEND = MIROFISH_ROOT / "backend"

# ── 阿里百炼配置（用户提供的） ──
BAILIAN_API_KEY = "sk-2d3ce929a91f433cac2d7acffc7b9707"
BAILIAN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
BAILIAN_MODEL = "qwen3.6-plus"


def ensure_mirofish_env():
    """确保MiroFish的Python环境可导入"""
    if str(MIROFISH_BACKEND) not in sys.path:
        sys.path.insert(0, str(MIROFISH_BACKEND))
    if str(MIROFISH_BACKEND / "app") not in sys.path:
        sys.path.insert(0, str(MIROFISH_BACKEND / "app"))
    
    # 设置环境变量
    os.environ.setdefault("LLM_API_KEY", BAILIAN_API_KEY)
    os.environ.setdefault("LLM_BASE_URL", BAILIAN_BASE_URL)
    os.environ.setdefault("LLM_MODEL_NAME", BAILIAN_MODEL)
    os.environ.setdefault("ZEP_API_KEY", "")  # 已禁用


def build_graph(topic: str, context: str = "") -> str:
    """构建知识图谱：用LLM从文本中提取实体 → 存入LocalGraphStore"""
    ensure_mirofish_env()
    
    from backend.app.services.graph_builder import GraphBuilderService
    
    builder = GraphBuilderService()
    
    # 构建种子材料
    seed_text = f"预测主题: {topic}\n"
    if context:
        seed_text += f"背景信息: {context}\n"
    seed_text += f"""
请基于以上主题，构建推演所需的知识图谱。
"""
    
    # 异步构建图（同步等待）
    task_id = builder.build_graph_async(
        text=seed_text,
        graph_name=f"prediction_{topic[:20]}",
        chunk_size=3000,
    )
    
    # 等待完成（最多60秒）
    for _ in range(30):
        task = builder.task_manager.get_task(task_id)
        if task and task.status == "completed":
            return task.result.get("graph_id", "default")
        time.sleep(2)
    
    return "default"


def run_simulation(graph_id: str, topic: str, num_agents: int = 10, num_rounds: int = 5) -> dict:
    """运行OASIS双平台并行模拟"""
    ensure_mirofish_env()
    
    from backend.app.services.simulation_runner import SimulationRunner
    
    runner = SimulationRunner()
    
    # 从图谱读取实体，生成OASIS agent配置
    config = runner.create_simulation_config(
        graph_id=graph_id,
        topic=topic,
        num_agents=num_agents,
        num_rounds=num_rounds,
    )
    
    # 运行模拟
    result = runner.run_parallel_simulation(config)
    return result


def generate_report(graph_id: str, topic: str, simulation_result: dict) -> dict:
    """生成推演报告"""
    ensure_mirofish_env()
    
    from backend.app.services.zep_tools import ZepToolsService
    from backend.app.services.local_graph_store import LocalGraphStore
    
    tools = ZepToolsService()
    store = LocalGraphStore()
    
    # 统计图谱数据
    stats = store.get_stats(graph_id)
    
    # 深度检索
    insight = tools.insight_forge(
        graph_id=graph_id,
        query=topic,
        simulation_requirement="预测推演",
    )
    
    # 生成最终报告
    report = {
        "预测主题": topic,
        "图谱统计": {
            "实体数": stats["node_count"],
            "关系数": stats["edge_count"],
            "实体类型": stats["entity_types"],
        },
        "模拟统计": {
            "Agent数": simulation_result.get("num_agents", 0),
            "模拟轮次": simulation_result.get("num_rounds", 0),
        },
        "关键实体洞察": insight.to_dict(),
    }
    
    return report


async def predict(
    topic: str,
    context: str = "",
    num_agents: int = 10,
    num_rounds: int = 5,
    mode: str = "quick"
) -> dict:
    """
    MiroFish 群体智能预测（完整版）
    
    Args:
        topic: 预测主题
        context: 背景信息/种子材料
        num_agents: OASIS Agent数量（默认10，最多50）
        num_rounds: 模拟轮次（默认5，最多20）
        mode: "full"=完整管线, "graph_only"=仅构建图谱, "sim_only"=仅模拟
    
    Returns:
        dict: 预测报告
    """
    # Phase 1: 完整模式 — 使用MiroFish引擎
    if mode == "full":
        from .mirofish_pipeline import run_full_prediction
        return run_full_prediction(topic, context)
    
    # Phase 2: 快速模式
        graph_id = build_graph(topic, context)
    else:
        graph_id = "default"
    
    # Phase 2: OASIS模拟
    sim_result = {"num_agents": 0, "num_rounds": 0}
    if mode in ("full", "sim_only"):
        sim_result = run_simulation(graph_id, topic, num_agents, num_rounds)
    
    # Phase 3: 生成报告
    if mode == "full":
        report = generate_report(graph_id, topic, sim_result)
        report["运行模式"] = "完整管线（LLM提取+OASIS模拟+报告生成）"
        return report
    
    return {
        "topic": topic,
        "mode": mode,
        "graph_id": graph_id,
        "num_agents": num_agents,
    }


async def _quick_predict(topic: str, context: str = "", num_agents: int = 8) -> dict:
    """
    快速预测模式（不构建图谱，直接多Agent LLM推演）
    用于简单/快速查询，节省时间。
    """
    roles = [
        "你是一个资深技术分析师，关注AI和开源社区，善于从技术趋势中判断方向",
        "你是一个风险投资人，关注商业价值和市场机会，善于判断哪些项目能赚钱",
        "你是一个产品经理，关注用户需求和产品体验，善于判断什么产品能流行",
        "你是一个行业研究员，关注行业动态和政策走向，善于判断宏观趋势",
        "你是一个量化分析师，关注数据和统计学，善于从数字中发现规律",
        "你是一个安全研究员，关注风险和漏洞，善于发现潜在问题",
    ][:num_agents]
    
    from openai import OpenAI
    client = OpenAI(
        api_key=BAILIAN_API_KEY,
        base_url=BAILIAN_BASE_URL,
    )
    
    # Phase 1: 各Agent独立思考
    agent_judgments = []
    for i, role in enumerate(roles):
        messages = [
            {"role": "system", "content": f"{role}\n\n对给定场景做出判断和预测。输出JSON：{{'judgment':'你的判断','confidence':0.0-1.0,'reasoning':'依据'}}"},
            {"role": "user", "content": f"预测场景：{topic}\n\n前置信息：{context or '无'}"}
        ]
        
        response = client.chat.completions.create(
            model=BAILIAN_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.8,
        )
        content = response.choices[0].message.content
        
        import re
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                judgment = json.loads(json_match.group())
            else:
                judgment = {"judgment": content, "confidence": 0.5, "reasoning": "原始输出"}
        except:
            judgment = {"judgment": content, "confidence": 0.5, "reasoning": "解析失败"}
        
        agent_judgments.append({
            "agent_id": i,
            "role": role[:20],
            "judgment": judgment.get("judgment", ""),
            "confidence": judgment.get("confidence", 0.5),
            "reasoning": judgment.get("reasoning", ""),
        })
    
    # Phase 2: 汇总
    summary_prompt = f"""你是一位首席分析师。以下是关于"{topic}"的{len(agent_judgments)}位不同背景专家的预测。
汇总共同点和分歧点，给出综合预测报告。

专家意见：{json.dumps([{
    "角色": r["role"], "判断": r["judgment"],
    "置信度": r["confidence"], "依据": r["reasoning"]
} for r in agent_judgments], ensure_ascii=False, indent=2)}"""

    response = client.chat.completions.create(
        model=BAILIAN_MODEL,
        messages=[{"role": "user", "content": summary_prompt}],
        max_tokens=800,
        temperature=0.3,
    )
    
    return {
        "topic": topic,
        "运行模式": "快速模式（8 Agent LLM推演）",
        "num_agents": len(agent_judgments),
        "context_used": bool(context),
        "agent_judgments": agent_judgments,
        "final_report": response.choices[0].message.content,
        "confidence_avg": sum(r["confidence"] for r in agent_judgments) / len(agent_judgments) if agent_judgments else 0,
    }
