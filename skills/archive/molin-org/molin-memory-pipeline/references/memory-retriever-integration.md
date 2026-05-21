# Memory Retriever Integration Guide

Files: `~/Molin-OS/molib/memory/`

## Architecture

Two modules work together:
1. **retriever.py** — Agent reads history before deciding
2. **output_writer.py** — Agent writes structured output after executing

## retriever.py API

```python
from molib.memory.retriever import retrieve_context, retrieve_insights

# Standard: search across all sources
ctx = retrieve_context(
    query="转化率提升策略",
    agent_name="edu",          # None = all agents
    top_k=5,
    days_back=30,
    section_filter=["洞察", "可复用知识"]  # only return these section types
)
# Returns: {query, agent, results[], summary, total_found}

# The summary field can be injected directly into agent prompts:
prompt = f"当前任务: ...\n\n## 历史参考\n{ctx['summary']}"

# Insight-only: searches Obsidian for Insight/Conclusion/Learning sections
insights = retrieve_insights(
    topic="用户转化",
    agent_name="edu",
    top_k=3
)
```

### Supported section filters
- `"洞察"` / `"结论"` / `"可复用知识"` / `"Key Learnings"` — wisdom sections
- `"执行动作"` / `"Actions"` — action items
- `"风险"` / `"Risks"` — failure patterns

## output_writer.py API

```python
from molib.memory.output_writer import write_agent_output

result = write_agent_output(
    agent_id="finance",
    output_type="daily_report",
    goal="一句话任务目标",
    summary="核心结果摘要",
    analysis="详细分析（支持markdown）",
    actions="做了什么",
    risks="风险异常",
    learnings="可复用知识",
    data_source="数据来源",
    related_tasks="关联任务",
    relations="[[关联知识]]",
    relay_path="relay/finance/daily.json",
    write_supermemory=False    # Supermemory已废弃
)
```

## Directory Structure
```
产出/{agent_id}/
  ├── {date}.md              ← By output_writer
  └── {topic}.md             ← By migration/sync
```

## Integration Pattern

Every cron job that produces output should:
1. Import `retriever` at start to get context
2. Execute task
3. Call `output_writer` at end
