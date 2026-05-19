---
name: gatekeeper-sop
description: 全流量门禁 Agent — 所有对外输出必须过的 QA + Compliance 合规检查岗
category: molin-org
version: 1.1.0
tags: [sop, qa, compliance, gatekeeper, governance, quality]
trigger: 所有 Agent 完成执行 SOP 后、对外发布/分发前，必须加载此技能进行终检
---

# Gatekeeper SOP — 全流量合规门禁

## 定位

```
所有 Agent 输出
    ↓
Gatekeeper 终检 ← 这是最后一道防线
    ↓
通过 ≥ 85  → 对外输出/发布
70-84      → 自动修正后输出
60-69      → ⚠️ 人工审批
< 60       → 🚫 拦截 + 打入待人工审核
```

## 核心职责

Gatekeeper 不是独立运行的 Agent，而是**每个 Agent 输出前的强制检查节点**。

它由三部分构成：
1. **质检检查**（QA Check）— 对照各 Agent 的 QA SOP 逐项评分
2. **合规检查**（Compliance Check）— 全流量统一规则
3. **阻断决策**（Block Decision）— 决定是否放行

---

## 一、质检检查（QA Check）

### 通用检查矩阵（所有 Agent 通用）

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 数据真实性 | 25% | 数据可验证？来源明确？有无幻觉？ |
| 合规无风险 | 25% | 敏感词？政策红线？竞品贬低？虚假宣传？ |
| 逻辑完整性 | 15% | 上下文连贯？结论有支撑？无逻辑跳跃？ |
| 可操作性 | 15% | 接收方能否直接使用？需要额外解读吗？ |
| 格式规范性 | 10% | 是否符合输出模板约定？ |
| 时效性 | 10% | 信息是否过时？发布时间是否合理？ |

### 评分规则

```
总分 = Σ(维度得分 × 权重)

否决条件（任一触发直接 0 分）：
1. 涉及政治敏感/成人/暴力/歧视内容
2. 承诺无法兑现的服务或结果
3. 冒充他人或伪造授权
4. 包含未公开的客户/用户隐私数据
5. 包含可执行的恶意代码或指令
```

---

## 二、合规检查（Compliance Check）

### 平台合规规则

#### 小红书
- ❌ 禁止：医疗承诺、金融承诺、隐藏广告（软广未标注）
- ⚠️ 限制：绝对化用语、竞品对比、引流到微信
- ✅ 要求：广告标注、话题标签、原创声明

#### 抖音/视频号
- ❌ 禁止：虚假宣传、诱导互动（必须点赞才能看）
- ⚠️ 限制：引流到第三方平台
- ✅ 要求：内容真实、未成年保护

#### 公众号/SEO
- ❌ 禁止：抄袭洗稿、标题党
- ⚠️ 限制：医疗/金融等特管行业资质
- ✅ 要求：来源标注、引用规范

#### LINE 推播
- ❌ 禁止：未授权商业推广、频繁推送
- ⚠️ 限制：用户隐私数据使用
- ✅ 要求：退订链接、发送频率控制

### 品牌合规规则

- 品牌名称必须与 `company.toml` 一致
- Logo/视觉必须使用已注册版本
- 不得使用竞品商标做关键词堆砌
- 对外口径必须与 CEO 确认过的策略一致

---

## 三、证据质量门禁（吸收自 agency-agents Reality Checker）

> 源：[Reality Checker](https://github.com/msitarzewski/agency-agents/blob/main/testing/testing-reality-checker.md) · MIT License · 吸收日期：2026-05-17

### 核心哲学：「默认拒绝」原则

```
默认状态 = "需要修改"（NEEDS WORK）
只有压倒性证据才能翻转为 "生产就绪"（PRODUCTION READY）
```

三条铁律：
1. **停止幻想批准** — 不再有「基本网站得了 98/100」，拒绝过度乐观
2. **要求压倒性证据** — 每个系统声明必须有可视化证明
3. **诚实反馈驱动更好结果** — C+/B- 评分是正常的，首批实现通常需要 2-3 轮修改

### 证据要求矩阵

| 声明类型 | 最低证据要求 |
|---------|------------|
| 功能完成 | 端到端截图/录屏 |
| 性能达标 | 基准测试数据 |
| 安全合规 | 扫描报告 |
| 跨平台兼容 | 多设备截图矩阵 |
| 数据准确 | 来源验证 + 交叉比对 |

### 强制检查步骤

```
Step 1: 验证声明（Reality Check）
  • 声称的功能是否真正存在？
  • 交叉比对 QA 发现与代码实际
  • 全面用户旅程测试 + 截图证据

Step 2: 证据交叉验证
  • QA 报告 vs 自动化截图
  • 测试数据 vs 声明数据
  • 不一致 → 标记「证据矛盾」，退回

Step 3: 端到端系统验证
  • 完整用户旅程（from 入口 to 目标完成）
  • 多设备验证（desktop/tabet/mobile）
  • 交互流程完整性检查
```

### 评级标尺

| 评级 | 含义 | 门禁动作 |
|------|------|---------|
| A+ | 压倒性证据，无缺陷 | ✅ 直接放行 |
| A/A- | 高质量，微小瑕疵 | ✅ 放行 + 记录改进项 |
| B+/B | 达标，有改进空间 | 🔄 标注改进项后放行 |
| B-/C+ | 勉强可用 | ⚠️ 退回修改 1 轮 |
| C 及以下 | 不可用 | 🚫 阻断 + 锁定 |

### 否决证据链

当阻断发生时，必须输出完整证据链：

```json
{
  "status": "NEEDS WORK",
  "rating": "C",
  "blocked_items": [
    {"claim": "响应式设计完成", "evidence": "mobile截图显示布局断裂"},
    {"claim": "暗色模式完成", "evidence": "grep未找到暗色模式CSS变量"}
  ],
  "required_fixes": [
    "修复 mobile 布局断裂（具体元素：header/hero section）",
    "实现暗色模式 CSS 变量并验证"
  ],
  "retry_allowed": true,
  "max_retry": 3,
  "escalation": null
}
```

---

## 四、阻断决策（Block Decision）

### 决策树

```
输入内容
  ↓
触发否决条件？───是──→ 🚫 直接阻断，写入 relay/gatekeeper_blocked/
  ↓ 否
QA评分 ≥ 85？───是──→ ✅ 放行
  ↓ 否
70 ≤ QA < 85？───是──→ 🔄 自动修正后放行
  ↓ 否
60 ≤ QA < 70？───是──→ ⚠️ L2 审批：通知 Founder 确认
  ↓ 否
QA < 60？────────→ 🚫 拦截 + 飞书告警 + 记录原因到 relay/gatekeeper_blocked/
```

### 拦截记录格式

gatekeeper 阻断时，确保目录存在：
```bash
mkdir -p /Users/laomo/relay/gatekeeper_blocked/
```

拦截记录写入 `relay/gatekeeper_blocked/{ticket_id}.json`：

```json
{
  "timestamp": "2026-05-16T22:00:00+08:00",
  "source_agent": "content_writer",
  "content_type": "xiaohongshu_post",
  "title": "xxx",
  "qa_score": 45,
  "block_reason": "触发否决条件：敏感话题",
  "action": "已拦截，通知Founder",
  "ticket_id": "GK-20260516-001"
}
```

---

## 四、与现有系统的集成

### 集成点 1：Cron 飞轮出口

在每日分发 Cron 的最后一步前，插入 Gatekeeper 检查：

```
情报采集 → 内容生产 → QA自检 → Gatekeeper终检 → 平台分发
                                          ↑
                                    这是新插入的节点
```

### 集成点 2：Content SOP 调用

在 `content-sop-pack` 的 QA SOP 自检后，最终输出前：
1. 先自检（content-sop-pack QA）
2. 再 Gatekeeper 终检（gatekeeper-sop）
3. 通过后才能进入分发 Cron

### 集成点 6：22:00 复盘终检

22:00 内容复盘 Cron（反馈层）在产出前必须过 Gatekeeper：
```
① 读取 KPI 数据
② QA 趋势分析
③ 3 天连续下降检测
④ 异常审计
⑤ Gatekeeper 终检 ← 本集成点
⑥ 写入复盘笔记 + 复盘元数据
```

Gatekeeper 在此检查：
- ✅ 复盘数据的真实性（数据来源可验证，非 AI 幻觉）
- ✅ 异常记录的完整性（所有触发的异常有无遗漏）
- ✅ 建议的可操作性（明日优化建议具体可执行）
- ✅ 格式规范性（复盘笔记和元数据是否符合模板）
- ✅ 时效性（复盘时间为当天，数据为当天数据）

### 集成点 4：Vault 结构合规

Gatekeeper 的检查范围延伸到 vault 目录结构。`scripts/vault_health_check.py` 每日自动运行，检测：

- 顶层目录是否在允许列表（决策/知识/流程/成果/报告/配置/产出/学习档案）
- 根级是否有非 .md 文件（Makefile/README 等代码文件）
- 是否出现遗留目录（Agents/Daily/System/env 等）
- 是否出现同名文件冲突
- Agent 输出是否在正确的 `产出/业务线｜{主题}.md` 下（平坦结构，无子目录）

健康检查结果在每日 22:00 复盘时引用。不合格项标记为 gatekeeper 拦截。

### 集成点 5：记忆四层架构

所有 Agent 输出写入前必须经过记忆分层检查：

- L1 工作记忆 → 不进 Obsidian（只在飞书对话/Session）
- L2 情节记忆 → Supermemory（30天未调用→蒸馏到 L3）
- L3 语义记忆 → Obsidian `产出/`（平坦，永久）
- L4 程序记忆 → skill 文件（版本化管理）

由 `molib/memory/output_writer.py` 强制执行。vault 结构合规检查详见 `references/vault-compliance.md`。

### 集成点 3：Escalation 联动

Gatekeeper 拦截的内容自动触发 Escalation：
- QA < 60：记录到 `relay/gatekeeper_blocked/` + 飞书告警
- 否决条件触发：紧急飞书告警 + 锁定相关 Agent

---

## 五、参考

- QA 评分细化规则：各 Agent 专属 QA SOP
- 品牌合规详情：`supermemory_search("墨麟品牌合规")`
- 平台最新规则：调用平台对应的 skill
- Agent 模板：`skill_view('agent-sop-template')`
- 治理级别：`config/governance.yaml`
- Vault 结构合规：`references/vault-compliance.md`（目录规则 + 健康检查）
