---
name: vertical-learning-sop
description: "五大Agent垂直学习管道SOP — 定向订阅→精读吸收→SKILL文件更新→质量门控，学习结果写入 Obsidian 学习档案/（平坦结构）"
version: 1.0.0
author: Molin-OS
license: MIT
platforms: [macos]
trigger-keywords:
  - 垂直学习
  - 学习管道
  - 领域学习
  - Github学习
  - 定向订阅
  - 精读吸收
  - 学习档案
  - 深度笔记
  - 垂直扫描
  - github-absorb
  - 每周学习
invocation-context: "Load this skill when: (1) running the weekly vertical learning scan cron job; (2) any agent needs to learn from GitHub repos, papers, or blogs in its domain; (3) creating deep notes after absorbing external knowledge; (4) updating agent skills based on learning; (5) fixing or debugging the learning pipeline."
prerequisites:
  commands: [curl, python3, gh]
  env_vars: [GITHUB_TOKEN, OBSIDIAN_VAULT_PATH]
metadata:
  hermes:
    tags: [learning, sop, github, obsidian, agents, cron, 墨麟]
    category: molin-org
---

# 垂直学习管道 SOP (Vertical Learning Pipeline)

## 概述

为墨麟AI集团五大业务Agent建立领域定向学习管道，让每个Agent持续吸收其领域的最新发展，做深度笔记，反哺技能文件。

### 五层架构

```
第1层：定向采集 → 按领域关键词，定时扫描 GitHub Trending / arXiv / 博客
第2层：精读吸收 → 每次精选 3-5 篇，写深度笔记（5问模板）
第3层：技能内化 → 有价值的发现 → 更新对应 SKILL.md
第4层：质量门控 → 自动检查笔记质量、输出合规、配图
第5层：档案沉淀 → 笔记写入 Obsidian 学习档案/（平坦结构，`业务线｜{主题}·{日期}.md`）
```

### 五大Agent订阅表

| Agent | Agent ID | 职能 | GitHub 关键词 | 附加源 |
|-------|---------|------|-------------|--------|
| 墨笔文创 | content | 文字内容创作 | content-marketing, copywriting-ai, SEO-tool, xhs-bot, douyin-automation | 新榜API/飞瓜数据RSS/运营研究社 |
| 墨学教育 | edu | 课程设计与辅导 | lms-platform, tutoring-ai, course-design, spaced-repetition, ai-tutor | 教育部政策RSS/多知网/ProductHunt Education |
| 墨研竞情 | research | 竞争分析与趋势 | gpt-researcher, web-scraping, competitive-intelligence, market-analysis | HN Top/arXiv cs.AI/36氪快讯 |
| 墨码开发 | dev | 软件开发与架构 | agent-framework, code-generation, claude-code, mcp-server, devops-ai | GitHub Trending Daily/changelog聚合 |
| 墨梦AutoDream | autodream | AI实验与原型 | self-improving-ai, memory-system, rag-system, agent-evolution | arXiv cs.MA/LangChain Blog |

### Obsidian 档案路径（v3.0 平坦结构）

```
{OBSIDIAN_VAULT_PATH}/学习档案/
  ├── 系统｜总索引.md                   ← 全部 Agent 学习概览
  ├── 元瑶｜教育研究吸收·W20.md          ← 元瑶第20周学习
  ├── 银月｜GitHub知识吸收·0516.md       ← 银月学习笔记
  ├── 银月｜提示词方法论.md              ← 银月方法论
  └── ...
```

**零子目录。** 所有笔记直接放入 `学习档案/`，文件名 `业务线｜主题·日期.md` 区分归属。

业务线对照：
- 元瑶   → edu（墨学教育）
- 银月   → media（银月传媒）
- 梅凝   → global（墨海出海）
- 宋玉   → side（宋玉副业）
- 系统   → 跨Agent公共学习

---

## 第1层：定向采集 (Scan)

### 流程

每周一轮（周一 06:00），脚本扫描以下来源：

#### A. GitHub Trending (当天)
```bash
# 按语言/关键词搜索
curl -s "https://api.github.com/search/repositories?q=${KEYWORD}+in:name,description+created:>=2026-05-10&sort=stars&order=desc&per_page=5" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json"
```

#### B. arXiv 论文扫描
```bash
# arXiv API 按类别+关键词
curl -s "https://export.arxiv.org/api/query?search_query=all:${KEYWORD}+AND+cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=5"
```

#### C. 博客/RSS 扫描
```bash
# 使用 blogwatcher-cli 检查未读文章
blogwatcher-cli scan
blogwatcher-cli articles --blog "$BLOG_NAME" --limit 5
```

### 输出

采集结果汇总到临时文件：
```
/Users/laomo/.hermes/vertical-learning/{agent_id}/scan-{YYYY-MM-DD}.json
```

包含标题、链接、摘要、星数（GitHub）、热度评分。

### 热度评分公式
```
GitHub: stars + forks*0.5 + 取平方根归一化到 1-10
arXiv: citationCount (Semantic Scholar) + 归一化到 1-10
博客: 发布天数 / 30 衰减 + 相关性关键词匹配
```

---

## 第2层：精读吸收 (Deep Read)

### 选材原则

- 每轮选 3-5 篇（从采集结果中按热度排序取 Top 10，人工/Agent 筛选）
- **必读条件**（至少满足2条）：
  - 热度 ≥ 5
  - 与 Agent 核心职能直接相关
  - 有方法论或可借鉴的代码/架构
  - 顶级出品（LangChain Blog、DeepMind、OpenAI、Anthropic 等）
- **跳过条件**：
  - 纯新闻/发布公告（无技术深度）
  - 已有覆盖（检查 学习档案 目录有无相同主题）
  - 非本领域（误匹配）

### 精读方法

每篇资源按以下步骤吸收：

1. **阅读摘要/README** — 获取大框架
2. **阅读代码/论文核心章节** — 抓方法论
3. **对比当前体系** — 是否有可迁移的部分
4. **写深度笔记** — 使用下方模板

---

## 第3层：写深度笔记 (Deep Note Template ⭐)

**这是审计报告要求的核心模板，每个学习条目必须按此格式书写。**

```markdown
---
created: {YYYY-MM-DD}
source: {project name / paper title}
source_url: {GitHub / arXiv / blog link}
agent: {agent_id}
topic: {主题分类}
confidence: high|medium|low
---

# {项目/论文名称} 深度笔记

## 核心问题
{项目/论文解决什么问题？不超过 3 句}

## 关键方法论
{可迁移的思想、技术方案、设计模式。2-5 条要点}

## 与当前能力的对比

| 维度 | 该项目 | 我们当前 |
|------|--------|---------|
| {维度1} | {该项目做法} | {当前做法} |
| {维度2} | {该项目做法} | {当前做法} |
| {维度3} | {该项目做法} | {当前做法} |
| ... | ... | ... |

## 可立刻借鉴的 3 个点
1. **{可借鉴点1}** — 具体怎么落地（代码/配置/流程改动）
2. **{可借鉴点2}** — 具体怎么落地
3. **{可借鉴点3}** — 具体怎么落地

## 长期影响
{这个项目对 Agent 长期能力的影响评估：
 - 是否值得深度跟进
 - 是否会影响现有技术选型
 - 建议什么时候重新评估}
```

### 笔记质量门控

写完后自动检查：

| 门控项 | 标准 | 失败处理 |
|--------|------|---------|
| 模板完整性 | 5个问题全有 | 补全后再归档 |
| 可行性 | "可立刻借鉴"有具体操作 | 空话→重写 |
| 对比表 | 至少3个维度 | 补充维度 |
| 字数 | 全文 ≥ 300 字 | 太短说明没消化透 |
| 与现有笔记 | 不重复已有主题 | 重复→追加到已有文件 |

---

## 第4层：技能内化 (Skill Update)

当深度笔记中发现以下情况时，需要更新对应 Agent 的 SKILL.md：

### 触发条件
- 发现了新工具/API/工作流 且 与 Agent 职能直接相关
- 发现当前技能文件的步骤已过时或有更好的替代方案
- 发现某操作有新的陷阱或最佳实践

### 更新流程
1. 用 `skill_view(name)` 加载当前 SKILL.md
2. 定位需要更新的段落（命令、参数、步骤、陷阱等）
3. 用 `skill_manage(action='patch')` 做精确替换
4. 在 SKILL.md 的 changelog 或版本注释中记录更新原因

### 更新纪律
- 只更新有实证支撑的内容（经过测试或验证）
- 新发现放在"有待验证"段落，不要直接替代已验证的内容
- 每次更新附上来源链接

---

## 第5層：學習檔案管理 (Archive Management) — v3.0 平坦結構

> 每週深度吸收（5問模板）是主力，但對於每日快速掃描 GitHub Trending，提供更輕量的金字塔格式（結論→背景→核心內容→下一步）。詳見下方「每日快速掃描模式」章節。

## 每日快速掃描模式（Daily Quick Scan）— 金字塔輕量版

### 適用場景

- **每日 Agent 專屬 GitHub 學習**（如 cron 排程每日定時執行）
- 當天只想掃「今天有什麼值得關注的」，不打算寫 300+ 字深度筆記
- Agent 需要保持 daily pulse，而非 weekly deep dive

### 與每週管道的區別

| 維度 | 每週深度吸收 | 每日快速掃描 |
|------|------------|------------|
| 頻率 | 每週一次（週一 06:00） | 每日（08:00 或自訂） |
| 選材量 | 每個 Agent 3-5 篇 | 全局 2-3 個項目 |
| 模板 | 5問深度筆記模板 | 金字塔格式（結論→背景→核心內容→下一步） |
| 檔案目的地 | `學習檔案/業務線｜{主題}·{MMDD}.md` | `决策/{Agent}｜GitHub.md`（Living document，見 templates/agent-daily-github-learning.md 對照表） |
| 輸出長度 | ≥300 字 | 精簡，不超過 8 條核心 |
| 技能更新 | 觸發 SKILL.md patch | 通常不觸發，單純歸檔 |

### 金字塔模板

使用 `templates/agent-daily-github-learning.md`。frontmatter 範例：

```yaml
---
created: 2026-05-18
updated: 2026-05-18
agent: global
category: 決策
status: 活躍
confidence: 已验证
importance: ⭐⭐⭐
source: GitHub Trending 每日學習
tags: [決策, 梅凝, GitHub學習, 出海運營]
---
```

### 快速掃描技術（從實戰中驗證）

---

### 目录结构

```
学习档案/
├── 系统｜总索引.md                  ← 全部 Agent 学习概览
├── 元瑶｜教育研究吸收·0520.md        ← 元瑶学习笔记（时间后缀）
├── 元瑶｜多Agent教育吸收·0517.md
├── 银月｜GitHub知识吸收·0516.md
├── 银月｜提示词方法论.md
└── ...
```

**零子目录。** `学习档案/edu/github-absorb/` `学习档案/media/` 全部消灭。

### 文件命名规则
- 周概览: `业务线｜{主题}·W{周序号}.md`，如 `元瑶｜教育研究吸收·W20.md`
- 深度笔记: `业务线｜{主题}·{MMDD}.md`，如 `元瑶｜多Agent教育吸收·0517.md`
- 方法论: `业务线｜{主题}.md`（无日期，持续更新），如 `银月｜提示词方法论.md`
- 总索引: `系统｜总索引.md`（持续更新）

### 维护规则
- 每篇笔记写入后，更新 `系统｜总索引.md`（追加一行）
- 每周扫描后写周概览文件
- 不再维护各 Agent 独立 index.md（已消灭）

---

## Cron 配置

### 主扫描任务 (每周一 06:00)

使用 `hermes cron create` 创建：

```bash
hermes cron create \
  --name "垂直学习扫描 — 五大Agent" \
  --schedule "0 6 * * 1" \
  --skills "vertical-learning-sop" \
  --deliver "local" \
  --prompt "
请执行垂直学习管道 SOP，按以下步骤：

## 第1步：采集
对于以下5个Agent，分别扫描各自的 GitHub 关键词：
- content（墨笔文创）: content-marketing, copywriting-ai, SEO-tool, xhs-bot, douyin-automation
- edu（墨学教育）: lms-platform, tutoring-ai, course-design, spaced-repetition, ai-tutor
- research（墨研竞情）: gpt-researcher, web-scraping, competitive-intelligence, market-analysis
- dev（墨码开发）: agent-framework, code-generation, claude-code, mcp-server, devops-ai
- autodream（墨梦AutoDream）: self-improving-ai, memory-system, rag-system, agent-evolution

使用 GitHub Search API 搜索最近一周的新项目（stars排序），每个关键词取 Top 3。

### 附加源扫描
- research 同时扫 arXiv cs.AI（curl arxiv API）
- dev 同时扫 GitHub Trending（https://github.com/trending）
- 其他按需要补充

## 第2步：汇总+筛选
按热度评分排序，每个 Agent 选 3-5 篇（热度≥5、直接相关、有可借鉴的方法论）。

## 第3步：精读+写深度笔记
使用深度笔记模板（第3层），每篇一个文件，写入：
/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents/学习档案/业务线｜{主题}·{MMDD}.md

业务线对照: edu→元瑶, media→银月, content→银月, global→梅凝, dev→系统, autodream→系统

## 第4步：更新总索引
在 学习档案/系统｜总索引.md 追加新笔记条目。

## 第5步：质量门控
检查每篇笔记：
- 5个问题都有回答
- 对比表至少3个维度
- 全文≥300字
- 不缺失文件名/来源链接

## 第6步：输出总结
输出本次扫描的概览：
- 总共扫描了多少仓库/论文
- 各Agent选了多少篇
- 是否有值得更新SKILL.md的发现
- 总学习笔记数量
"
```

### 补充任务 (如有需要)

```bash
# 每日 GitHub Trending 快扫（可选，仅 dev + research 两个Agent）
hermes cron create \
  --name "开发者每日GitHub快扫" \
  --schedule "0 18 * * *" \
  --skills "vertical-learning-sop" \
  --deliver "local" \
  --prompt "快速扫描 GitHub Trending 中与 agent-framework, code-generation, mcp-server 相关的新仓库，列出 Top 5 但不写深度笔记。结果写入 /Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents/产出/系统｜GitHub快扫·{date}.md"
```

---

## 一次性初始化

首次使用时，Obsidian vault 已具备 8 根目录结构，无需创建子目录。只需确保总索引存在：

```bash
VAULT="/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents"

# 创建总索引（如不存在）
if [ ! -f "$VAULT/学习档案/系统｜总索引.md" ]; then
  cat > "$VAULT/学习档案/系统｜总索引.md" << 'EOF'
---
created: 2026-05-17
updated: 2026-05-17
agent: system
category: 学习档案
status: 活跃
tags: [学习档案, 索引, 垂直学习]
---

# 学习档案 · 总索引

> 五大Agent垂直学习管道的全部产出。
> 每轮扫描后追加新条目。

## 最近更新
| 日期 | 业务线 | 主题 | 文件名 |
|------|--------|------|--------|
EOF
fi
```

**不再创建各 Agent 子目录和独立 index.md。笔记直接以 `业务线｜{主题}·{日期}.md` 写入 `学习档案/`。**

---

## 故障排查

### GitHub API Rate Limit
- 未认证请求: 60 req/h
- 带 token 请求: 5000 req/h
- 每个关键词取 Top 3，5个Agent共15个关键词，完全在限额内
- 如果超额，限制到每周只扫前3个Agent

### arXiv API Rate Limit
- ~1 req / 3秒
- 脚本中每隔3秒发一次请求，5个关键词约15秒

### 文件写入失败
- 检查 iCloud 路径是否存在
- 检查 `OBSIDIAN_VAULT_PATH` 环境变量
- 尝试直接用 `write_file` 工具

### 笔记质量不达标
- 检查模板是否完整
- 如果"可立刻借鉴"写得太抽象 → 需要具体到代码/配置级别
- 如果对比表的维度数不够 → 重新阅读项目，从项目文档找差异

### Cron 任务不触发
```bash
hermes cron list              # 查看任务状态
hermes cron run <id>          # 手动触发
hermes cron status            # 检查调度器
```

---

## 参考资料

- GitHub REST API: https://docs.github.com/en/rest/search
- arXiv API: https://info.arxiv.org/help/api/index.html
- Semantic Scholar API: https://api.semanticscholar.org/
- Hermes Cron 文档: https://hermes-agent.nousresearch.com/docs/user-guide/features/cron
- Obsidian 写作规范: note-taking/obsidian 技能
- 记忆同步管道: molin-org/molin-memory-pipeline 技能
- **外部系统评估**: `references/mempalace-nuwa-evaluation-20260518.md` — MemPalace (52k⭐, 本地AI记忆) + Nuwa-Skill (19.7k⭐, 思维蒸馏框架) 深度评估，含 Molin-OS 可借鉴的方法论

## 版本历史

- v1.0 (2026-05-17): 初始版本，基于审计报告建议建立五大Agent垂直学习管道
