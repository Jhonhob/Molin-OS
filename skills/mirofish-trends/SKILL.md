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
min_hermes_version: 0.13.0
---

# MiroFish Trends — 蜂群趋势预测引擎

## Overview

MiroFish is a full swarm intelligence prediction engine. It ingests seed materials (news, docs, social signals), extracts entities into a knowledge graph, generates thousands of OASIS agent profiles with individual personas, runs simulated social interactions (Twitter + Reddit), and produces multi-path prediction reports.

## Engine Location

Code at `engine/mirofish/` in Molin-OS repo. See `skills/intelligence/research/mirofish-trends/SKILL.md` for full documentation.

- `engine/mirofish/backend/scripts/run_parallel_simulation.py` — 双平台并行模拟（推荐入口）
- `engine/mirofish/backend/services/simulation_runner.py` — OASIS 仿真编排（核心，1768 行）
- `engine/mirofish/backend/services/report_agent.py` — LangChain ReACT 报告生成
- `engine/mirofish/backend/services/oasis_profile_generator.py` — Agent 档案生成

## Quick Start

```bash
cd ~/Molin-OS/engine/mirofish
pip install -r backend/requirements.txt
# 配置 .env (参考 .env.example)
python backend/scripts/run_parallel_simulation.py --config simulation_config.json
```

## Dependencies

- flask, openai, zep-cloud==3.13.0, camel-oasis==0.2.5, camel-ai==0.2.78
- Zep Cloud 账户 (https://app.getzep.com/)
- LLM API (推荐阿里百炼 qwen-plus)

## Integration

| Skill | Role |
|-------|------|
| last30days | 种子信号提取 — 当前讨论热点喂入 MiroFish |
| polymarket | 概率校准 — 真实市场验证模拟预测 |
| blogwatcher | 持续信号流输入知识图谱 |
| karpathy-autoresearch | 种子材料深度丰富 |

## molib 集成

```python
python -m molib intel trend --topic "AI video tools" --depth simulation
python -m molib intel predict --topic "Xiaohongshu trends" --mode mirofish
```

## 注意事项

模拟需要 Zep Cloud + LLM API + OASIS 引擎。大数据量模拟消耗 token 较多，建议从小规模开始（< 40 轮）。
