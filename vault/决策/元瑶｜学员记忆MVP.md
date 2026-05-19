---
created: 2026-05-15
updated: 2026-05-16
agent: edu
status: 活跃
confidence: 已验证
importance: ⭐⭐⭐
source: 自研
tags: [edu, 学员记忆, Supermemory, MVP, 技术选型]
---

# 持久化学员记忆体系 MVP 方案

## 结论

复用已有 Supermemory + Obsidian 双通道架构，以飞书 open_id 为零成本身份锚点，3 周完成"学员下次来系统记得上次"的最小闭环。

## 理由

- Supermemory container_tag=edu 已就绪，能存能搜
- 飞书是墨麟现有触点，学员身份直接用 open_id，无需额外登录
- FastAPI + Python 与现有 sync_memory.py 同栈

## 架构

```
学员发消息 → 飞书机器人(元瑶) → 记忆中间件
                                   ├── 1.查Supermemory(before)
                                   ├── 2.注入上下文到System Prompt
                                   ├── 3.正常教学
                                   └── 4.存记忆(after) → Supermemory + Obsidian
```

## 学员画像结构

每个学员在 Supermemory 存一份 JSON（open_id 为 key）：
- sessions[]: 每次会话的 主题/进度/困难/下一步
- profile: 学习风格/强项/弱项/正确率/连续天数
- last_session_summary: 上次摘要

## 实施节奏（3周）

| 周 | 目标 | 关键交付 |
|----|------|---------|
| 第1周 | 核心回路 | 记忆中间件 + 飞书触点 |
| 第2周 | 记忆体验 | "被记住"问候 + 画像可视化 |
| 第3周 | 教学联动 | 薄弱点推荐 + 助教简报 |

## 验证指标

| 指标 | MVP目标 |
|------|---------|
| 学员第二次会话率 | ≥60% |
| "被记住"正向反馈率 | ≥70% |
| 每周人均会话频次 | ≥2次 |

## 下一步

- [ ] 第1周：实现记忆中间件（前置hook + 会后写入）
- [ ] 第1周：飞书 open_id → 学员画像映射
- [ ] 第2周：实现"上次你学到XX…"召回体验
- [ ] 第3周：与课程内容联动 + 助教简报

---

> 原始文件：`~/.hermes/profiles/edu/plans/student_memory_mvp_v1.md`
