# 墨麟OS v7.0 · 技能体系全盘重构方案

> 版本: 1.0
> 日期: 2026-05-21
> 状态: 待创始人审批
> 关联: `docs/skills-registry-v7.md` (自动生成注册表)

---

## 一、现状诊断

### 1.1 核心数据

| 指标 | 数值 | 评级 |
|------|------|:----:|
| 技能总数 (SKILL.md) | **646** | 🔴 臃肿 |
| 总文件数 (.md) | **1,485** | 🔴 失控 |
| 有 Frontmatter | 598/646 (92.6%) | 🟡 |
| 有 `owner_domain` 标注 | **0/646 (0%)** | 🔴 致命 |
| 有 `intent_tags` | 247/646 (38.2%) | 🔴 |
| 缺 Frontmatter | 48 | 🟡 |
| Hub 安装技能 | **584** (90.4%) | 🔴 外来 |
| 墨麟定制技能 | 26 (4.0%) | 🟢 |
| 其他本地技能 | 36 (5.6%) | 🟡 |

### 1.2 自动分类结果（六司）

| 司 | 技能数 | 占比 | Top Worker |
|----|--------|------|-----------|
| 💀 玄骨 (中枢) | 325 | 50.3% | 墨码 187 |
| 🌸 元瑶 (教育/增长) | 112 | 17.3% | 墨增 51 |
| 🌙 银月 (内容/媒体) | 82 | 12.7% | 墨笔 45 |
| 🍃 宋玉 (商业) | 64 | 9.9% | 墨商 59 |
| 🔮 紫灵 (情报) | 57 | 8.8% | 墨研 26 |
| ❄️ 梅凝 (跨境) | 6 | 0.9% | 墨译 3 |

### 1.3 根因分析

```
为什么技能体系失控？
  ↓
① Hermes skills install 命令一键安装了 584 个 Hub 技能（占 90%）
  ↓
② 没有任何「安装即用」机制 — 安装后就被遗忘，从未被调用
  ↓
③ 没有 Frontmatter 标准 — SOUL.md 触发表中引用的技能无法自动发现
  ↓
④ 387 个扁平目录 — 无法区分「核心技能」和「垃圾技能」
  ↓
结果：646 个技能中，真正被系统调用的不超过 50 个，
     剩下 596 个是纯粹的「数字垃圾」
```

---

## 二、目标架构

### 2.1 三层目录结构

```text
skills/
├── global/                      ← 玄骨 L0 · 跨公司通用技能 (~15 个)
│   ├── file_reader.md
│   ├── web_search.md
│   └── ...
│
├── domains/                     ← 六司 L1 · 领域专用技能 (~50 个)
│   ├── ziling_intelligence/     ← 紫灵·情报 (墨研/墨数/墨影/墨嗅/墨投)
│   │   ├── arxiv_scraper.md
│   │   ├── blogwatcher.md
│   │   └── competitor_price.md
│   ├── yinyue_content/          ← 银月·内容 (墨笔/墨图/墨剪/墨链/墨播/墨星)
│   │   ├── xiaohongshu_writer.md
│   │   ├── video_editor.md
│   │   └── live_streamer.md
│   ├── yuanyao_education/       ← 元瑶·教育 (墨增/墨销/墨导/墨学/墨创/墨域)
│   │   ├── course_designer.md
│   │   ├── growth_hacker.md
│   │   └── community_manager.md
│   ├── meining_outbound/        ← 梅凝·跨境 (墨译/墨媒/墨站/墨航/墨盾)
│   │   ├── taiwan_localizer.md
│   │   ├── shopee_manager.md
│   │   └── gdpr_compliance.md
│   └── songyu_business/         ← 宋玉·商业 (墨商/墨案/墨关/墨聚/墨采)
│       ├── bd_prospector.md
│       ├── proposal_writer.md
│       └── vendor_sourcer.md
│
├── workers/                     ← 三十四将 L2 · Worker 独占技能 (~40 个)
│   ├── mo_xiu/                  ← 墨嗅·趋势嗅探器
│   │   ├── darkweb_monitor.md
│   │   └── policy_tracker.md
│   ├── mo_jian/                 ← 墨剪·视频后期
│   │   └── auto_capcut_api.md
│   └── ...
│
└── archive/                     ← 沉睡技能 (~550 个)
    ├── ab-test-analysis/
    ├── agent-design-ux-researcher/
    └── ... (未被系统调用的 Hub 技能)
```

### 2.2 标准化 Frontmatter 模板

```yaml
---
skill_id: "arxiv_scraper_v1"           # 全局唯一ID
name: "arXiv 最新论文抓取器"            # 人类可读名
description: "从 arXiv API 检索最新 AI/ML 论文，提取摘要和链接"
owner_domain: "ziling"                 # 归属领域: ziling|yinyue|yuanyao|meining|songyu|xuangu
owner_worker: "mo_xiu"                 # 归属Worker: mo_xiu... 或 null (领域通用)
intent_tags:                           # 语义标签 → ChromaDB 向量化
  - "学术检索"
  - "AI论文"
  - "情报收集"
  - "arXiv"
parameters:                            # 调用参数
  - name: "query"
    type: "string"
    description: "检索关键词"
  - name: "max_results"
    type: "int"
    default: 5
version: "1.0.0"
status: "active"                       # active|deprecated|experimental
---
```

---

## 三、584 Hub 技能 → 六司三十四将分类映射

### 3.1 分类逻辑

| 判定维度 | 权重 | 说明 |
|---------|------|------|
| 技能名称/描述中的关键词 | 60% | 匹配六司关键词表 (见 `scripts/generate_registry.py`) |
| `metadata.hermes.tags` 标签 | 25% | Hub 自带标签 |
| 技能所在目录名 | 15% | 原始安装目录 |

### 3.2 六司关键词速查表

```
💀 玄骨: git, debug, deploy, security, database, api, cli, docker, 
         testing, monitoring, memory, vector, embedding, hermes, 
         mlops, fine-tuning, architecture

🔮 紫灵: research, arxiv, osint, scrape, rss, monitor, trend, 
         competitor, data analysis, visualization, prediction, polymarket

🌙 银月: content, copywriting, social media, image, video, audio, 
         design, animation, seo, publish, tiktok, xiaohongshu, youtube

🌸 元瑶: education, learning, course, growth, conversion, crm, 
         sales, pricing, strategy, okr, ideation, ab test, persona

❄️ 梅凝: translation, localization, global, cross-border, ecommerce, 
         shopify, shopee, compliance, gdpr, supply chain, trade

🍃 宋玉: business, b2b, sales, proposal, procurement, negotiation, 
         investor, legal, contract, airtable, linear, email, calendar
```

### 3.3 分类结果摘要

| 司 | 技能数 | 代表性技能 |
|----|--------|-----------|
| 💀 玄骨 | 325 | nano-pdf, apple-notes, claude-code, codex, llama-cpp, vllm, huggingface-hub, ollama, hermes-agent, native-mcp, github-*, memory-*, systematic-debugging |
| 🌸 元瑶 | 112 | course-designer, growth-hacker, student-crm, conversion-optimizer, sales-strategist, ab-test-analysis, brainstorm-*, sprint-plan, okr-*, user-personas |
| 🌙 银月 | 82 | xiaohongshu-*, youtube-content, copywriting, comfyui, manim-video, ffmpeg-*, songwriting, pixel-art, excalidraw, baoyu-*, seo-* |
| 🍃 宋玉 | 64 | himalaya, imessage, airtable, linear, notion, google-workspace, finance-report, legal-review, xianyu-automation, zhubajie-automation |
| 🔮 紫灵 | 57 | arxiv, blogwatcher, polymarket, last30days, osint-investigation, market-research, competitor-analysis, llm-wiki, darwinian-evolver |
| ❄️ 梅凝 | 6 | molin-global, taiwan-localization, taiwan-market-skill, molin-legal, legal-review, molin-growth-marketing |

> 完整分类表见 `docs/skills-registry-v7.md`（646 行详细表格）

### 3.4 批量 Frontmatter 注入方案

针对 **48 个缺 Frontmatter** 和 **399 个缺 intent_tags** 的技能：

```python
# scripts/batch_inject_frontmatter.py
# 读取 skills-registry-v7.json 中的分类结果
# 为每个技能注入标准化 YAML Frontmatter
# 
# 逻辑：
# 1. 已有 Frontmatter → 追加缺失字段 (owner_domain, owner_worker, intent_tags)
# 2. 无 Frontmatter → 创建全新 Frontmatter
# 3. 保护原有内容不被修改
```

---

## 四、执行计划（4 个 Phase，3 天）

### Phase 0: 前置审计（已完成 ✅）

- [x] `scripts/generate_registry.py` — 扫描 646 技能，输出 JSON + Markdown
- [x] `docs/skills-registry-v7.md` — 六司分类注册表 (自动生成)
- [x] `docs/skills-registry-v7.json` — 结构化数据，供后续脚本消费

---

### Phase 1: 技能分流（预计 2h）

**目标**: 646 → ~100 活跃 + 546 archive

**脚本**: `scripts/reorganize_skills.py`

**逻辑**:
```
FOR EACH skill IN registry:
    IF skill IN 引用清单 (SOUL/Cron/Persona):
        → 保留到 domains/ 或 workers/ 目录
    ELIF skill 被标记为墨麟定制:
        → 保留到 domains/ 或 workers/ 目录
    ELSE:
        → 移动到 archive/ 目录
```

**引用清单提取**（需扫描的文件）:
1. `SOUL.md` — 所有 Agent 的技能触发表
2. `config/hermes-agent/cron_jobs.md` — Cron Job 中引用的 skill
3. 6 个 Agent Persona 文件（`~/.hermes/profiles/*/persona.md` 或 `config/` 中的 persona 定义）
4. `AGENTS.md` — 系统提示中引用的 skill

**产出**:
- `skills/archive/` — 546 个沉睡技能
- `skills/domains/*/` — ~50 个领域技能
- `skills/global/` — ~15 个公共技能
- `skills/workers/*/` — ~40 个 Worker 独占技能

---

### Phase 2: 元数据标准化（预计 3h）

**目标**: 646 个技能全部拥有标准化 Frontmatter

**脚本**: `scripts/batch_inject_frontmatter.py`

**注入字段**:
```yaml
skill_id: "{dirname}_v1"        # 自动生成
name: "{从原 Frontmatter 提取}"
owner_domain: "{从分类结果}"     # 自动分类
owner_worker: "{从分类结果}"     # 自动分类  
intent_tags: ["{从 tags 提取}"] # 从 Hub metadata 或自动推断
version: "1.0.0"
status: "active"
```

**处理三种情况**:
| 情况 | 文件数 | 操作 |
|------|--------|------|
| 有完整 Frontmatter + 缺 owner_domain | 598 | 追加 owner_domain/owner_worker/intent_tags |
| 无 Frontmatter | 48 | 创建全新 Frontmatter |
| YAML 解析错误 | 1 | 手动修复 |

**注意**: `archive/` 中的技能也需要 Frontmatter，以便将来随时激活。

---

### Phase 3: RAG 检索引擎部署（预计 2h）

**目标**: 部署 `molib/skill_retriever.py`，替换手动 `skill_view()`

**文件**:
- `molib/skill_retriever.py` — ChromaDB 向量检索引擎（你的代码）
- `molib/router.py` — Hermes 路由层（你的代码，需适配现有架构）
- `scripts/index_skills.py` — 启动时批量索引所有技能

**集成点**:
1. `Makefile` 添加 `index-skills` 目标
2. Cron Job `#1 记忆同步` 追加技能索引刷新步骤
3. 6 个 Agent Persona 中注入路由逻辑

**验证**: 运行后 `python -c "from molib.skill_retriever import SkillRegistry; r = SkillRegistry(); print(len(r.retrieve_skills('生成小红书爆款文案', top_k=3, domain_filter='yinyue')))"` 期望返回 3。

---

### Phase 4: 飞轮管线注入（预计 2h）

**目标**: 每个公司的 Cron/Flywheel 配置引用技能时使用语义检索而非硬编码

**文件**: `config/domains/*.yaml` (6 个)

**改造前** (`cron_jobs.md`):
```yaml
# Cron Job #15 内容工厂
skills: [content-sop-pack, gatekeeper-sop, kpi-tracker]
```

**改造后** (`config/domains/yinyue.yaml`):
```yaml
flywheel:
  content_factory:
    cron: "0 22 * * *"
    trigger_worker: "mo_bi"
    skill_retrieval:
      intent: "生成小红书和公众号内容"
      domain_filter: "yinyue"
      top_k: 3
    fallback_skills:         # 检索失败时的兜底
      - "content-sop-pack"
```

---

## 五、风险与回滚

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| 错将活跃技能移入 archive | 中 | 高 | archive/ 目录保留，`hermes skills install` 从 archive 恢复 |
| 自动分类错误（Worker 分配不对） | 中 | 低 | Frontmatter 可随时手动修改，不影响系统运行 |
| ChromaDB 索引失败 | 低 | 中 | 保留 `skill_view()` 作为 fallback，不删除现有调用 |
| Cron 改造后飞轮断裂 | 中 | 高 | 分 Profile 灰度：先改银月，验证 3 天后再全量 |

---

## 六、成功标准

| 指标 | 当前 | 目标 |
|------|------|------|
| 活跃技能数 | 646（全混在一起） | ~100（分三层） |
| `owner_domain` 覆盖率 | 0% | 100% |
| `intent_tags` 覆盖率 | 38.2% | 100% |
| Frontmatter 覆盖率 | 92.6% | 100% |
| 技能调度方式 | 手动 `skill_view(name)` | RAG 语义检索 `retrieve_skills(intent)` |
| Cron 飞轮耦合 | 硬编码技能名 | 语义意图 + 自动召回 |

---

## 七、附录

- `docs/skills-registry-v7.md` — 646 技能完整注册表 (自动生成)
- `docs/skills-registry-v7.json` — 结构化数据
- `scripts/generate_registry.py` — 注册表生成器
- `scripts/batch_inject_frontmatter.py` — Phase 2 脚本 (待创建)
- `scripts/reorganize_skills.py` — Phase 1 脚本 (待创建)
- `molib/skill_retriever.py` — Phase 3 (待创建)
