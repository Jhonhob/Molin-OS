# Agent 输出标准模板

所有 Agent 输出必须通过 `molib/memory/output_writer.py` 写入。

## 模板结构

```markdown
# 🧠 Agent Output: {agent_name}

## 🕒 Metadata
- 时间: {datetime}
- Agent: {agent_id}
- 类型: {output_type}
- 来源数据: {data_source}
- 关联任务: {related_tasks}

---

## 🎯 任务目标
{一句话说明这次执行在解决什么问题}

---

## 📊 核心结果（Summary）
{关键数据 + 结论}

---

## 🔍 详细分析（Deep Analysis）
{数据拆解 + 洞察}

---

## ⚙️ 执行动作（Actions）
{已执行的操作}

---

## 🚨 风险与异常
{失败/异常记录}

---

## 🧩 可复用知识（Key Learnings）
{下次可参考的经验}

---

## 🔗 关联知识
{链接到其他相关文档}

---

## 📤 输出路径
- relay/{relay_path}
```

## Supermemory 语义块划分规则

output_writer.py 自动将以下区块拆分为独立语义块写入 Supermemory：

| 区块 | Supermemory 标签 | 用途 |
|------|-----------------|------|
| 核心结果 | `{agent_id} 执行摘要 {date}` | 快速回顾 |
| 可复用知识 | `{agent_id} 洞察 {date}` | 下次决策参考 |
| 执行动作 | `{agent_id} 执行动作 {date}` | 操作跟踪 |
| 风险与异常 | `{agent_id} 风险 {date}` | 问题追踪 |

## API 调用

```python
from molib.memory.output_writer import write_agent_output

result = write_agent_output(
    agent_id="finance",       # 小写英文 ID
    output_type="daily_report",
    goal="...",
    summary="...",
    analysis="...",
    actions="- 步骤1\n- 步骤2",
    risks="- 无异常",
    learnings="- 关键经验",
    data_source="relay/kpi/",
)
```

## 目录命名规范

- Obsidian: `产出/{agent_id}/{date}.md`
- Agent ID 映射：edu=元瑶教育, media=银月传媒, content=墨笔文创 等

## 禁止

- ❌ 直接 `write_file` 写入 `产出/`（绕过双写）
- ❌ 在内容中使用 `#` 或 `---` 以外的分隔符（破坏解析）
- ❌ 省略 metadata（导致无法按 Agent 检索）
