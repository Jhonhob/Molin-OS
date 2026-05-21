# Affitor/affiliate-skills 深度分析报告

> 项目：https://github.com/Affitor/affiliate-skills
> 星标：400+ | 分支：13 | 提交：58 | 许可证：MIT
> 最新更新：2025年4月

---

## 一、核心分类与体系架构：8阶段飞轮模型

该项目将联盟营销全链路拆解为 **8个阶段、52个技能**，每个技能是一个独立的 `SKILL.md` 文件，构成一个闭环飞轮：

```
  S1 调研 → S2 内容 → S3 博客SEO → S4 落地页
       ↑                              │
       │                              ↓
       └── S6 分析反馈 ◄──── S5 分发 ──┘
                     │
                     ↓
               S7 自动化 → 规模化
                     │
               S8 元技能（横跨所有阶段）
```

### 各阶段核心技能分布

| 阶段 | 技能数 | 核心定位 |
|------|--------|----------|
| **S1 调研** | 9 | 选品、竞品分析、流量评估、角度排序、趋势扫描 |
| **S2 内容** | 7 | 社交帖子、TikTok脚本、Reddit帖子、信息图、调研简报 |
| **S3 博客SEO** | 7 | 长文、对比文、清单文、关键词集群、内容护城河计算 |
| **S4 落地页** | 8 | AIDA页面、展示页、引导页、价值阶梯、担保生成 |
| **S5 分发** | 4 | 个人链接页、邮件序列、社媒排期、GitHub Pages部署 |
| **S6 分析** | 5 | UTM追踪、A/B测试、性能报告、SEO审计、内链优化 |
| **S7 自动化** | 5 | 内容复用、邮件自动化、多项目管理、广告文案、专有数据 |
| **S8 元技能** | 5 | 技能发现、漏斗规划、合规检查、自我改进、品类设计 |

**架构亮点：**
- 每个 `SKILL.md` 包含完整的：YAML frontmatter（元数据）→ Input Schema → Workflow → Output Schema → 链式连接 → 自我验证清单
- `chain_metadata.suggested_next` 让AI自动知道下一个该执行什么技能
- `registry.json` 为机器可读索引，供外部工具和编排系统调用

---

## 二、内容创作类技能的具体实现方式

### 2.1 Viral Post Writer（病毒帖撰写器）

**前置条件触发：** 通过YAML frontmatter中`description`字段定义20+种自然语言触发模式，从"帮我写一篇LinkedIn文章"到"帮我自然地卖X"全覆盖。

**数据驱动创作流程：**
1. **上下文收集** — 检查S1调研阶段是否已运行，自动提取`recommended_program`
2. **产品调研** — 自动 `web_search` 获取产品最新动态、用户痛点、竞品对比
3. **格式研究** — 如果 S1 的 `trending-content-scout` 已运行，直接使用其`pattern_analysis.winning_formats` 数据选择最高互动格式；否则快速搜索社交平台获取信号
4. **病毒框架选择** — 基于平台自动匹配最佳框架（LinkedIn→转型故事，X→话题串，Reddit→真实推荐）
5. **写作规则** — 硬性约束：首行钩子（1.5秒决策）、具体>泛泛、故事>推销、单CTA、FTC合规
6. **自我验证** — 7项检查清单，包括FTC披露位置、禁止词检测、链接放置规则

### 2.2 Infographic Generator（信息图生成器）

- **Type auto-detection**: 根据内容模式自动选择图表类型（stat_highlight / comparison / process_flow / checklist 等8种）
- **多平台尺寸支持**: LinkedIn 1080×1350, Instagram 1080×1080, X 1200×675
- **输出格式**: 支持 spec（结构化JSON）、html（自包含HTML/CSS）、both 三种模式
- **品牌定制**: 支持主色/辅色/强调色、字体风格、logo文字

### 2.3 Content Research Brief（内容调研简报）

**核心价值：让AI不再是"凭空写作"**
- 自动收集真实源文章（`web_search` → `web_fetch` 多个URL）
- 提取具体数据点、引语、统计数据
- 生成3个差异化角度，附带平台适配建议
- 输出可直接被 S2/S3 所有内容技能消费

### 2.4 关键设计模式

1. **Volume Mode** — 内容技能支持"批量模式"，一次生成5-10个变体，让数据选择胜者
2. **Quality Gate** — 每个技能输出前自我检查："我会在我的个人社交账号上分享这个吗？"
3. **Chain Chaining** — 内容→信息图→排期→追踪，形成完整产出链路

---

## 三、跨平台分发策略

### 3.1 分发矩阵（76个渠道，9级分层）

项目在 `docs/distribution-strategy.md` 中制定了极其系统的分发计划：

| 层级 | 渠道数 | 核心渠道 | 策略 |
|------|--------|----------|------|
| **T1 技能注册表** | 8 | skills.sh, ClawHub.ai, SkillsMP, LobeHub | 自动索引，SEO基底 |
| **T2 GitHub Awesome List** | 21 | awesome-claude-code, awesome-agent-skills, awesome-claude-skills | PR提交，永久SEO |
| **T3 发布平台** | 5 | Hacker News Show HN, Product Hunt, DevHunt | 一次性爆发流量 |
| **T4 开发者社区** | 11 | Dev.to, Reddit(r/ClaudeAI/r/LocalLLaMA), Hashnode, Medium | 内容营销 + SEO |
| **T5 AI工具目录** | 8 | Toolify.ai, Futurepedia, AI Agents Directory | SEO外链 |
| **T6 资讯简报** | 6 | TLDR AI, The Rundown AI, Ben's Bites | 媒体曝光 |
| **T7 开源发现** | 6 | GitHub Topics/Trending, AlternativeTo | 自然增长引擎 |
| **T8 Discord社区** | 5 | Anthropic/Claude, Hugging Face, OpenAI | 社区互动 |
| **T9 MCP注册表** | 5 | MCP Registry, PulseMCP, Smithery.ai | 生态扩展 |

### 3.2 4周启动执行计划

- **第1周**：基础设置 + 集中发布（Show HN + Dev.to + Reddit 同日发布，争取GitHub Trending）
- **第2周**：Awesome List PR + Product Hunt + DevHunt
- **第3周**：Newsletter pitches + AI工具目录提交
- **第4周**：长尾社区 + Discord + 跨平台内容再分发

### 3.3 多代理平台适配

项目在 `platforms/` 目录下为每个AI代理平台提供专门配置：

- **ChatGPT** → Custom GPT + GPT Projects + 单对话模式（3种方法）
- **Cursor/Windsurf** → `.cursorrules` 自动配置
- **Gemini CLI** → 专门适配文件
- **OpenClaw** → ClawHub生态
- **Claude Code/Pi** → 完整CLI集成 + MCP Server（hidrix-tools）

**核心理念：** "Any AI that reads text" — 通过 `prompts/bootstrap.md` 单文件，10秒内让任何AI变成联盟营销代理

---

## 四、数据驱动的优化方法

### 4.1 闭环反馈系统（Flywheel的杀手锏）

```
S6 Analytics → S1 Research 反馈回路：
  - conversion-tracker → affiliate-program-search: 高转化品类 → 找更多同品类
  - performance-report → trending-content-scout: 你的内容指标 vs 行业基准
  - performance-report → content-angle-ranker: 实际表现好的角度 → 优化角度评分
  - seo-audit → monopoly-niche-finder: 已排名的关键词 → 找到垄断利基
  - ab-test-generator → purple-cow-audit: 胜出变体 → 什么是"remarkable"
```

### 4.2 标准化的互动评分公式

```python
engagement_score = (likes × 2 + comments × 3 + shares × 5) / max(views, 1) × 1000
```

该公式在 `trending-content-scout` 中统一定义，被所有内容技能引用，确保跨技能数据一致性。

### 4.3 角度排名机制

`content-angle-ranker` 按5个维度加权评分内容角度：
- 竞争度、互动预测、平台适配、时效性、数据支撑度
- 输出可直接被 `viral-post-writer`、`tiktok-script-writer`、`affiliate-blog-builder` 消费

### 4.4 程序评分体系（5维度加权）

```
Earning Potential (30%) + Content Potential (25%) + Market Demand (20%)
+ Competition Level (15%) + Trust Factor (10%) = Overall Score
Verdict: ≥7.5 "Strong Pick" | 5.5-7.4 "Worth Testing" | <5.5 "Skip"
```

### 4.5 内容格式自动分类

项目定义了8种内容格式（comparison / review / tutorial / listicle / reaction / story / demo / explainer）和6种钩子类型（question / shock / bold_claim / demo_first / relatable / contrarian），通过标题和描述自动检测，用于模式分析和角度推荐。

---

## 五、对墨麟全媒体运营的适用建议

### 5.1 可以借鉴的核心方法论

| 墨麟需求 | affiliate-skills 可借鉴方案 |
|----------|---------------------------|
| **内容创作效率** | 采用"调研简报 → 内容技能 → 信息图 → 排期 → 追踪"的链式工作流，不再孤立创作 |
| **跨平台适配** | 设置统一的输出Schema，一个内容源自动适配LinkedIn/X/Reddit/TikTok各平台格式 |
| **数据驱动选角** | 引入 `trending-content-scout` 热力追踪模式，创作前先了解"什么在赢" |
| **闭环反馈** | 建立S6→S1反馈回路：分析数据反向喂给调研层，形成持续优化飞轮 |
| **质量门禁** | 每个内容技能加入Quality Gate检查清单（自检7项），确保输出质量 |
| **规范化的技能模板** | 使用标准化的 `SKILL.md` 模板（frontmatter + schema + workflow + chain），让每个内容生产任务可重复、可度量、可串联 |

### 5.2 可复制的架构设计

1. **Skill-as-a-File** 模式：每个内容生产任务是一个Markdown文件，包含完整指令、输入输出Schema、链式连接——这种"原子化技能"设计让AI自动编排工作流
2. **10秒激活**：一个 `bootstrap.md` 文件让任何AI瞬间获得全部技能知识
3. **跨平台兼容**：一个技能定义同时适配Claude/ChatGPT/Gemini/Cursor等7+代理平台
4. **生态外挂**：通过MCP Server（hidrix-tools）给技能注入实时社交数据能力

### 5.3 具体落地路径

1. **短期（1-2周）**：提取 `prompts/bootstrap.md` 模式，创建墨麟全媒体运营的引导提示词；复制 `template/SKILL.md` 模板
2. **中期（3-4周）**：构建墨麟自己的技能目录，先覆盖内容创作+SNS分发2个阶段（对应 S2+S5），建立内容质量门禁
3. **长期（1-2月）**：实现完整飞轮——调研→创作→分发→分析→反馈；接入实时数据源（类似hidrix-tools MCP）；建立AI驱动的内容优化闭环

---

## 总结

该项目本质上不是"提示词集合"，而是一个 **面向AI代理运营的操作系统**。其核心创新在于：

1. **飞轮架构** — 8个阶段不是线性流程，而是带反馈回路的闭环系统
2. **技能原子化** — 每个SKILL.md是可独立执行、可串联、可替换的"AI微服务"
3. **数据驱动** — 从内容格式选择到角度评分，一切基于真实互动数据
4. **平台无关** — 一次定义，在所有AI代理上运行
5. **开源生态** — MIT许可证 + 社区贡献 + 注册表分发

对墨麟而言，这套体系的借鉴价值远超工具层面——它提供了一种**将全媒体运营工作流系统化、数据化、自动化的方法论框架**，而不仅仅是50个提示词。
