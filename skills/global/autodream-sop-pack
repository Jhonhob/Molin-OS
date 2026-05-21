---
name: autodream-sop-pack
description: 墨梦AutoDream Agent SOP 技能包 — AI自动化实验/快速原型/创新探索/经验蒸馏
category: molin-org
version: 1.0.0
tags: [sop, autodream, experiment, prototype, innovation, rnd]
trigger: 所有实验性/创新性任务（快速原型/新技术探索/AI自动化实验）必须先加载此技能
---

# 墨梦AutoDream Agent SOP 技能包

## 适用 Agent
- 墨梦AutoDream (auto_dream.py)
- 集成：deep-dream-memory, self-learning-loop

---

## 一、Lead SOP（实验需求获取）

### 需求来源

| 来源 | 方式 | 优先级 |
|------|------|--------|
| Founder 直接指派 | 对话中提出实验想法 | P0 |
| 运营反馈 | 现有流程中的优化点/痛点 | P1 |
| 技术趋势 | 新技术/新工具出现 | P2 |
| 其他 Agent 建议 | Growth/Crisis SOP 触发的改进想法 | P1 |

### 实验评估

| 维度 | 权重 | 说明 |
|------|------|------|
| 潜在价值 | 30% | 如果成功，能带来多大改进 |
| 实验成本 | 25% | Token/时间投入估算 |
| 技术可行性 | 20% | 在当前环境下是否可做 |
| 风险 | 15% | 失败对现有系统的影响 |
| 学习价值 | 10% | 即使失败是否有收获 |

---

## 二、Execution SOP（实验流程）

```
想法输入 → 可行性评估 → 原型构建 → 实验运行 → 结论提取 → 经验蒸馏
```

### Step 1: 可行性评估

回答三个问题：
1. **做什么**：这个实验/原型的核心假设是什么？
2. **衡量标准**：成功的定义是什么？（明确可量化指标）
3. **终止条件**：什么情况下停止投入？

结果记录到 `relay/autodream/experiment_{id}.json`

### Step 2: 原型构建

- 最小可行性原型（MVP）：最小成本验证假设
- 不与生产环境共享资源（防影响线上）
- 沙盒运行，不影响现有代理
- 快速迭代（每轮 < 30 分钟）

### Step 3: 实验运行

实验记录格式：
```yaml
experiment_id: "AD-20260517-001"
hypothesis: "假设描述"
status: "running / concluded / cancelled"
started_at: "2026-05-17T10:00:00+08:00"
concluded_at: null
result: null
token_cost: 50000
learnings: []
artifacts: ["原型路径1", "原型路径2"]
next_steps: []
```

### Step 4: 结论提取

实验结论必须包含：
- 假设是否成立（是/否/部分）
- 证据（数据支撑）
- 意外发现（如果有）
- 可行性建议（投产/继续迭代/放弃）

### Step 5: 经验蒸馏

成功实验 → 提炼为 skill 或 SOP 更新
失败实验 → （已废弃 supermemory，改记录到 local 存档）

蒸馏流程：
```
实验结论
    ↓ 如果成功
skill_manage(action='create' 或 'patch')  → 固化到技能体系
    ↓ 如果失败
memory(action='add') → 记录教训 "实验AD-xxx失败原因：..."
```

---

## 三、QA SOP（实验质量质检）

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 假设清晰度 | 25% | 核心假设是否明确可测？ |
| 实验设计 | 25% | 方法是否合理？变量控制？ |
| 结论可靠性 | 25% | 结论是否有数据支撑？ |
| 文档完整 | 15% | 过程是否可复现？ |
| 安全性 | 10% | 实验是否影响生产环境？ |

---

## 四、Escalation SOP

| 场景 | 触发 | 动作 |
|------|------|------|
| 实验成本超限 | Token 消耗超过预估 300% | 停实验 + L1 通知 |
| 实验影响生产 | 意外影响线上 Agent | 立即回滚 + L2 审批 |
| 重大发现 | 实验发现高价值优化 | L1 通知 + 加速投产评估 |

---

## 五、Cron 经营节奏

| 时间 | 任务 | 产出 |
|------|------|------|
| 周五 14:00 | 本周实验周报 + 下周实验计划 | 实验报告 |
| 按需 | Founder 指派实验 | 原型/结论 |

---

## 六、系统集成

### SOP Engine 关联
本技能对应的 SOP Engine 定义文件：
`sop/definitions/auto_dream_sop.yaml` — 由 SOP Engine 加载，提供结构化执行步骤和触发条件。
当 `SOP_AUTOMATION_ENABLED=true` 时，SOP Engine 与本技能协同工作：Engine 负责步骤控制，本技能提供具体执行知识。

### 知识管理
```
实验结论
    ↓ 经验蒸馏（Step 5）
supermemory ~~已废弃~~
    ↓
其他 Agent 可引用
```

### Growth 联动
```
content-sop-growth 提出优化假设
    ↓ 需要验证时转
autodream-sop-pack 执行实验
    ↓ 结论返回
Growth SOP 应用结果
```

---

## 七、Agent 编排管道（吸收自 agency-agents Agents Orchestrator）

> 源：[Agents Orchestrator](https://github.com/msitarzewski/agency-agents/blob/main/specialized/agents-orchestrator.md) · MIT License · 吸收日期：2026-05-17

### 编排哲学

你不是自己做所有事的人——你是**指挥**。你的价值在于：让正确的 Agent 在正确的时间拿到正确的上下文，做对的事。

### 13 阶段编排管道

```
PM规划 → 架构设计 → [开发 ↔ QA循环] → 集成 → 交付
```

| 阶段 | Agent | 交付物 | 验收标准 |
|------|-------|--------|---------|
| 1 需求分析 | PM | 需求文档 | 所有约束明确 |
| 2 任务拆解 | PM → 任务列表 | tasklist.md | 每个任务独立可测 |
| 3 架构设计 | 架构师 | 架构文档 | 技术选型论证 |
| 4-10 开发 | 开发者 | 代码实现 | 任务级验收 |
| ↻ QA 循环 | QA → 开发者 | 修复+重验 | 最多 3 轮 |
| 11 集成测试 | 集成测试 | 测试报告 | 端到端通过 |
| 12 文档 | 技术写作 | 使用文档 | 可独立上手 |
| 13 交付 | 全员 | release | 门禁通过 |

### 持续质量循环（核心）

```
任务完成 → QA 验证 → 通过？→ 是 → 下一任务
                       ↓ 否
                    反馈给开发者 → 修复 → QA 复验
                       ↓ 3 次失败
                    升级：人工介入
```

### 状态管理

每个编排任务必须维护状态文件：

```yaml
pipeline:
  project: "项目名"
  phase: "开发/QA/集成"
  current_task: "task-05"
  completed_tasks: ["task-01", "task-02", "task-03", "task-04"]
  failed_tasks: []
  qa_loop_count: 2
  bottlenecks: []
  decisions: ["选用方案A因为..."]
```

### 关键规则

1. **无捷径**：每个任务必须通过 QA 验证
2. **证据驱动**：所有决策基于实际 Agent 输出和证据
3. **重试上限**：每个任务最多重试 3 次，超限升级
4. **清晰交接**：每个 Agent 拿到完整的上下文和明确指令
5. **进度追踪**：状态文件实时更新

### 与墨麟 delegate_task 集成

```
autodream-sop-pack 编排命令
    ↓
delegate_task (tasks=[]) 并行/串行派发
    ↓
各子 Agent 返回结果
    ↓
QA 循环 (gatekeeper-sop 检查)
    ↓
最终交付
```

### 失败处理矩阵

| 失败类型 | 动作 | 升级条件 |
|---------|------|---------|
| 单任务超时 | 自动重试 1 次 | 仍超时 → L1 通知 |
| QA 连续不通过 | 反馈给开发者，最多 3 轮 | 3 轮后 → L2 审批 |
| Agent 无响应 | 超时等待 5 分钟 | 仍无响应 → L1 通知 |
| 管道阻塞 | 检查依赖关系 | 无解 → L2 审批 |

---

## 八、参考

- 实验存档：`relay/autodream/`
- 历史实验：参考实验存档（supermemory已废弃）
- 技能创建：`skill_manage(action='create')`
- 记忆管理：`memory(action='add')`
