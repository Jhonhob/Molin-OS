# MemPalace + Nuwa-Skill 评估（2026-05-18）

> 已精读评估，信息截止 2026-05-18。两个项目均 MIT 协议，可自由集成。

---

## 1. MemPalace — MemPalace/mempalace ⭐52,420

### 是什么

**本地优先的 AI 记忆系统**。逐字存储对话历史，语义检索，零 API 调用即达 96.6% R@5（LongMemEval 500题）。

### 核心架构

```
Palace 隐喻:
  Wing   → 人物/项目（如 "laomo", "edu-agent"）
  Room   → 主题分类（如 "architecture-decisions", "bug-fixes"）
  Drawer → 原始对话/文件块（逐字存储，不摘要不提取）

检索层:
  ChromaDB（默认）→ 可插拔 backend（base.py 定义接口）
  Hybrid v4: 语义搜索 + 关键词boost + 时间邻近boost → 98.4% R@5 (held-out)
  Hybrid v4 + LLM rerank → ≥99%

附加功能:
  - 时序知识图谱（SQLite, validity windows）
  - 29 个 MCP tools（read/write/navigate/agent diaries）
  - Claude Code hooks（auto-save + pre-compression save）
  - sweep 命令：按消息粒度逐条存储（sweep transcript-dir/）
```

### 与 Molin-OS 当前记忆体系对比

| 维度 | MemPalace | Molin-OS 当前 |
|------|-----------|--------------|
| 存储形式 | 逐字原文（verbatim） | YAML frontmatter + Markdown body |
| 检索方式 | 语义搜索 (ChromaDB) | 文件系统 grep / Obsidian wiki-link |
| 图谱 | SQLite 时序实体关系图 | Obsidian 原生图谱 |
| 位置 | 本地优先，无云依赖 | iCloud Drive + GitHub 备份 |
| 粒度 | 消息级（sweep） | 文件级（.md） |
| Agent 隔离 | 每个 Agent 独立 wing + diary | 业务线前缀区分（系统/元瑶/银月/...） |
| 安装 | `uv tool install mempalace` | Git repo + Python venv |

### 可借鉴点

1. **Pluggable backend 模式** — `backends/base.py` 定义统一接口，ChromaDB 只是默认实现。我们的 sync_memory.py 也可以抽象出 backend 接口。
2. **Verbatim 而非摘要** — MemPalace 刻意不做摘要/释义，理由是"removing nuance is data loss"。我们的 Obsidian 笔记也应是原文+链接而非纯摘要。
3. **Wing/Room/Drawer 三层分区** — 比我们当前的"8个扁平目录+业务线前缀"更结构化，搜索时可 scope 到 wing 缩小检索范围。
4. **Hybrid 检索管线** — 语义 + 关键词 + 时序 + LLM rerank，每一层独立启用/禁用。
5. **MCP tool 暴露** — 29 tools 不占系统 prompt，按需发现。我们的 relay pipeline 也可以用 MCP 暴露为按需查询接口。

### 不适合 Molin-OS 的部分

- **ChromaDB 依赖** — 额外进程/磁盘开销（~300MB embedding model），Obsidian 用户看不到。Molin-OS 的核心需求是"内容最终要可见于 Obsidian"。
- **逐字存储 vs 结构化笔记** — Molin-OS 的产出是决策/报告/成果/知识，不是对话日志。MemPalace 更适合"回放"而非"结构化知识管理"。
- **没有 Obsidian 集成** — MemPalace 是独立存储，没有写入 Obsidian vault 的路径。

### 集成建议

**轻量级借鉴，不全量替代。** 保留 Obsidian vault 作为主要存储，从 MemPalace 借鉴：

1. 在 `sync_memory.py` 中参照 base.py 的接口设计，抽象 "写入目标" 为 pluggable backend（当前只有 Obsidian，未来可加 ChromaDB 或 SQLite）
2. 借鉴 Hybrid 检索思路，为 relay 管道加语义检索层（目前只有关键词 grep）
3. 如果需要 "Agent diary" 功能（跨会话自动记录做了什么），MemPalace 的 sweep + diary 模式是可参考的成熟实现

---

## 2. Nuwa-Skill — alchaincyf/nuwa-skill ⭐19,722

### 是什么

**思维蒸馏框架**。输入一个人名，6 个并行 Agent 自动采集→提炼→生成结构化的 `SKILL.md`，使 AI 能以该人物的思维方式回应。

### 核心方法论 — 五层提取

| 层次 | 说明 | Molin-OS 对应 |
|------|------|------------|
| 怎么说话 | 表达DNA — 语气、节奏、用词偏好 | Agent persona（user profile） |
| 怎么想 | 心智模型、认知框架 | 当前无结构化定义 |
| 怎么判断 | 决策启发式 | SOP 中的决策规则 |
| 什么不做 | 反模式、价值观底线 | 部分在 SOP 的"不要做"段落 |
| 知道局限 | 诚实边界 | 当前缺失 |

### 执行流程

```
Phase 0: 入口分流
  ├─ 0A: 明确人名 → 澄清需求 + 检查是否有本地语料
  └─ 0B: 模糊需求 → 诊断推荐（需求维度表映射到最佳蒸馏对象）

Phase 0.5: 创建 Skill 目录结构
  └─ references/research/0X-xxx.md × 6 文件

Phase 1: 6-Agent 并行采集
  ├─ Agent 1: 著作与系统长文
  ├─ Agent 2: 对话与即兴思考
  ├─ Agent 3: 碎片表达与风格DNA
  ├─ Agent 4: 他者视角与批评
  ├─ Agent 5: 决策记录与行动
  └─ Agent 6: 人物时间线

Phase 2: 主 Agent 提炼 → 生成 SKILL.md

Phase 3: 验证校对（检查证据支撑、诚实边界）
```

### 产出格式 — SKILL.md

以 `duan-yongping-skill/SKILL.md` 为例（zwbao 基于 Nuwa-Skill 生成）：

```yaml
---
name: duan-yongping-perspective
description: |
  段永平的思维框架。基于雪球2212条问答、6场深度访谈、600篇博客。
trigger-keywords: 段永平视角、大道怎么看、duan yongping perspective
---
```

核心内容结构：
1. **角色扮演规则** — 激活后直接以该人物第一人称回应
2. **身份卡** — 我是谁、起点、现状
3. **核心心智模型 × 5** — 每个模型包含：一句话、证据（引用原文）、应用（如何用）、局限（诚实边界）
4. **决策启发式 × 8** — 短规则 + 应用场景 + 案例
5. **表达DNA** — 语气、句式、禁用词
6. **不为清单** — 绝对不能做的事
7. **诚实边界** — 明确标注做不到什么

### 与 Molin-OS Agent Persona 对比

| 维度 | Nuwa-Skill | Molin-OS 当前 |
|------|-----------|--------------|
| 人物来源 | 蒸馏真实人物（乔布斯/芒格/费曼） | 虚构角色（银月/元瑶/宋玉） |
| 构建方式 | 6-Agent 并行调研 → 结构化提炼 | 手工编写 persona 描述 |
| 心智模型 | 每个模型有证据+应用+局限三件套 | 当前无此层次 |
| 诚实边界 | 强制要求，每个 Skill 都写 | 当前缺失 |
| 证据链 | 引用原文+来源URL | 无结构化证据 |
| Agent 并行 | 6 个 subagent 同时采集 | 单 Agent 执行 |

### 对 Molin-OS 的可迁移概念

1. **心智模型结构化** — 当前 Molin-OS Agent 的 persona 只有"你是谁+怎么说话"，缺少"你怎么想"。Nuwa-Skill 的五层框架可以直接嫁接到 Agent persona 定义中。
2. **证据链** — Nuwa-Skill 的每个心智模型都要求引用原文证据。Molin-OS Agent 的决策/产出也应该有来源追溯。
3. **诚实边界** — "知道什么做不到"是 Nuwa-Skill 的硬性要求。Molin-OS Agent 的 SOP 也应该有 limitations 段落。
4. **Phase 0 诊断推荐** — Nuwa-Skill 的"模糊需求→诊断→推荐蒸馏对象"流程可以用于 Molin-OS 的"用户不知道该找哪个 Agent 时"的入口路由。
5. **Skill 自包含原则** — Nuwa-Skill 要求所有调研文件存在 skill 目录内部，复制即用。Molin-OS 的 skills 也应该做到 relative-path-only、不依赖外部路径。

### 不适合的部分

- **全量蒸馏成本高** — 每个真实人物需要 6 个 Agent 同时跑，token 消耗大。Molin-OS 的商业化场景不需要蒸馏乔布斯。
- **第一人称角色扮演不是 Molin-OS 的核心需求** — Molin-OS Agent 是"以角色身份执行任务"，不是"假装成另一个人回答用户问题"。
- **Nuwa-Skill 面向 Claude Code 生态** — `npx skills add` 的安装方式，与 Hermes Agent 的 skill_manage 体系不兼容。

### 集成建议

**借鉴方法论，不直接使用。** 具体动作：

1. 在 Molin-OS Agent persona 定义中增加三层：
   - **心智模型**（你看世界的方式）
   - **决策启发式**（你做判断的直觉规则）
   - **诚实边界**（你明确做不到什么）
2. SOP 模板（agent-sop-template）中增加 limitations 段落
3. Agent 交叉路由时，参照 Nuwa-Skill Phase 0B 的"需求诊断→匹配Agent"逻辑

---

## 3. 总体判断

| 项目 | 成熟度 | 与 Molin-OS 契合度 | 建议 |
|------|--------|-------------------|------|
| MemPalace | ⭐⭐⭐⭐⭐ 极成熟（52k⭐/MIT/有 benchmarks） | ⭐⭐⭐ 中（定位不同：对话记忆 vs 知识管理） | 借鉴 backend 接口设计 + Hybrid 检索思路 |
| Nuwa-Skill | ⭐⭐⭐⭐ 成熟（19.7k⭐/MIT/有生态） | ⭐⭐⭐ 中（定位不同：角色扮演 vs 任务执行） | 借鉴心智模型结构 + 诚实边界 + 证据链要求 |

**两者都比 Supermemory 好**（MemPalace 有真实 benchmarks、MIT 协议、本地优先），但都不能直接替代 Molin-OS 的 Obsidian vault 体系。正确的做法是"选择性吸收方法论，不全量替代架构"。
