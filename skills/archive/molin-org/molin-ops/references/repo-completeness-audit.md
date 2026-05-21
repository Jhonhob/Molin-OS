# 系统-Repo 完整性审计 (System-Repo Completeness Audit)

> 验证本地运行的墨麟 OS 系统是否完全被 GitHub 仓库捕获。

## 场景

用户问「现在的系统是完全同步至 GitHub 吗」「这个仓库包含所有内容吗」「从 GitHub 重新部署能恢复一切吗」时，执行本清单。

## 审计维度

### 1. Git 基础状态

```bash
cd ~/Molin-OS
git status --short         # 未提交的文件变更
git status --short --branch  # 分支 + 远程跟踪状态
git rev-parse HEAD         # 本地 HEAD
git rev-parse origin/main # 远程 HEAD（比较是否一致）
git log --oneline -5       # 最近提交
git diff --stat HEAD       # 未提交变更的文件数
```

### 2. 子模块

```bash
cat .gitmodules                   # 定义的所有子模块
find . -name ".git" -not -path "./.git" -type d  # 实际存在的子模块
# 对每个子模块检查：
#   cd <submodule> && git remote -v && git log --oneline -3
```

### 3. 脚本完整性 — ~/.hermes/scripts/ vs repo/scripts/

```bash
for f in ~/.hermes/scripts/*; do
  basename "$f"
done | while read f; do
  [ -f "$HOME/Molin-OS/scripts/$f" ] && echo "  IN REPO: $f" || echo "  NOT IN REPO: $f"
done
```

特别注意被 cron 使用的脚本是否在 repo 里：
cross_request_worker.py / molin-sync-all.sh / publish_to_xiaohongshu.py

### 4. Skill 完整性 — ~/.hermes/skills/ vs repo/skills/

```bash
ls ~/.hermes/skills/ | while read s; do
  [ -d "$HOME/Molin-OS/skills/$s" ] || echo "  EXTRA: $s"
done
```

额外技能通常是 SOP pack（content-sop-pack, finance-sop-pack 等），它们不在 repo 的 skills/ 目录中。

### 5. Obsidian 知识库

```bash
# 查找所有 .obsidian 目录
find ~ -maxdepth 3 -name ".obsidian" -type d

# 对每个 vault 检查：
#   du -sh <vault-path>        # 大小
#   find <vault-path> -type f | wc -l  # 文件数
#   cd <vault-path> && git remote -v   # 远程指向
#   ls <vault-path>            # 根目录内容
```

关键检查：vault 是否在 repo 的 .vault-git-mirror 中有镜像？
镜像的远程是否指向正确的仓库（Molin-OS vs MolinOS-Ultra）？

### 6. Cron 作业

```bash
hermes cron list
```

对每个 job 检查：
- `last_status: ok` — 正常
- `last_status: error` — 需要排查
- `enabled: true/false` — 是否被暂停
- `script` — 脚本路径，检查脚本是否在 repo 里
- `no_agent` — 脚本型还是 LLM 型

### 7. 系统依赖

```bash
# Python
which python3 && python3 --version
which python3.11

# Node
which node && node --version
which npm && npm --version

# Homebrew
brew list --formula

# Git
git --version

# 关键 pip 包
pip3 list | grep -iE "openai|firecrawl|flask|httpx|pydantic|loguru|rich"
```

### 8. Hermes 配置

```bash
# Config — ~/.hermes/config.yaml (profile-aware)
# .env — ~/.hermes/.env (secrets, 只检查存在性)
# Profiles — ~/.hermes/profiles/ 下每个目录的 .env
# 已注册平台 — ~/.hermes/channel_directory.json
# Gateway 状态 — ~/.hermes/gateway_state.json
```

### 9. 运行时数据（不可通过 repo 复现）

| 路径 | 内容 | 是否关键 |
|------|------|---------|
| ~/.hermes/sessions/ | 历史会话 SQLite | 丢失可接受 |
| ~/.hermes/logs/ | 运行日志 | 丢失可接受 |
| ~/.hermes/cron/output/ | cron 作业执行记录 | 丢失可接受 |

## 输出模板

审计完成后，按以下分类组织结果：

### In-Sync（完全同步）
- 列出的文件/配置路径

### Out-of-Sync（有差异）
- 未提交的文件（数量+列表+类型）

### Missing from Repo（仓库缺失）
- ~/.hermes/scripts/ 中不在 repo 的脚本
- ~/.hermes/skills/ 中不在 repo 的技能  
- 系统依赖工具（需文档化）

### External（独立于 repo）
- Obsidian vault（独立 Git）
- 系统级软件（Python / Node / Homebrew — 需 setup.sh 处理）

## 完整结论格式

```
Molin-OS GitHub — 代码部分：
HEAD (<sha>) 和 origin/main [一致/不一致]
从 <time> 到现在，本地有 <N> 个未提交的改动：
| 文件 | 变化类型 |
|------|---------|
| ...  | ...     |

Obsidian 知识库同步 — [已同步/已断]：
[说明]

其他方面：
- git-backup.sh cron (HH:MM) [正常运行/报错]
- 记忆同步管道 cron (每N分钟) [正常/报错]
- <N> 个 cron 任务中 [X 正常, Y 报错]

要修复缺失的文件/未提交的改动吗？
```
