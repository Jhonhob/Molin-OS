# MolinOS Ultra — 部署文档

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
| `engine/mirofish/` | `~/Molin-OS/engine/mirofish/` |

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
