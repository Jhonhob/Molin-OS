---
title: 元瑶教育Agent项目总计划
status: 活跃
last_updated: 2026-05-19
agent_sync: true
frameworks_applied:
  - 5W1H × SMART
  - PDCA
---

元瑶教育Agent项目以飞书open_id为零成本身份锚点，复用Supermemory+Obsidian双通道架构，完成学员下次来系统记得上次的最小闭环。后续演进方向为多Agent教育系统(诊断/教学/督学三Agent联动)。

---

## 学员记忆MVP方案

复用已有Supermemory+Obsidian双通道架构，以飞书open_id为零成本身份锚点。Supermemory容器tag=edu已就绪能存能搜，飞书是现有触点学员身份直接用open_id无需额外登录，FastAPI+Python与现有同步脚本同栈。

## 架构

学员发消息→飞书机器人(元瑶)→记忆中间件：查Supermemory(before)→注入上下文到System Prompt→正常教学→存记忆(after)到Supermemory+Obsidian。

## 学员画像结构

每个学员在Supermemory存一份JSON(open_id为key)：sessions[]包含每次会话的主题/进度/困难/下一步，profile包含学习风格/强项/弱项/正确率/连续天数，last_session_summary包含上次摘要。

## 实施节奏

第1周核心回路：记忆中间件+飞书触点。第2周记忆体验：被记住问候+画像可视化。第3周教学联动：薄弱点推荐+助教简报。

## 验证指标

学员第二次会话率≥60%，被记住正向反馈率≥70%，每周人均会话频次≥2次。
