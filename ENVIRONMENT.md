# 墨麟OS 环境清单 v7.0

> 更新：2026-05-21
> 主机：macOS 26.5 · Apple Silicon (arm64)
> 架构：六司三十四将 · 6 Profile · 6 飞书Bot

## 系统软件

| 软件 | 版本 | 路径 |
|:-----|:-----|:-----|
| macOS | 26.5 | — |
| Homebrew | 5.1.10 | /opt/homebrew |
| Git | 2.50.1 | /usr/bin/git |
| Node.js | v24.14.0 | /opt/homebrew |
| Python 3.11 | 3.11.15 | /opt/homebrew/bin/python3.11 |
| FFmpeg | 8.1.1 | /usr/local/bin/ffmpeg |

## Hermes Agent

- 版本：v0.14.0
- 项目路径：~/Molin-OS/hermes/
- Python：3.11.15 (venv)
- Gateway：6 Profile 独立 Gateway

## 六司 Profile

| Profile | 公司 | 飞书 App ID |
|:--------|:-----|:------------|
| yuanyao | 元瑶 · 教育与用户增长公司 | cli_a956...5cd4 |
| ziling | 紫灵 · 情报与战略调研公司 | cli_aa89...cbc3 |
| yinyue | 银月 · 内容生态与全媒体矩阵公司 | cli_a966...9bd2 |
| meining | 梅凝 · 跨境出海与全球化公司 | cli_aa88...89bb5 |
| songyu | 宋玉 · 创新拓展与商业化公司 | cli_a951...9bcf |
| xuanhu | 玄骨 · 底层中枢与集团赋能公司 | cli_aa88...9bb4 |

## 配置密钥

| 密钥 | 状态 |
|:-----|:----:|
| DEEPSEEK_API_KEY | ✅ |
| DASHSCOPE_API_KEY | ✅ |
| GITHUB_TOKEN | ✅ |
| FEISHU_APP_ID/SECRET (x6) | ✅ |
| SUPERMEMORY_API_KEY | ❌ 已停用 |

## Cron 作业

详见 `config/hermes-agent/cron_jobs.md`（19 个作业定义）。
当前 cron 系统待重建。

## 记忆系统

- MemPalace：567 条 vault/ 索引
- ChromaDB：向量记忆存储
- Supermemory：已停用

## 备份

- GitHub：https://github.com/moye-tech/Molin-OS
- Vault：iCloud Drive (Obsidian)
