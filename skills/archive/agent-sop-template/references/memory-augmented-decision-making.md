# Memory-Augmented Decision Making

Captured from 2026-05-17 architecture upgrade.

## Core Concept

Agent execution shifted from stateless (current input → output) to stateful (current input + history → reasoning → decision). This is RAG + SOP execution fused.

## Implementation

```python
from molib.memory.retriever import retrieve_context
from molib.memory.output_writer import write_agent_output

# 1. Retrieve before executing
context = retrieve_context(
    query="转化率提升策略",
    agent_name="edu",
    section_filter=["洞察", "可复用知识"],
    top_k=5
)

# 2. Inject context into agent prompt
# SYSTEM.md defines the SOP, context supplies historical wisdom

# 3. Output through structured writer
result = write_agent_output(
    agent_id="edu",
    output_type="daily_report",
    goal="生成今日教育日报",
    summary="招生+12%, 转化率18%",
    analysis="渠道A转化率下降原因...",
    learnings="- 下午跟进转化更高\n- 视频转化优于图文",
)
```

## Key Files

| File | Role |
|------|------|
| `molib/memory/retriever.py` | Unified retrieval entry point |
| `molib/memory/obsidian_reader.py` | Obsidian structured knowledge search |
| `molib/memory/ranker.py` | Scoring + dedup + section filter |
| `molib/memory/output_writer.py` | Structured output + dual-write |

## Memory Layers

| Layer | Name | Carrier | Retention |
|-------|------|---------|-----------|
| L1 | Working | Session context | 24h |
| L2 | Episodic | Supermemory | 30d → distill |
| L3 | Semantic | Obsidian 产出/ | Permanent |
| L4 | Procedural | SKILL.md files | Versioned |

## Pitfalls

- Don't dump full context to agent — use `section_filter` to extract only Insights/Learnings
- Don't skip output_writer — raw writes bypass dual-write and lose Supermemory indexing
- Don't conflate L3 (Obsidian) with L4 (skills) — L4 changes require AutoDream proposal + L2 approval
