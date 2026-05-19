---
title: 元瑶教育 Agent 项目总计划
status: 迭代中 (Active)
last_updated: 2026-05-19
agent_sync: true
---

## 学员记忆 MVP 方案

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

## 学员记忆方案

## 2026-05-16

### 结论
━━━━━━━━━━━━━━━━━━ 📋 SRS 复习时间表 · 任务完成 ━━━━━━━━━━━━━━━━━━

### 背景
修改 student_memory.py 加入 SRS 复习时间表功能

### 核心内容
- 补充结论：━━━━━━━━━━━━━━━━━━ 📋 修改 student_memory.py 加入游戏化连胜系统 ━━━━━━━━━━━━━━━━━━
- Let me verify edge cases with nonexistent students.
- Now verify the file structure is correct.
- The return statement and `_sync_to_sm` got lost. Let me fix this.
- All 4 commands verified. Let me do a final integrity check on the file:

### 下一步
- [ ] 待补充

## 学员记忆方案学习·0517

================================================================================
2026-05-15 学员持久记忆体系 · 自动化部署完成
================================================================================

一、存储架构
- 本地JSON文件（事实源）：edu/memories/students/<student_id>.json
  - 读写即刻生效，无延迟
  - 存储完整结构化画像（会话记录、统计、画像）
- Supermemory（搜索索引）：edu容器，自然语言文本（超时3秒，失败不阻塞）

二、学员画像自动追踪
- 每次对话自动诊断：认知阶段（1-8）、知识域、SRS阶段、连胜次数
- 画像自动写入JSON（7小时内同类数据合并去重，7小时外新文件写入）
- 关键维度：motivation_trend（动机趋势）、achievement_trend（成就趋势）、learning_plateau（学习高原）
- game-like连胜系统：回答正确累积连胜，纠正/重写归零

三、SRS复习调度（学习曲线干预）
- 复习时间表生成：SuperMemo2公式计算最优间隔
- 错题再测：根据记忆保留概率（96%/90%/80%/60%）决定干预级别
- 渐进提示策略：从最小提示开始，逐步增加

四、思维过程提取与评估
- 识别逻辑推理节点（假设识别→推理链条→结论形成）
- 评估关键思维能力（批判性思维、系统性思维、创造性思维）
- 每次对比历史表现（纵向趋势），避免单一维度评价

五、记忆模板配置
- JSON模板：M1_initial（首次）、M2_active（活跃）、M3_struggling（挣扎）、M4_high_performer（高表现者）
- 按学员表现阶段切换模板

## 修订日志 (Changelog)

- **2026-05-19**: 从学员记忆 MVP + 方案 + 学习记录合并
