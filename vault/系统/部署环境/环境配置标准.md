---
title: 墨麟 OS 环境配置与部署标准
status: 迭代中 (Active)
last_updated: 2026-05-19
agent_sync: true
---

## 系统部署文档

## 系统要求

| 组件 | 最低版本 | 推荐版本 |
|------|---------|---------|
| macOS | 14.0+ | 15.0+ |
| Python | 3.10 | 3.11+ |
| Node.js | 22 | 24+ |
| Git | 2.0 | 2.40+ |
| 内存 | 8GB | 16GB+ |
| 磁盘 | 20GB | 50GB+ |

## 一键部署

```bash
# 克隆仓库
git clone https://github.com/moye-tech/MolinOS-Ultra.git
cd MolinOS-Ultra

# 配置环境变量
cp env/.env.example .env
# 编辑 .env 填入你的 API keys

# 执行部署
bash scripts/deploy.sh

# 启动
make start
```

## 环境变量说明

| 变量 | 必填 | 说明 | 获取方式 |
|------|------|------|---------|
| `DEEPSEEK_API_KEY` | ✅ | LLM API 密钥 | platform.deepseek.com |
| `SUPERMEMORY_API_KEY` | ✅ | 长期记忆服务 | supermemory.ai |
| `GITHUB_TOKEN` | ✅ | GitHub API 访问 | github.com/settings/tokens |
| `BROWSERBASE_API_KEY` | ❌ | 浏览器自动化 | browserbase.com |
| `EXA_API_KEY` | ❌ | AI 搜索 | exa.ai |

## 首次安装 Hermes Agent

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

## 验证部署

```bash
make health
```

正常输出应显示：
- Hermes Agent 已安装
- 5 个 Gateway 全部 running
- API Keys 已配置

## 目录映射

| 仓库路径 | 部署路径 |
|---------|---------|
| `agents/<name>/` | `~/.hermes/profiles/<name>/` |
| `skills/` | `~/.hermes/skills/` |
| `molib/` | `~/Molin-OS/` |
| `tools/MiroFish/` | `~/Molin-OS/MiroFish/` |

## 日常维护

```bash
make status    # 查看状态
make health   # 健康检查
make sync     # 手动同步记忆
make backup   # 手动备份到 GitHub
make restart  # 重启全部服务
```

## 迁移到新机器

1. 新机器安装环境（Python、Node.js、Git）
2. 克隆仓库：`git clone https://github.com/moye-tech/MolinOS-Ultra.git`
3. 配置 .env
4. `bash scripts/deploy.sh`
5. `make start`

## 部署流程

## 2026-05-17

### 结论
━━━━━━━━━━━━━━━━━━ 📊 三厂周报 · 2026-05-16 ━━━━━━━━━━━━━━━━━━

### 背景
今天能集成的部分有哪些，融合进你的业务来补强

### 核心内容
- 都部署完了，给你汇个总。 ━━━━━━━━━━━━━━━━━━━ ✅ A方案 · 全部跑通
- 清楚了。我需要做两件事： 第一，建立对学而思/猿辅导/作业帮的持续研究机制 第二，升级GitHub搜索体系，更主动地找项目补强业务
- 所有API全部通过验证。服务器已启动。 ━━━━━━━━━━━━━━━━━━━━ ✅ 玄骨设计 · 控制台已上线

### 下一步
方向

## 工具链规范

## 银月
|
| hermes-cli | terminal, file, web, browser, search |
| delegation | delegate_task, cronjob |
| skills | skill_view, skill_manage, skills_list |
| memory | memory, session_search |

## 玄骨
|
| hermes-cli | terminal, file, web, browser, search |
| delegation | delegate_task, cronjob |
| skills | skill_view, skill_manage, skills_list |
| memory | memory, session_search |

## 梅凝
|
| hermes-cli | terminal, file, web, browser, search |
| delegation | delegate_task, cronjob |
| skills | skill_view, skill_manage, skills_list |
| memory | memory, session_search |

## 宋玉
|
| hermes-cli | terminal, file, web, browser, search |
| delegation | delegate_task, cronjob |
| skills | skill_view, skill_manage, skills_list |
| memory | memory, session_search |

## 元瑶
|
| hermes-cli | terminal, file, web, browser, search |
| delegation | delegate_task, cronjob |
| skills | skill_view, skill_manage, skills_list |
| memory | memory, session_search |

## 部署方案决策

> 竞争态势监控 + 产品经理竞品分析框架 + 情报日报输出。

## 情报日报 2026-05-15

### 执行摘要

本周 AI 行业密集震荡，三巨头旗舰集中发布：

- **Anthropic Claude 4** — 发布
- **OpenAI GPT-4.1** — 发布
- **Google Gemini 3.0** — 发布
- **EU AI Act** — 5月14日正式执法，成为行业分水岭
- **AI Agent** — 集体从 Demo 走向企业级部署
- **AI 视频生成** — 进入实时时代

### 竞争态势简报

#### 主要玩家动态 (截止 2025 年中训练数据)

| 公司 | 关键动向 | 影响评估 |
|------|---------|---------|
| OpenAI | GPT-4.1 发布，多模态深化 | 行业基准上移 |
| Google DeepMind | Gemini 3.0，生态整合 | Android/Workspace 绑定 |
| Anthropic | Claude 4，安全优先定位 | 企业合规市场 |
| Meta AI | Llama 开源持续推进 | 开源生态领导者 |
| xAI/Grok | 实时数据接入 X 平台 | 社交媒体 AI 差异化 |

> 注: 以上基于训练数据。2025 下半年至今动态需联网搜索补充。

## 竞品分析框架

### 产品经理竞品分析配置

- **触发方式**: cron 定时 + 手动调用 `competitor-analysis` 技能
- **覆盖维度**: 产品功能、定价策略、市场定位、技术栈、团队规模
- **输出格式**: 结构化 JSON → Obsidian + Supermemory 双写

### 情报收集管道

```
cron (0700 daily) → competitor-analysis skill → web_search 多轮
→ 结构化编译 → JSON 输出 → Obsidian/Supermemory 双写
```

## 待执行

- [ ] EU AI Act 合规要求对墨麟各业务线的影响评估
- [ ] Claude 4 / GPT-4.1 / Gemini 3.0 对墨麟技术栈的适配分析
- [ ] 竞争态势简报升级为周报格式

## 修订日志 (Changelog)

- **2026-05-19**: 从 4 个部署相关文件合并：部署文档、流程、工具链、方案决策
