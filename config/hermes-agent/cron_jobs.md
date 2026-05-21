# 墨麟 OS v7.0 · Cron 作业全量排班表

> 最后更新: 2026-05-21
> 架构: 六司三十四将 v7.0
> 共计: 19 个活跃作业 (当前全部暂停，待创始人确认后启用)

---

## 修复记录

| 日期 | 修复项 | 详情 |
|------|--------|------|
| 2026-05-21 | 🔴 P0-1: KPI看板路径 | `generate_dashboard.py daily` → `generate_kpi_dashboard.sh` (wrapper) |
| 2026-05-21 | 🔴 P0-2: 记忆同步脚本 | 重写 `molin-sync-all.sh`，剔除旧 `collect_architecture.py`，改用纯本地 ChromaDB 语义合并 |
| 2026-05-21 | 🔴 P1-1: 垂直学习扫描 | 重写 prompt，移除 exfil_curl_url 触发词，限缩为本地 Obsidian + skills |
| 2026-05-21 | 🔴 P1-2: AutoDream精读 | 重写 prompt，限缩写入作用域至 skills/，全程离线 |
| 2026-05-21 | 🔴 P1-3: 记忆蒸馏 | 重写 prompt，配置离线沙箱安全策略，仅用本地工具 |

---

## 六司作业分布

| 司 | 负责人 Worker | 管辖作业数 | 作业 ID |
|----|-------------|----------|---------|
| 💀 玄骨 (中枢) | 墨维/墨算/墨安/墨码/墨梦 | 10 | #1 #2 #3 #6 #9 #10 #11 #12 #14 #16 |
| 🌙 银月 (内容) | 墨笔/墨图/墨剪/墨星 | 2 | #13 #15 |
| 🔮 紫灵 (情报) | 墨研/墨数/墨嗅 | 2 | #4 #5 #8 |
| ❄️ 梅凝 (跨境) | 墨译/墨媒 | 1 | #7 |
| 🌸 元瑶 (增长) | 墨导 | 1 | #17 |
| 集团主脑 | — | 2 | #10 #17 #19 |
| 🍃 宋玉 (商业) | 墨商 | 1 | #18 #19 |

---

## 作业清单

| # | job_id | 名称与自动化行为 | 调度 | 类型 | 负责司 | Skills / 脚本 | 状态 |
|---|--------|------------------|------|------|--------|--------------|------|
| 1 | `210cba244f36` | **全局记忆同步** — 每小时盘点 L2/L3 增量，ChromaDB 语义向量增量合并 | `0 * * * *` | Script | 💀玄骨 (墨维) | `molin-sync-all.sh` | ⏸ 暂停 |
| 2 | `5cd81602c531` | **本地分布式 Git 备份** — 代码与 Obsidian 全量异地容灾 | `0 2 * * *` | Script | 💀玄骨 (墨安/墨维) | `git-backup.sh` | ⏸ 暂停 |
| 3 | `712178799998` | **系统级安全主动审计** — 例行扫描内核权限与 Token 暴露 | `0 3 * * 1` | Agent | 💀玄骨 (墨安/墨律) | `security-sop-pack` | ⏸ 暂停 |
| 4 | `ef1b8c26ce5c` | **五大领域知识库垂直学习** — 提取全周沉淀，精炼商业认知，仅本地闭环 | `0 6 * * 1` | Agent | 🔮紫灵 (墨研)→💀玄骨 | `vertical-learning-sop` `obsidian` | ⏸ 暂停 |
| 5 | `9dd66fafeb6d` | **【飞轮①】情报银行：arXiv 扫描** — 抓取最新 AI 论文并生成简报 | `0 7 * * *` | Script | 🔮紫灵 (墨研/墨数) | `daily_arxiv_scan.sh` | ⏸ 暂停 |
| 6 | `e4a86b802135` | **AutoDream 认知内化与技能自进化** — 根据复盘日志自动优化系统 Skills | `0 7 * * 1` | Agent | 💀玄骨 (墨梦/墨算) | `vertical-learning-sop` `obsidian` | ⏸ 暂停 |
| 7 | `a169caa8c9ac` | **海外前沿技术动态学习** — 定向追踪全球开源生态增量 | `0 8 * * *` | Agent | ❄️梅凝 (墨译/墨媒) | prompt-based | ⏸ 暂停 |
| 8 | `d1e92fbc6c8d` | **全网商业变现/供应链价格监控** — 捕捉跨境商品及 SaaS 服务汇率波动 | `30 9 * * *` | Script | 🔮紫灵 (墨嗅)→🍃宋玉 | `daily_side_price_monitor.sh` | ⏸ 暂停 |
| 9 | `61cc88accaa9` | **知识库合规与死链周检** — 全自动清理 Obsidian 孤立节点 | `0 9 * * 1` | 默认 | 💀玄骨 (墨维) | 作用域：`vault/` | ⏸ 暂停 |
| 10 | `49961528a542` | **主脑级周计划动态生成** — 依据上周 KPI 拆解下周各司任务 | `30 9 * * 1` | Agent | 集团主脑→💀玄骨 (墨算) | `obsidian` `kpi-tracker` | ⏸ 暂停 |
| 11 | `bad81fa1d323` | **高频跨线网关轮询** — 调度 6 个飞书 Bot 间的异步协作通讯 | `*/15 * * * *` | Script | 💀玄骨 (墨码) | `cross_request_worker.py` | ⏸ 暂停 |
| 12 | `614f6c663f11` | **全渠道业务 KPI 自动化采集** — 抽取各平台播放量/留存率/营收数据 | `50 21 * * *` | Agent | 💀玄骨 (墨算) | `kpi-tracker` `data-sop-pack` | ⏸ 暂停 |
| 13 | `5c7c2cfe6103` | **多矩阵全媒体周度增长复盘** — 剖析本周爆款文案转化特征 | `0 21 * * 0` | Agent | 🌙银月 (墨星)→🌸元瑶 | `kpi-tracker` `content-sop-growth` | ⏸ 暂停 |
| 14 | `b896895087fb` | **深度记忆蒸馏与 L3 资产质量门控** — 高价值对话固化为永久 SOP | `30 21 * * 0` | Agent | 💀玄骨 (墨算/墨维) | `obsidian` `mempalace` | ⏸ 暂停 |
| 15 | `05ee5848f9f4` | **【飞轮②】内容工厂：全媒体日更** — 承接早间情报，生成多媒体资产 | `0 22 * * *` | Agent | 🌙银月 (墨笔/墨图/墨剪) | `content-sop-pack` `gatekeeper-sop` | ⏸ 暂停 |
| 16 | `e25fcf710cf0` | **集团多维动态 KPI 看板渲染** — 更新本地及前端可视化仪表盘 | `10 22 * * *` | Script | 💀玄骨 (墨算) | `generate_kpi_dashboard.sh` | ⏸ 暂停 |
| 17 | `ca23aefea523` | **【飞轮③】增长引擎：跨平台发售规划** — 复盘今日流量，编排明日投放 | `30 22 * * *` | Agent | 集团主脑→🌸元瑶 (墨导) | `kpi-tracker` `obsidian` | ⏸ 暂停 |
| 18 | `55a2385d955a` | **集团财务日报与合规审计** — 盘点各营收子公司今日流水与 ROI | `0 23 * * *` | Agent | 🍃宋玉 (墨商)→💀玄骨 | `finance-sop-pack` `kpi-tracker` | ⏸ 暂停 |
| 19 | `a22276b31c18` | **战略级月度商业发售规划** — 每月 1 号自动执行，指引全局营收方向 | `0 9 1 * *` | Agent | 集团主脑→🍃宋玉 (墨商) | `kpi-tracker` `finance-sop-pack` | ⏸ 暂停 |

---

## 飞轮管线（内容自动化三棒接力）

```
08:00 情报银行 ──→ 09:20 内容工厂 ──→ 10:45 增长引擎
   ↓                   ↓                   ↓
intelligencemorning  contentmorning     growthmorning
     .json               .json              .json
```

| 棒次 | 时间 | 负责司 | Worker | 说明 |
|------|------|--------|--------|------|
| 第一棒 | 08:00 | 🔮紫灵 | 墨研/墨数 | 情报银行：arXiv 扫描 + 舆情采集 → `relay/intelligencemorning.json` |
| 第二棒 | 09:20 | 🌙银月 | 墨笔/墨图/墨剪 | 内容工厂：消费上游 → 生成多平台内容 → `relay/contentmorning.json` |
| 第三棒 | 10:45 | 🌸元瑶 | 墨导/墨增 | 增长引擎：SEO 优化 + 审计 + 追踪 → `relay/growthmorning.json` |

飞轮接力规则：每棒必须检查上游文件存在且 < 90 分钟，否则发 T4 飞书告警。

## 飞轮语义检索 (v7.0 新增)

Cron Job 不再硬编码技能名，改为通过 `scripts/flywheel_skills.py` 读取 `config/domains/*.yaml` 中的飞轮配置，执行语义检索动态获取技能列表。

**改造前** (硬编码):
```yaml
skills: [content-sop-pack, gatekeeper-sop, kpi-tracker]
```

**改造后** (语义检索):
```bash
python3 scripts/flywheel_skills.py yinyue content_factory
→ 自动检索 domain yinyue 中与 "生成小红书公众号短视频内容" 最相关的 Top-3 技能
```

各飞轮 → Domain YAML 映射:
| 飞轮 | Domain YAML | 语义意图 |
|------|------------|---------|
| 情报银行 | `ziling_intelligence.yaml` | arXiv 论文抓取 AI前沿技术研究 |
| 内容工厂 | `yinyue_media.yaml` | 生成小红书公众号短视频内容 |
| 增长引擎 | `yuanyao_edu_growth.yaml` | 全媒体增长复盘 AB测试 |
| 财务日报 | `songyu_innovation.yaml` | 财务日报 ROI审计 |
| 记忆同步 | `xuanhu_infrastructure.yaml` | 记忆同步 ChromaDB |
| KPI 采集 | `xuanhu_infrastructure.yaml` | KPI采集 数据看板 |

---

## 按频率分布

| 频率 | 任务 |
|------|------|
| 每 15 分钟 | #11 跨线请求轮询 |
| 每小时 | #1 记忆同步 |
| 每日 | #2 Git备份 / #5 arXiv / #7 梅凝学习 / #8 价格监控 / #12 KPI采集 / #15 内容复盘 / #16 KPI看板 / #18 财务日报 |
| 每日(飞轮联动) | #17 增长引擎(22:30) |
| 每周一 | #3 安全审计 / #4 垂直学习 / #6 AutoDream / #9 Vault合规 / #10 周计划 |
| 每周日 | #13 增长复盘 / #14 记忆蒸馏 |
| 每月 1 号 | #19 月度规划 |

---

## 部署指南

所有作业当前处于暂停状态（`state: paused`），待创始人确认后启用。

启用命令：
```bash
hermes cron resume <job_id>   # 恢复单个作业
hermes cron run <job_id>      # 手动触发一次验证
```

批量启用（确认后执行）：
```bash
for id in 210cba244f36 5cd81602c531 712178799998 ef1b8c26ce5c 9dd66fafeb6d \
  e4a86b802135 a169caa8c9ac d1e92fbc6c8d 61cc88accaa9 49961528a542 \
  bad81fa1d323 614f6c663f11 5c7c2cfe6103 b896895087fb 05ee5848f9f4 \
  e25fcf710cf0 ca23aefea523 55a2385d955a a22276b31c18; do
  hermes cron resume $id
done
```

⚠️ **重要**：批量启用前确保所有修复已验证通过。
