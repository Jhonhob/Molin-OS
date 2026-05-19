---
title: Obsidian工作流标准
status: 活跃
last_updated: 2026-05-19
agent_sync: true
frameworks_applied:
  - SCQA
  - MECE
  - PDCA
  - DIKW
---

> **TL;DR — 核心结论**
>
> Obsidian vault + Supermemory 双通道架构是墨麟OS记忆管线的核心写入路径。Agent产出通过4个同步脚本（sync_memory.py / obsidian_sync.py / collect_architecture.py / relay_to_obsidian.py）自动推送到Vault对应目录和Supermemory语义索引。每小时整点由Cron Job `210cba244f36` 触发管道执行，确保Agent记忆在任意时刻可在双通道中检索。

---

## SCQA：为什么是双通道架构？

### S 情境

墨麟OS已接入5个Agent（玄骨中枢、元瑶教育、银月传媒、梅凝出海、宋玉创业），每天自动产生数十份文档。这些文档需要同时满足两种检索需求：
- **精确检索**：Agent需要全文搜索已写入的产出、配置、规范——用 Obsidian 的文件系统和全文搜索实现
- **语义检索**：Agent需要按语义相似度召回相关记忆，不依赖文件名和关键词——用 Supermemory 向量数据库实现

### C 冲突

在决定双通道架构之前，单一方案遇到了以下问题：

| # | 尝试方案 | 失败原因 | 后果 |
|---|---------|---------|------|
| 1 | 仅用 Obsidian vault | 文件系统无向量能力，Agent无法按语义召回旧记忆 | RAG召回率<50%，Agent重复询问相同问题 |
| 2 | 仅用 Supermemory | API调用和网络延迟导致文档写入不可靠；无本地离线访问 | 网络中断时Agent完全失忆 |
| 3 | 纯 Git 版本控制 | 写入->commit->push 延迟高，文件系统无结构化索引 | 非开发人员无法使用，检索体验差 |
| 4 | 双通道但无自动同步 | Agent需手动写入两个通道，经常遗漏一个通道 | 数据不一致，一个通道的更新另一个通道没有 |

### Q 疑问

如何在Agent生态持续扩张的情况下，确保每一次产出**同时、自动、可靠**地写入语义检索（Supermemory）和文件系统（Obsidian vault）两个通道，且在任意一个通道出现故障时不影响另一个？

### A 解答

**每整点 Cron 触发的四步同步管道** + **每个脚本同时写入两个通道** + **定稿级别的幂等设计和冲突处理**。下文详细说明。

---

## 决策记录：为什么 Supermemory + Obsidian 双通道？

| 维度 | 选定方案：双通道 | 被拒绝方案 1：Notion | 被拒绝方案 2：单向量库 | 被拒绝方案 3：Git-only |
|------|-----------------|---------------------|----------------------|----------------------|
| **检索方式** | 全文搜索 + 语义搜索 | 仅全文搜索（API受限） | 仅语义搜索 | 仅grep全文搜索 |
| **离线访问** | ✅ Obsidian本地文件 | ❌ 需要网络 | ❌ 需要网络 | ✅ 本地仓库 |
| **API可靠性** | ✅ 双通道互为备份 | ❌ 单点故障 | ❌ 单点故障 | ✅ 本地操作 |
| **写入延迟** | 秒级（本地文件） | 秒级但有API限流 | 秒级但有API限流 | 分钟级（commit+push） |
| **非技术用户** | ✅ Obsidian GUI | ✅ Notion GUI | ❌ 无GUI | ❌ 需Git知识 |
| **向量检索** | ✅ Supermemory | ❌ 需额外插件 | ✅ 本身即有 | ❌ 无法实现 |
| **成本** | 免费（本地）+ API | 订阅制 | API调用费用 | 免费 |
| **Agent写入便利性** | ✅ 本地文件直接写 | ❌ API调用限制 | ✅ API直接写 | ❌ Git封装复杂 |
| **跨设备同步** | ✅ iCloud + Supermemory API | ✅ 云服务 | ✅ API | ❌ 需手动push |
| **长期归档** | ✅ 永久本地存储 | ❌ 导出麻烦 | ❌ 依赖服务存续 | ✅ Git历史 |

**核心原则**：双通道互为冗余且不共享故障域。Obsidian 通道是"权威副本"（source of truth），Supermemory 通道是"检索加速层"。两者通过 `agent_sync=true` 标志关联。

---

## 同步脚本规范

以下按执行顺序列出管道中的4个同步脚本。

### 1. sync_memory.py — 会话记忆分类写入

```
命令签名
  python3 ~/Molin-OS/scripts/sync_memory.py
  python3 ~/Molin-OS/scripts/sync_memory.py --dry-run

路径
  ~/Molin-OS/scripts/sync_memory.py

调用方式
  由 molin-sync-all.sh 调用
  > /opt/homebrew/bin/python3.11 "$SCRIPTS_DIR/sync_memory.py"

参数
  --dry-run    仅预览即将同步的内容，不实际写入

读取源
  Agent会话记忆：~/.hermes/profiles/{agent}/memories/MEMORY.md, USER.md
  每个Agent使用 container_tag 实现隔离（edu/media/global等）

写入目标
  Obsidian：产出/{agent}｜{source}_{hash}.md
    - 文件名示例：产出/元瑶｜memory_a1b2c3d4.md
  Supermemory：按 container_tag 分类，metadata 包含 source/hash

同步策略
  hash-based 增量同步：每条记忆内容取 SHA256[:16] 作为唯一ID
  sync_state.json 跟踪已同步的 hash 集合

前置依赖
  - ~/.hermes/profiles/{agent}/memories/MEMORY.md 存在
  - SUPERMEMORY_API_KEY 环境变量或 ~/.zprofile 中配置
  - supermemory 第三方 SDK 可用（pip install supermemory）

输出写入目录表
  Obsidian Vault 路径                                读取源
  ─────────────────────────────────────────────────  ──────────────────────
  产出/元瑶｜memory_{hash}.md                         edu: MEMORY.md
  产出/元瑶｜user_{hash}.md                           edu: USER.md
  产出/银月｜memory_{hash}.md                         media: MEMORY.md
  ...（按Agent扩展）
```

### 2. obsidian_sync.py — 报告同步

> ⚠️ **当前状态**：已禁用（`molin-sync-all.sh` 中 Step 2 被注释）。
> 等待升级到 v3.0 flat vault 结构后恢复。

```
命令签名
  python3 ~/Molin-OS/scripts/obsidian_sync.py
  python3 ~/Molin-OS/scripts/obsidian_sync.py --dry-run

路径
  ~/Molin-OS/scripts/obsidian_sync.py

调用方式
  由 molin-sync-all.sh 调用（当前禁用）
  > /opt/homebrew/bin/python3.11 "$SCRIPTS_DIR/obsidian_sync.py" $DRY_RUN

参数
  --dry-run    仅预览

写入目标
  （设计目标）
  Obsidian：向 vault 中 Agent 生成的报告文档推送到对应目录
  Supermemory：同步到语义索引

前置依赖
  - Agent 报告产出目录存在
```

### 3. collect_architecture.py — 架构采集

```
命令签名
  python3 ~/Molin-OS/scripts/collect_architecture.py

路径
  ~/Molin-OS/scripts/collect_architecture.py

调用方式
  由 molin-sync-all.sh 调用
  > export SUPERMEMORY_API_KEY && /opt/homebrew/bin/python3.11 "$SCRIPTS_DIR/collect_architecture.py"

参数
  无（当前不支持 --dry-run）

写入目标
  Obsidian vault：系统层/ 和 业务层/ 下的架构决策文档
  Supermemory：架构知识的语义索引

前置依赖
  - Agent 架构记忆文件存在
  - SUPERMEMORY_API_KEY 有效
```

### 4. relay_to_obsidian.py — Relay产出写入

```
命令签名
  python3 ~/Molin-OS/scripts/relay_to_obsidian.py
  python3 ~/Molin-OS/scripts/relay_to_obsidian.py --dry-run

路径
  ~/Molin-OS/scripts/relay_to_obsidian.py

调用方式
  由 molin-sync-all.sh 调用
  > /opt/homebrew/bin/python3.11 "$SCRIPTS_DIR/relay_to_obsidian.py"

参数
  --dry-run    仅预览

扫描目录
  ~/Molin-OS/relay/shared/results/    — arxiv 每日论文等
  ~/Molin-OS/relay/side/results/      — 副业价格监控等

写入目标
  Obsidian：知识/玄骨｜每日·Arxiv论文.md
            知识/玄骨｜每日·副业价格监控.md
  Supermemory：按内容分类存储

同步策略
  fingerprint-based 增量同步：(mtime_ns, size) 作为指纹
  relay_sync_tracker.json 记录每文件的指纹，跳过已同步内容
  幂等：同一文件再次运行不会重复写入

前置依赖
  - relay 目录存在且有新文件
  - SUPERMEMORY_API_KEY（超级记忆同步时）
```

---

## Crontab 配置表

| 调度 | Job ID | 名称 | 脚本/入口 | 日志位置 | 依赖 |
|------|--------|------|-----------|---------|------|
| `0 * * * *` ⏸️ | `210cba244f36` | Molin-OS 记忆同步 — 每小时 | `molin-sync-all.sh` → 管道四步 | `~/.hermes/cron/output/` | 步骤间串行 |
| `0 2 * * *` ✅ | `5cd81602c531` | Molin-OS 每日 Git 备份 02:00 | `git-backup.sh` | `~/.hermes/cron/output/` | 无 |
| `0 7 * * *` ✅ | `9dd66fafeb6d` | arxiv 每日论文扫描 | `daily_arxiv_scan.sh` | `~/.hermes/cron/output/` | 无 |
| `30 9 * * *` ✅ | `d1e92fbc6c8d` | 副业每日价格监控 | `daily_side_price_monitor.sh` | `~/.hermes/cron/output/` | 无 |
| `*/15 * * * *` ✅ | `bad81fa1d323` | 跨线请求轮询 | `cross_request_worker.py` | `~/.hermes/cron/output/` | 无 |
| `0 9 * * 1` ⏸️ | `61cc88accaa9` | Vault合规周检 | LLM驱动 | Hermes日志 | Vault文件扫描 |
| `0 8 * * *` ⏸️ | `a169caa8c9ac` | 梅凝每日GitHub学习 | LLM驱动 | Hermes日志 | 无 |

> **图例**: ✅ 已启用 · ⏸️ 已暂停 · ❌ 已禁用
>
> ⏸️ 暂停原因（2026-05-19）: 整体系统迁移到v3.0 flat vault结构，Job `210cba244f36` 的管道步骤（sync_memory等）处于脚本升级窗口，升级完成后重新启用。

### molin-sync-all.sh 管道内部计时和重试

```
molin-sync-all.sh 入口
  │
  ├── [Step 1] sync_memory.py
  │   ├── 成功 → 进入 Step 2
  │   └── 失败 → 脚本退出（set -e），记录错误到 stdout+stderr
  │               Cron 下次整点重试，不自动重试
  │
  ├── [Step 2] obsidian_sync.py  ⏸️ DISABLED
  │
  ├── [Step 3] collect_architecture.py
  │   ├── 成功 → 进入 Step 4
  │   └── 失败 → 脚本退出（set -e），同上
  │
  └── [Step 4] relay_to_obsidian.py
      ├── 成功 → 管道完成，last_status=ok
      └── 失败 → 脚本退出，last_status=error
```

---

## 目录映射表：哪个脚本写哪个Vault目录

| 脚本 | 写入的Obsidian目录 | 写入的Supermemory容器 | iCloud同步 |
|------|-------------------|----------------------|-----------|
| `sync_memory.py` | `产出/{agent}｜{source}_{hash}.md` | `container_tag={agent}` | ✅ 在vault路径下，iCloud自动同步 |
| `obsidian_sync.py` ⏸️ | 待定（升级后确定） | 待定 | ✅ 同 |
| `collect_architecture.py` | `系统层/`、`业务层/` 下的架构文档 | `architecture` | ✅ 同 |
| `relay_to_obsidian.py` | `知识/玄骨｜每日·Arxiv论文.md`、`知识/玄骨｜每日·副业价格监控.md` | 按内容分类 | ✅ 同 |

> 所有写入的 Obsidian 路径均在 `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/` 下，
> 因此所有文件自动通过 iCloud 同步到所有设备。

---

## 完整同步周期场景

### 场景：飞书会话产生一条记忆 → 最终出现在 Obsidian vault

```
时间线

T-5min ─ Agent（元瑶教育）在飞书中完成一次用户咨询
          └── 新记忆被写入 ~/.hermes/profiles/edu/memories/MEMORY.md

T+0min ─ Cron Job 210cba244f36 触发（每小时整点）
          └── molin-sync-all.sh 开始执行

T+0s  ─ [Step 1] sync_memory.py 运行
          ├── 读取 MEMORY.md → 发现 1 条新记忆（hash: a1b2c3d4 不在 sync_state.json 中）
          ├── 写入 Obsidian：~/.../Documents/产出/元瑶｜memory_a1b2c3d4.md
          │     ┌─────────────────────────────────────┐
          │     │ ---                                │
          │     │ tags: [edu/memory, edu/agent]      │
          │     │ created: 2026-05-19T18:00:00+00:00 │
          │     │ source: memory                     │
          │     │ hash: a1b2c3d4                     │
          │     │ ---                                │
          │     │                                    │
          │     │ ## 记忆内容                          │
          │     │ 用户咨询关于课程排期调整...          │
          │     └─────────────────────────────────────┘
          ├── 写入 Supermemory：client.documents.add(content=..., container_tags=["edu"])
          ├── 更新 sync_state.json：添加 hash a1b2c3d4
          └── 输出: "[完成] 总计 N 条记忆已管理"

T+1s  ─ [Step 2] obsidian_sync.py ⏸️ DISABLED，跳过

T+2s  ─ [Step 3] collect_architecture.py 运行
          ├── 检查是否有新的架构决策记忆
          ├── 无新架构数据 → 快速退出
          └── 输出: "无新架构更新"

T+3s  ─ [Step 4] relay_to_obsidian.py 运行
          ├── 扫描 relay/shared/results/ → 无新文件
          ├── 扫描 relay/side/results/ → 无新文件
          └── 输出: "无新内容"

T+4s  ─ molin-sync-all.sh 完成
          └── Cron Job last_status = ok
              last_run_at = 2026-05-19T18:00:36

T+10s ─ iCloud 自动同步
          └── 产出/元瑶｜memory_a1b2c3d4.md → 同步到 iCloud 所有设备

T+30s ─ Obsidian 索引更新
          └── 新文件出现在 Obsidian 文件列表中，全文索引立即可搜索

T+5min ─ 其他 Agent（如墨码开发）通过 Supermemory API 查询相关记忆
          └── Supermemory 语义检索返回该条记忆（命中）
```

---

## 错误处理

### 各脚本失败场景

| 脚本 | 故障模式 | 影响 | 自动恢复 | 人工介入 |
|------|---------|------|---------|---------|
| `sync_memory.py` | Supermemory API 超时 | Obsidian写入成功，Supermemory缺同步 | 下次整点重试时自动补同步 | 如果连续3次失败，飞书告警 |
| `sync_memory.py` | 记忆文件不存在 | 跳过该Agent，不影响其他Agent | 下次整点自动再试 | — |
| `sync_memory.py` | Obsidian写入失败（磁盘满/权限） | Supermemory写入成功，本地缺文件 | 下次整点重试 | 紧急：检查磁盘+权限 |
| `relay_to_obsidian.py` | relay 目录不存在 | 跳过，输出"无新内容" | 下次自动 | — |
| `relay_to_obsidian.py` | tracker.json 损坏（JSON解析失败） | 从空tracker重新开始，可能导致重复写入 | 自动重建空tracker | — |
| `collect_architecture.py` | 架构记忆文件损坏 | 跳过该次采集 | 下次自动 | 检查架构记忆文件 |
| `molin-sync-all.sh` | 任一步骤失败（set -e） | 管道中断，后续步骤不执行 | 下次整点整管道重试 | Cron Job 显示 last_status=error |

### 重试策略

| 级别 | 策略 | 适用范围 |
|------|------|---------|
| 脚本内重试 | 无重试（脚本级出错立即退出） | `sync_memory.py`、`relay_to_obsidian.py` |
| 管道级重试 | 下次整点整管道重新执行 | `molin-sync-all.sh`（Cron调度保证） |
| 人工重试 | `cron job run 210cba244f36` 或直接执行脚本 | 所有 |

### 告警机制

| 场景 | 告警级别 | 通道 | 触发条件 |
|------|---------|------|---------|
| Cron Job 连续1次失败 | T4（通知） | 飞书消息 | last_status = error |
| Cron Job 连续3次失败 | T3（告警） | 飞书告警 | 3次连续的 error |
| Supermemory API 不可用 | T4（通知） | 脚本输出日志 | sync_to_supermemory 返回 0 |
| 磁盘空间 < 500MB | T2（紧急） | 飞书 + 系统通知 | 系统diskutil检测 |
| iCloud 同步冲突 | T4（通知） | 脚本日志 | 文件名被追加冲突后缀 |

---

## 同步数据

### 运行频率统计（当前状态）

| 指标 | 数值 | 数据来源 |
|------|------|---------|
| 记忆同步 Job 执行次数 | 101次 | Cron Job repeat.completed |
| 当前启用状态 | ⏸️ 已暂停（v3.0迁移） | Cron Job enabled=false |
| 最后运行状态 | ok | last_status |
| 最后运行时间 | 2026-05-19 15:00:36 | last_run_at |
| 平均同步耗时 | <5秒（脚本执行） | 估算（Cron无精确计时） |
| 成功率（历史） | ~95% | 101次中少数error |
| Relay同步跟踪记录 | ~15次 | sync_log.txt |

### 观察到的历史问题

| 日期 | 问题 | 影响 | 根因 | 解决 |
|------|------|------|------|------|
| 2026-05-18 | 同步脚本未执行 | Job paused | 系统迁移时手动暂停 | 等待恢复 |
| 2026-05-16 | 重复同步 | 文件多份 | sync_state.json 未正确持久化 | 修复 JSON 写入 |
| 2026-05-15 | Supermemory API key 缺失 | Supermemory通道无同步 | $HOME 重定向污染环境变量 | 增加 .zprofile fallback |
| 2026-05-15 | 输出路径到 02_Agent_Outputs/ | 文件不可检索 | 脚本硬编码废弃路径 | 更新为四层目录体系 |

---

## 风险登记

| 风险 | 概率 | 影响 | 等级 | 检测手段 | 兜底方案 |
|------|------|------|------|---------|---------|
| **Vault磁盘满** | 低 → 中 | 所有Obsidian写入失败 | **P1** | 系统diskutil告警（<1GB时触发） | 自动清理~/.hermes/cache和~/.hermes/logs；紧急：移至外部磁盘 |
| **iCloud同步冲突** | 中 | 同一文件在多设备同时修改，产生冲突副本 | **P2** | iCloud同步完成后检查 `.md` 冲突文件后缀 | `output_writer.py` 幂等检查避免并发写入；冲突文件手动合并 |
| **Supermemory API 不可用** | 低 | 语义检索通道中断 | **P2** | 脚本内 try/except 捕获 | 降级为仅 Obsidian 写入，下次重试自动补同步 |
| **Cron Job 静默暂停** | 中 | 记忆不更新 | **P1** | 双保险：Cron last_status + 飞书每日健康检查（待实现） | 手动 `cron job resume 210cba244f36`；加飞线 ping 检查 |
| **sync_state.json 损坏** | 低 | 重复写入，文件数膨胀 | **P3** | JSON解析失败时自动重建 | 重建为空tracker，容忍少量重复 |
| **$HOME 被 Hermes 重定向** | 中 | 脚本读取错误的 $HOME 路径 | **P2** | 脚本硬编码 `/Users/laomo` 绕过 | 所有路径已硬编码绝对路径 |
| **新 Agent 未配置 sync_memory** | 中 | 新Agent产出未写入任一通道 | **P2** | 每周合规检查扫描遗漏Agent | 自动生成 sync_memory 配置模板 |
| **Obsidian vault 结构升级** | 中 | 脚本写入了废弃路径 | **P1** | 废弃路径扫描（周检） | 脚本路径更新 + 文件迁移 |

---

## 写入规范

所有写入遵循 [[系统层/架构演进/内容规范]]，强制包含：

1. **YAML frontmatter** — 必须包含 `title`, `status`, `last_updated`, `agent_sync`
2. **TL;DR Blockquote** — 写在正文开头，3句话以内概括核心结论
3. **结构化正文** — 按金字塔原理组织（H2→H3），使用 MECE 分类
4. **Changelog** — 每次修改记录在文末 PDCA 表中

不合规内容被自动拒绝并记录警告日志到 Hermes logs。

### 文件命名规范

参见 [[系统层/架构演进/Agent产出写入标准#一、命名规范设计决策记录]]，所有文件使用 `业务线｜内容.md` 格式。

---

## 交叉引用

| 相关文档 | 路径 | 关系 |
|---------|------|------|
| 定时任务管理标准 | [[系统层/部署与环境/定时任务管理标准]] | 本标准的 Cron Job `210cba244f36` 在此文档中归类为"流程类"；包含全部7个Cron Job的完整清单 |
| 内容规范 | [[系统层/架构演进/内容规范]] | 所有写入 Obsidian 的文档必须遵循此规范的6个框架（金字塔、MECE、SCQA、5W1H×SMART、DIKW、PDCA） |
| Agent产出写入标准 | [[系统层/架构演进/Agent产出写入标准]] | 定义四层目录体系、`业务线｜内容.md` 命名规则、废弃路径列表；sync_memory.py 等4脚本的产出路由遵从该标准的映射表 |
| Vault合规周检 | [[系统层/架构演进/Agent产出写入标准#七、健康检查体系]] | 每周合规检查验证本工作流的执行情况 |
| Git备份 | [[系统层/部署与环境/定时任务管理标准#一、流程类]] | 每日02:00的Git备份确保Vault的版本历史可追溯 |

---

## Changelog

| 日期 | 版本 | 修改内容 | 修改原因 |
|------|------|---------|---------|
| 2026-05-19 | v2.0 | 1. 新增SCQA开篇（为什么双通道）<br>2. 新增决策记录表（双通道 vs Notion/单向量库/Git-only）<br>3. 4个同步脚本各增加完整命令签名、参数、读写目录、依赖<br>4. 新增Crontab配置表（全量Job清单 + 管道流程图）<br>5. 新增目录映射表（脚本→Vault目录→Supermemory容器）<br>6. 新增完整同步周期场景（飞书→4脚本→Vault 全链路追踪）<br>7. 新增错误处理表（故障模式×7 + 重试策略 + 告警机制）<br>8. 新增同步数据（运行频次、历史问题）<br>9. 新增风险登记表（8项风险 + 兜底方案）<br>10. 新增交叉引用表（定时任务/内容规范/Agent写入标准）<br>11. 补充写入规范小节，链接到关联文档 | 系统层架构演进专项升级：补齐SCQA框架、决策记录、脚本规范、全场景追踪、风险兜底，使工作流标准达到可执行、可审计、可故障排查水平 |
| 2026-05-19 | v1.0 | 初始版本：双通道架构描述 + 4脚本清单 + 触发模式 + 写入规范 | 创建Obsidian工作流标准 |
