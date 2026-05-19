---
name: research-sop-pack
description: 墨研竞情 Agent SOP 技能包 — 情报采集/竞品分析/趋势发现/报告标准
category: molin-org
version: 1.0.0
tags: [sop, research, intel, competitive-analysis, intelligence]
trigger: 所有墨研竞情任务（情报扫描/竞品分析/趋势报告/深度研究）必须先加载此技能
---

# 墨研竞情 Agent SOP 技能包

## 适用 Agent
- 墨研竞情 (research.py)

---

## 一、Lead SOP（情报线索获取）

### 数据源配置

| 来源 | 工具 | 频次 | 优先级 |
|------|------|------|--------|
| AI/技术新闻 | blogwatcher + RSS | 每日 06:30 | P0 |
| arXiv 论文 | daily_arxiv_scan.sh | 每日 07:00 | P1 |
| GitHub Trending | web_search | 每日 08:00 | P1 |
| 竞品产品动态 | 指定网站监控 | 每日 07:30 | P0 |
| 行业报告 | web_search + arxiv | 每周 | P1 |
| 社交媒体趋势 | X/Twitter / Reddit | 每日 08:00 | P2 |
| MiroFish 预测 | mirofish-prediction skill | 按需 | P1 |

### 筛选规则

```
原始信号 → 三道筛：

1. 相关筛：是否命中墨麟业务关键词（AI教育/AI Agent/出海/台湾/内容营销）
2. 价值筛：时效性 (30%) + 差异化 (25%) + 行业影响力 (25%) + 可操作性 (20%)
3. 冲突筛：是否与已有情报重复

通过标准：总分 ≥ 65
```

### 输出

每日情报写入 `relay/intelligence_{date}.json`：

```json
{
  "date": "2026-05-17",
  "signals": [
    {
      "id": "INTEL-001",
      "title": "标题",
      "source": "blogwatcher",
      "url": "...",
      "type": "产品动态/技术突破/行业趋势/竞品分析",
      "relevance_score": 85,
      "urgency": "high/medium/low",
      "summary": "100字摘要",
      "action": "可选操作（如：通知内容Agent出选题）"
    }
  ],
  "summary": {
    "total_signals": 15,
    "high_urgency": 3,
    "top_trend": "本周热点词"
  }
}
```

---

## 二、Execution SOP（情报分析流程）

### 标准情报分析流水线

```
情报采集 → 原始信息清洗 → 结构化提取 → 交叉验证 → 分析报告 → 分发
```

### Step 1: 原始信息清洗
- 去重（基于 URL 和标题相似度）
- 过滤无效/低质源
- 标准化格式

### Step 2: 结构化提取
从每条情报中提取：
- 5W1H（Who / What / When / Where / Why / How）
- 对墨麟业务的影响评估（影响面 + 影响程度 1-5）
- 建议响应（关注/分析/行动/忽略）

### Step 3: 交叉验证
- 同一信息是否有至少 2 个独立来源？
- 来源是否可信？
- 数据/数字是否一致？
- 标记置信度（high / medium / low）

### Step 4: 分析报告
输出格式取决于报告类型：

#### 日报（每日 07:00）
- 今日 TOP5 情报速览
- 高优项（需要立即关注）
- 写入 relay/intelligence_{date}.json

#### 深度报告（按需）
```
主题调研
    ↓
背景分析（现状 + 历史）
    ↓
核心发现（数据 + 论据）
    ↓
影响评估（对墨麟业务的影响）
    ↓
建议行动（推荐策略）
    ↓
附录（来源清单）
```

### Step 5: 分发
- 日报 → `relay/intelligence_{date}.json`（Content Agent Lead SOP 消费）
- 深度报告 → Obsidian `知识/系统｜{topic}·{date}.md`（v3.0 flat vault）
- 紧急情报 → 直接推送到飞书（L1 Escalation）

---

## 三、QA SOP（情报质量质检）

### 评分维度

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 数据准确性 | 30% | 来源可查？数据无幻觉？ |
| 时效性 | 20% | 是否最新？有无过时信息？ |
| 相关性 | 20% | 是否与墨麟业务直接相关？ |
| 差异化 | 15% | 是否有独特洞察而非公开信息堆砌？ |
| 可操作性 | 15% | 能否转化为业务动作？ |

### 阈值动作

| 分数 | 动作 |
|------|------|
| ≥ 80 | 直接分发 |
| 65-79 | 补充验证后分发 |
| < 65 | 标记低质，不进入主情报流，仅存档 |

---

## 四、Escalation SOP

| 场景 | 触发 | 动作 |
|------|------|------|
| 竞品重大发布 | 竞品发布新产品/融资/战略调整 | L1 通知 → 生成深度分析任务 |
| 行业政策变化 | AI/教育/出海相关新政策 | L1 通知 → 评估影响 |
| 数据源持续故障 | 某一核心源连续 3 天无法访问 | L1 通知 → 寻找替代源 |
| 情报质量连续低分 | QA 均分连续 5 天 < 70 | L2 审批 → 重新配置情报源 |

---

## 五、Cron 经营节奏

| 时间 | 任务 | 输出 |
|------|------|------|
| 06:30 | 新闻扫描（blogwatcher + RSS） | 原始信号 |
| 07:00 | arXiv 论文扫描 + 交叉验证 | 结构化信号 |
| 07:30 | 竞品动态检查 | 竞品信号 |
| 08:00 | 情报日报聚合 | relay/intelligence_{date}.json |
| 周日 20:00 | 情报周报（趋势总结 + 机会识别） | `报告/系统｜情报周报·{YYYYMMDD}.md` |

---

## 六、与其他 Agent 的集成

### 内容 Agent

```
墨研竞情 08:00 情报日报
    ↓ Lead SOP 消费
墨笔文创选题会
    ↓
内容生产
```

集成点：`relay/intelligence_{date}.json` → `content-sop-lead` 读取作为数据源之一

### CEO

```
墨研竞情 紧急情报
    ↓ L1/Escalation
飞书通知 Founder
```

---

## 七、外部 Agent 仓库评估与吸收

> 当用户要求评估外部 AI Agent 定义仓库（如 `agency-agents`、`superpowers` 等）时，使用此流程。

### 评估流程

```
仓库发现 → 结构扫描 → Agent 映射 → 分级评分 → 吸收计划 → 执行
```

### Step 1: 结构扫描
- 获取仓库 README（prefer `raw.githubusercontent.com`，避免 GitHub API 限速）
- 提取 Agent 目录结构（按 Division/Category 分组）
- 统计 Agent 总数、每个 Agent 的定义格式（YAML frontmatter / Markdown 章节）

### Step 2: Agent → 墨麟子公司映射
对每个 Agent 问三个问题：
1. 它的核心领域是否匹配墨麟 20 家子公司之一？
2. 它的工作流是否能填补现有 SKILL.md 的空白？
3. 它的交付物标准是否比现有标准更严格/更完整？

### Step 3: Tier 分级

| Tier | 标准 | 动作 |
|------|------|------|
| 🔴 Tier 1 | 95%+ 匹配，填补关键空白 | 立即吸收（当周） |
| 🟡 Tier 2 | 高匹配，增强现有能力 | 本周/下周吸收 |
| 🟢 Tier 3 | 有增强价值，非紧急 | 择机吸收 |
| ⚫ Skip | 不匹配/低价值/完全不相关 | 标注原因，不吸收 |

### Step 4: 吸收方法

每吸收一个外部 Agent 定义 → 墨麟 SKILL.md 的标准管线：

1. 读取外部源文件
2. 提取三要素：Identity + Workflow + Deliverables
3. 与现有墨麟 SKILL.md 做 diff 对比，只补缺不覆盖
4. 将英文流程翻译为中文 SOP 步骤
5. 注入墨麟工具链约束（vault 路径 `业务线｜内容.md`、飞书推送、Supermemory 双写）
6. 质量门控：gatekeeper-sop 检查后合并

### 文件格式转换

| 外部格式 | → 墨麟 SKILL.md 格式 |
|----------|---------------------|
| YAML frontmatter (name/description/color/emoji) | → SKILL.md YAML (name/description/category/version/tags) |
| `## Identity & Memory` | → `## Agent 身份` |
| `## Core Mission` | → `## 核心使命` |
| `### Phase 1/2/3` | → `## 执行流程` (Step 1/2/3) |
| `## Success Metrics` | → `success_criteria` (YAML 块) |
| 英文内容 | → 中文（保留关键英文术语） |

### 输出

评估报告写入 vault：`知识/系统｜{仓库名}评估·{YYYYMMDD}.md`

报告结构：总体判断 → Tier 分级清单 → 吸收方法 → 优先级路线图 → 风险提示 → 总结

### 已知高价值外部仓库

| 仓库 | 价值 | 匹配子公司数 |
|------|------|-------------|
| `msitarzewski/agency-agents` | 140+ Agent 人格定义，19 事业部 | ~22 直接匹配 |
| — | 持续补充 | — |

详细方法论见：`references/external-agent-evaluation.md`

---

## 八、趋势研究增强方法（吸收自 agency-agents Trend Researcher）

> 源：[Trend Researcher](https://github.com/msitarzewski/agency-agents/blob/main/product/product-trend-researcher.md) · MIT License · 吸收日期：2026-05-17

### 核心能力扩展

| 能力 | 工具/方法 | 墨麟应用场景 |
|------|----------|------------|
| **弱信号检测** | 统计验证+模式识别 | 早期识别 AI 教育/Agent 市场新兴趋势 |
| **跨行业模式分析** | 竞对情报+机会映射 | 电商→教育、娱乐→内容 的跨界洞察 |
| **消费者行为预测** | 高级分析+人物画像 | 台湾市场/出海受众的消费趋势预测 |
| **竞争定位** | 差异化策略+市场缺口分析 | 竞争对手能力矩阵 |
| **技术侦察** | 初创生态监控+创新追踪 | GitHub trending + ProductHunt |

### 弱信号检测三步法

```
Step 1: 信号采集
  • 社交媒体趋势（X/Twitter, Reddit, 小红书）
  • 搜索趋势（Google Trends, 百度指数）
  • 专利数据库
  • 投资流向（Crunchbase, PitchBook, IT桔子）

Step 2: 信号验证
  • 是否有 3+ 独立来源？
  • 信号强度是否在增长？（月环比趋势）
  • 是否有行业 KOL/头部公司在跟进？

Step 3: 机会评分
  总分 = 行业影响(30%) + 增长势能(25%) + 墨麟匹配度(25%) + 进入门槛(20%)
  ≥80 → P0 立即深度研究
  65-79 → P1 持续跟踪
  <65 → 存档备查
```

### 市场竞争情报框架

```
竞争态势分析：
  市场份额地图 → 产品/服务对比矩阵 → SWOT 四象限

技术景观扫描：
  技术成熟度曲线 → 技术栈映射 → 人才信号

监管情报：
  政策变化 → 合规要求 → 行业标准更新
```

### 研究报告结构升级

深度报告原结构基础上增加：

```markdown
## 市场时机评估
- 窗口期：已开启 / 6个月内 / 1-2年 / 远未来
- 先行者优势：[是/否] + 论据
- 进入壁垒：[技术/资金/品牌/政策] + 程度

## 创新机会矩阵
| 机会 | 市场成熟度 | 竞争强度 | 墨麟优势 | 推荐优先级 |
|------|-----------|---------|---------|-----------|
| ... | 早期/成长/成熟 | 低/中/高 | ... | P0/P1/P2 |

## 风险矩阵
| 风险 | 概率 | 影响 | 缓释策略 |
|------|------|------|---------|
| ... | ... | ... | ... |
```

---

## 九、參考

- 數據源具體配置：blogwatcher / arxiv / web_search 對應 skill
- 情報存档：Obsidian vault `知识/玄骨｜{topic}·{date}.md`（v3.0 flat vault）
- GitHub Trending 深度研究實戰方法論：`references/github-trending-deepdive.md`（含工具選擇策略、篩選標準、深度研究流程、格式化輸出、Obsidian 歸檔）
- Agent 模板：`skill_view('agent-sop-template')`
