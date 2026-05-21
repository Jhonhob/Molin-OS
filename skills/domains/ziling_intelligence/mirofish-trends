---
name: mirofish-trends
description: Swarm intelligence trend prediction — simulate thousands of agents with independent behaviors to forecast content trends, market movements, and technology adoption curves.
version: 2.0.0
tags: [prediction, trends, swarm-intelligence, forecasting, simulation, content-strategy]
category: research
related_skills: [last30days, polymarket, blogwatcher, karpathy-autoresearch]
metadata:
  hermes:
    source: https://github.com/666ghj/MiroFish
    stars: 61190
    engine_path: engine/mirofish/
    molin_owner: 墨研竞情（情报研究）
---

# MiroFish Trends — 蜂群趋势预测引擎

## Overview

MiroFish is a full swarm intelligence prediction engine. It ingests seed materials (news, docs, social signals), extracts entities into a knowledge graph, generates thousands of OASIS agent profiles with individual personas, runs simulated social interactions (Twitter + Reddit), and produces multi-path prediction reports.

## Engine Location

```
~/Molin-OS/engine/mirofish/
├── backend/
│   ├── run.py                                    # Flask 启动入口
│   ├── app/
│   │   ├── api/                                  # REST API (graph, simulation, report)
│   │   ├── services/
│   │   │   ├── graph_builder.py                  # GraphRAG 知识图谱构建
│   │   │   ├── oasis_profile_generator.py        # Zep→OASIS Agent 档案生成
│   │   │   ├── simulation_runner.py              # OASIS 仿真编排（核心，1.7K 行）
│   │   │   ├── simulation_manager.py             # 仿真生命周期管理
│   │   │   ├── simulation_ipc.py                 # 进程间通信（interview 模式）
│   │   │   ├── report_agent.py                   # LangChain ReACT 报告生成
│   │   │   ├── zep_tools.py                      # Zep 知识图谱工具
│   │   │   ├── zep_graph_memory_updater.py       # 动态记忆更新
│   │   │   ├── zep_entity_reader.py              # 实体读取
│   │   │   ├── ontology_generator.py             # 本体生成
│   │   │   ├── text_processor.py                 # 文本处理
│   │   │   └── simulation_config_generator.py    # 配置生成
│   │   ├── models/                               # 数据模型
│   │   └── utils/                                # 工具库 (LLM client, logger, retry...)
│   └── scripts/
│       ├── run_parallel_simulation.py            # 双平台并行模拟（推荐入口）
│       ├── run_twitter_simulation.py             # Twitter 单平台模拟
│       ├── run_reddit_simulation.py              # Reddit 单平台模拟
│       └── action_logger.py                      # 动作日志
├── requirements.txt                              # 依赖：flask, openai, zep-cloud, camel-oasis
└── .env.example                                  # 配置模板
```

## Dependencies

```bash
# 安装 MiroFish 引擎依赖
cd ~/Molin-OS/engine/mirofish
pip install -r backend/requirements.txt

# 核心依赖：
# - flask>=3.0, flask-cors    — Web 后端
# - openai>=1.0               — LLM 调用（支持任意 OpenAI 兼容 API）
# - zep-cloud==3.13.0         — 记忆知识图谱
# - camel-oasis==0.2.5       — OASIS 社交模拟框架
# - camel-ai==0.2.78         — OASIS 引擎
# - PyMuPDF/charset-normalizer — 文件解析
```

## Configuration

Copy `.env.example` to `.env` and fill in your API keys:

```
LLM_API_KEY=your_llm_api_key           # OpenAI 兼容 API
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1  # 推荐阿里百炼
LLM_MODEL_NAME=qwen-plus               # 大模型名

ZEP_API_KEY=your_zep_api_key           # Zep Cloud (https://app.getzep.com/)
ZEP_USER_ID=mirofish                   # Zep 用户标识
```

## How to Run (Standalone CLI Mode — Recommended for Molin OS)

### Quick Prediction Pipeline (3 steps)

```bash
cd ~/Molin-OS/engine/mirofish

# Step 1: Build knowledge graph from seed materials
# (This is done via the Flask API - graph_builder.py reads from seeds/)

# Step 2: Run parallel simulation (Twitter + Reddit)
python backend/scripts/run_parallel_simulation.py \
  --config simulation_config.json

# Step 3: Generate prediction report
python -c "
from backend.app.services.report_agent import ReportAgent
agent = ReportAgent()
report = agent.generate_report(simulation_output_dir='./sim_output')
print(report)
"
```

### Using the Flask API Server

```bash
cd ~/Molin-OS/engine/mirofish
python backend/run.py
# Server starts at http://localhost:5000

# API endpoints:
# POST /api/graph/build      — Build knowledge graph from seeds
# POST /api/simulation/run   — Run multi-agent simulation
# GET  /api/report/generate  — Generate prediction report
# GET  /health               — Health check
```

## The Swarm Prediction Method

### Phase 1: Seed Signal Extraction
- Scan news, social media, policy changes for weak signals
- Identify anomalies: what's getting unusual attention?
- Extract 3-5 key variables that could shift behavior
- Seed materials → Zep knowledge graph (graph_builder.py)

### Phase 2: Agent Profile Generation (oasis_profile_generator.py)
- Zep graph entities → OASIS agent profiles with:
  - Full persona, bio, MBTI personality type
  - Interests and behavior patterns
  - Initial posts and followers
- Generates thousands of unique agents simulating real users

### Phase 3: Social Simulation (simulation_runner.py + OASIS engine)
- Agents interact on simulated Twitter and Reddit across multiple rounds
- Actions: CREATE_POST, LIKE, REPLY, FOLLOW (configurable ratios)
- Each agent acts according to its persona and memory
- Full action log saved to sim_xxx/actions.jsonl

### Phase 4: Report Generation (report_agent.py)
- LangChain ReACT pattern queries post-simulation Zep graph
- Produces multi-path forecast with probabilities:
  - Best case: signal amplifies, early adopters cascade to mainstream
  - Base case: moderate adoption, niche community
  - Worst case: signal fades, no cascade
- Generates detailed prediction report with trend analysis

### Phase 5: Deep Interaction (IPC interview mode)
- After simulation, chat with any agent in the simulated world
- Supports single-agent interviews and batch interviews
- Get first-person insights from simulated personas

## When to Use

- Predicting what content format will trend next on Xiaohongshu/Douyin
- Forecasting which AI tool category will explode
- Market trend analysis for business planning
- Technology adoption curve prediction
- "Should I invest time in learning X?"
- Simulating consumer reaction to new product launches

## Use Cases for 一人公司

1. **Content trends**: "Will AI video tools be the next big Xiaohongshu trend?" → simulate creator adoption curve using MiroFish
2. **Service demand**: "Is demand for resume optimization rising or falling?" → simulate job market + AI awareness
3. **Platform shifts**: "Should I focus on Xiaohongshu or Douyin?" → simulate platform growth trajectories
4. **Pricing strategy**: "What price will the market bear for AI consulting?" → simulate buyer willingness

## Integration with Other Molin OS Skills

| Skill | Integration |
|-------|------------|
| last30days | Seed signal extraction — what's being discussed now feeds MiroFish simulation |
| polymarket | Probability calibration — real-money markets validate simulated forecasts |
| blogwatcher | Continuous signal feed into MiroFish knowledge graph |
| karpathy-autoresearch | Depth research mode — enrich seed materials before simulation |
| world-monitor | Trend monitoring — MiroFish predictions feed the monitoring dashboard |

## Molin OS molib Integration

```python
# Via molib CLI
python -m molib intel trend --topic "AI video tools" --depth simulation
python -m molib intel predict --topic "Xiaohongshu trends" --mode mirofish

# Direct Python usage
from molib.infra.mirofish import analyze_trend
result = analyze_trend("AI video tools on Xiaohongshu", model="deepseek-v4-pro")
```

## Note

MiroFish simulation requires:
- Zep Cloud account (free tier sufficient for small simulations)
- LLM API key (OpenAI-compatible, recommended: Alibaba qwen-plus)
- OASIS engine (camel-ai and camel-oasis packages)
- Heavy simulation rounds (40+ rounds) consume significant tokens — start small
