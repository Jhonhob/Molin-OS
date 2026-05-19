---
title: Obsidian工作流标准
status: 活跃
last_updated: 2026-05-19
agent_sync: true
---

Obsidian双通道同步(Supermemory+Obsidian vault)是墨麟OS记忆管线的核心写入路径。Agent产出通过自动同步脚本推送到Vault对应目录。

---

## 双通道架构

Supermemory提供语义检索能力，Obsidian提供全文检索能力。Agent记忆同时写入两个通道，确保冗余和检索灵活性。

同步脚本体系：sync_memory.py(会话记忆分类写入)、obsidian_sync.py(报告同步)、collect_architecture.py(架构采集)、relay_to_obsidian.py(Relay产出写入)。

## 触发模式

所有同步在Cron定时任务中自动触发，不依赖用户手动操作。内容产出在完成后自动归类写入目标目录。

## 写入规范

所有写入遵循内容规范(SOP)，强制包含YAML frontmatter、TL;DR、结构化正文。不合规内容被自动拒绝并记录警告日志。
