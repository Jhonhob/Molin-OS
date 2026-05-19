---
title: 内容情报管道标准作业程序
status: 活跃
version: 2.0
last_updated: 2026-05-19
agent_sync: true
frameworks_applied:
  - MECE
  - PDCA
  - SCQA
  - RRF
---

# 内容情报管道标准作业程序

## SCQA — 为什么情报管道是内容飞轮的第一步

**情境 (Situation)：**
墨麟每天产出 5-8 篇内容，横跨小红书、抖音、公众号、B站四个平台。内容团队规模有限，需要每篇内容都产生最大杠杆效应。

**冲突 (Complication)：**
传统流程是"先写再猜"——凭经验选题→花 2-3 小时创作→发布后等待数据验证。结果是：选题命中率约 30%，资源被低效选题消耗，热门机会窗口经常错过。选题决策依赖个人直觉而非结构化数据，且跨平台热门趋势无法在落笔前系统性获取。

**问题 (Question)：**
如何在落笔之前，用结构化数据替代直觉猜测，把选题命中率从 30% 提升到 70%+？

**答案 (Answer)：**
内容情报管道——每天 08:00 从 12+ 数据源并行拉取趋势信号，经归一化→RRF 融合排序→竞品对标→选题推荐后，生成结构化情报数据包，作为内容飞轮第一棒交付下游 Worker。**先知道什么在赢，再决定怎么写。**

---

## 决策记录

### 为什么是 12 个数据源？

MECE 框架下，内容热词信号按**平台生态 × 内容形态**切分为四象限：

| 象限 | 代表平台 | 覆盖源 |
|---|---|---|
| 短图文 + UGC | 小红书、微信话题 | 小红书热词、微信话题 |
| 短视频 + 直播 | 抖音、B站 | 抖音热词、B站热门 |
| 综合资讯 + 搜索 | 微博、百度、知乎 | 微博热搜、百度指数、知乎热榜 |
| 行业 + 竞品 | RSS、竞品账号 | 行业 RSS、竞品爆款 |

12 个源覆盖四象限，每象限 2-4 个源，保证跨平台覆盖同时避免单点依赖。内部测试显示：少于 8 个源时跨平台热点漏检率 > 40%；12 个源可将漏检率压至 < 10%。

### 被拒绝 / 推迟的数据源

| 数据源 | 拒绝原因 | 替代方案 |
|---|---|---|
| 快手热词 | 目标受众重合度 > 70%（与抖音），ROC 曲线收益 < 5% | 暂不接入，每周人工抽检 |
| 豆瓣小组热帖 | 反爬严格，稳定性 < 60%，封 IP 风险高 | 通过 RSS 订阅特定小组 |
| 微信搜一搜热词 | 腾讯限制 API 配额，每日仅 100 次 | 延迟到 v2.1 评估腾讯云合作 |
| TikTok 全球趋势 | 当前只做中文内容，全球化阶段再引入 | 架构预留 adapter 接口 |

---

## 五步流程（扩展版）

### S1 热词收集

**目标：** 每天 08:00-08:05 从 12+ 数据源并行拉取原始热词数据，各 Adapter 独立运行、互不干扰。

#### 子步骤

| # | 动作 | 执行者 | 超时阈值 |
|---|---|---|---|
| 1.1 | Adapter 初始化：加载源配置（凭证、限流参数、endpoint） | cron Agent | — |
| 1.2 | 并行分发：12 个 goroutine 独立执行 Fetch() | cron Agent | 180s |
| 1.3 | 降频重试：429/503 时指数退避 ×3，仍失败则标记 degraded | Adapter 内置 | 60s |
| 1.4 | 原始数据暂存：写入 /tmp/raw/{source}_{timestamp}.json | cron Agent | — |
| 1.5 | 收集统计：返回 per-source {fetched, failed, latency_ms, degraded} | cron Agent | — |

#### 决策点

- **某源持续失败 3 天 →** 标记为 DEAD，触发告警，自动切换至备用源（见数据源配置表 fallback 列）
- **某源返回空数据（空列表或全 null）→** 视为 degraded，重试一次；仍空则跳过，不阻塞下游
- **整体失败数 > 3 个源 →** pipeline 降级为部分结果模式，情报输出标注 limited 状态

#### 成功标准

- ✅ 单源 fetch 延迟 < 30s（95 分位）
- ✅ 总 pipeline fetch 阶段 < 6min
- ✅ 至少 10/12 源成功返回（含 degraded 视为成功）

#### 错误处理

| 错误类型 | 行为 | 日志级别 |
|---|---|---|
| 网络超时 | 自动重试 ×3，指数退避 (1s, 3s, 9s) | WARN |
| 认证失败 401 | 立即失败，不重试，触发凭证轮换 | ERROR |
| 限流 429 | 读取 Retry-After 头，等待后重试 | INFO |
| 数据格式异常 | 丢弃该条，记录 raw_data 用于事后分析 | WARN |
| 源完全宕机 | 切换 fallback 源（见配置表），标记 degraded | ERROR |

---

### S2 数据处理

**目标：** 将原始非结构化热词数据归一化为统一 schema，经 RRF 融合排序后输出结构化情报。

#### 子步骤

| # | 动作 | 输入 | 输出 |
|---|---|---|---|
| 2.1 | 文本清洗：去 HTML 标签、统一全角/半角、去除 emoji/特殊符号（保留关键词 emoji） | raw_data | cleaned_text |
| 2.2 | URL 归一化：去除 tracking params、统一协议 https、去除尾部斜杠 | raw_url | normalized_url |
| 2.3 | 互动率计算：interaction_rate = (likes + comments + shares) / followers | raw_counts | rate:float |
| 2.4 | 跨源 RRF 融合排序（见第7节 RRF 公式） | per-source ranked lists | fused_rankings |
| 2.5 | 热点聚类：文本相似度 > 0.75 的条目合并为同一事件，保留最早源 + 最高分 | fused list | clusters |

#### 决策点

- **RRF k 值选择：** 默认 k=60。短期热点（24h）用 k=30 提高召回；长期趋势（7d）用 k=100 提高精度
- **聚类去重阈值：** 0.75（基于 sentence-BERT 余弦相似度）。若某事件跨源出现 > 3 次，自动提升其权重 +20%

#### 成功标准

- ✅ 归一化覆盖率 > 99%（缺失值填充 UNKNOWN）
- ✅ RRF 排序延迟 < 2s（1,000 条目）
- ✅ 聚类时每个 cluster 至少含 1 条原文可追溯
- ✅ 无数据丢失（上游 verified count == 下游 document count）

#### 错误处理

| 错误类型 | 行为 | 日志级别 |
|---|---|---|
| URL 解析失败 | 保留 raw_url，标记 normalized=false | WARN |
| 数值字段溢出 | 截断至 int64 范围 | WARN |
| 聚类 OOM | 回退至单机 SimHash + Jaccard | CRITICAL |
| 空输入（所有源 failed）| 中断 pipeline，输出 empty 状态 | CRITICAL |

---

### S3 竞品分析

**目标：** 对标账号最新内容分析，识别爆款模式、互动优势区间、竞品策略变化。

#### 子步骤

| # | 动作 | 定时 | 数据量 |
|---|---|---|---|
| 3.1 | 对标账号最新内容拉取（最近 7 天） | 每源 30s | ~20 条/账号 |
| 3.2 | 互动数据对比：per-content 对比 my_baseline vs competitor_baseline | 5s | — |
| 3.3 | 打法识别：标题模式、封面风格、发布时间、热门标签 | 分布式对比 | — |
| 3.4 | 策略变化检测：较上周变化 > 15% 的维度标记 alert | 10s | — |

#### 决策点

- **竞品新账号发现：** 如果某账号连续 3 天在竞品分析中被引用（同话题），自动加入对标列表候选
- **竞品下线：** 某账号超过 30 天未更新 → 移至休眠列表，编号保留
- **我的品牌词在竞品内容中出现 →** 标记为 direct_competition，优先级提升

#### 成功标准

- ✅ 竞品列表覆盖率：对标账号数 ≥ 核心目标（初始 10 个，每季度 review）
- ✅ 策略变化检测：每周至少 1 条 actionable insight
- ✅ 竞品内容抓取延迟 < 60s（per account）

#### 错误处理

| 错误类型 | 行为 | 日志级别 |
|---|---|---|
| 竞品账号不存在 | 从活跃列表移除，触发告警 | WARN |
| 互动数据缺失（新内容 < 24h） | 标注 data_immature=true，跳过对比 | INFO |
| 反爬限制 | 降低频率 + 代理轮换，标记限流 | WARN |

---

### S4 选题推荐

**目标：** 基于 S2+S3 结果生成结构化选题建议，包含热度趋势、角度建议、平台适配和爆款概率预测。

#### 子步骤

| # | 动作 | 算法/模型 | 输出 |
|---|---|---|---|
| 4.1 | 热度趋势分析：计算每个 topic 的 d1/d3/d7 增速 | 线性回归 + 窗口滑动 | trend: rising/stable/declining |
| 4.2 | 角度建议生成：基于标题模式库 + 热点上下文，生成 5 个差异化角度 | LLM Prompt (gpt-4o-mini) | 5 angle strings |
| 4.3 | 平台适配建议：跨平台内容形态映射与适配策略 | 规则引擎 | per-platform recommendation |
| 4.4 | 爆款概率预测：基于历史特征 + 竞品基准回归 | XGBoost (ONNX runtime) | score: 0-100 |

#### 决策点

- **LLM 调用失败 →** 角度建议使用模板化 fallback（"分析热点 X 的 3 个层面"）
- **爆款预测分数 < 30 →** 不输出选题建议，仅标记为 monitored
- **某话题跨平台 > 5 个源 →** 自动提升为 P0 选题
- **同选题连续推荐 > 3 次 →** 需人工确认是否已跟过

#### 成功标准

- ✅ 趋势分析准确率 > 85%（对比下一日实际数据）
- ✅ 角度建议相关度评分（人工抽查）> 4.0/5.0
- ✅ 爆款预测 AUC > 0.75
- ✅ 每天至少输出 3 个 P0 选题 + 5 个 P1 选题

#### 错误处理

| 错误类型 | 行为 | 日志级别 |
|---|---|---|
| XGBoost 模型加载失败 | 回退至规则基线（加权平均 + 阈值） | CRITICAL |
| LLM timeout (>20s) | 使用模板化角度，记录失败用于 review | WARN |
| 无 trending topics 输入 | 跳过选题推荐，输出 empty | WARN |

---

### S5 输出持久化

**目标：** 将结构化情报数据写入永久存储，同时生成人工可读报告。

#### 子步骤

| # | 动作 | 目标路径 | 格式 |
|---|---|---|---|
| 5.1 | 写入 intelligence.json | `relay/media/intelligence.json` | JSON (schema 见第8节) |
| 5.2 | 生成 trending_topics.md | `relay/media/trending_topics.md` | Markdown + 表格 |
| 5.3 | 生成 competitor_analysis.md | `relay/media/competitor_analysis.md` | Markdown + 对比表格 |
| 5.4 | 写操作校验：checksum + schema validation | — | — |
| 5.5 | 通知下游 Worker（通过 relay channel） | — | message: pipeline_complete |

#### 成功标准

- ✅ 所有输出文件写入完成时间 < 08:30
- ✅ intelligence.json 通过 JSON schema 校验
- ✅ trending_topics.md 包含至少 8 个推荐选题
- ✅ competitor_analysis.md 覆盖至少 10 个对标账号

#### 错误处理

| 错误类型 | 行为 | 日志级别 |
|---|---|---|
| 磁盘空间不足 | 清理 oldest 3 天的 raw data, 重试 | CRITICAL |
| intelligence.json 损坏 | 回滚至上一有效版本, 触发告警 | CRITICAL |
| schema 校验失败 | 不覆盖文件, 保留上一版本, 记录 diff | ERROR |
| 写入 relay 失败 | 重试 ×3, 仍失败则降级为本地写入 | WARN |

---

## 数据源配置表

| 源名称 | 源类型 | 获取方式 | 限流 (次/分钟) | 认证方式 | Fallback 源 | 备注 |
|---|---|---|---|---|---|---|
| 小红书热词 | 平台热词 | 官方 API | 60 | API Key | 小红书搜索爬虫（降频） | 重点源，权重 1.2 |
| 抖音热词 | 平台热词 | 开放 API | 100 | Token | 抖音搜索 RSS | 权重 1.2 |
| 微博热搜 | 平台热搜 | RSS + API | 30 | Cookie (轮换) | 微博话题页爬虫 | 敏感词过滤 |
| 微信话题 | 生态热词 | 搜一搜 API | 20 | Token | 微信指数截图 OCR（降级） | 限频严格 |
| 知乎热榜 | 社区热榜 | 开放 API | 60 | 无 | 知乎首页爬虫 | 热榜+搜索双模式 |
| B站热门 | 视频社区 | 开放 API | 100 | 无 | B站精选页 RSS | 含弹幕密度指标 |
| 百度指数 | 搜索指数 | 官方 API (付费) | 10 | API Key + Secret | 百度搜索爬虫（降频） | 付费源，高精度 |
| 竞品爆款 A | 特定账号 | 账号 API | 30 | Auth Token | 页面爬虫 | 不可公开 |
| 竞品爆款 B | 特定账号 | 账号 API | 30 | Auth Token | 页面爬虫 | 不可公开 |
| 行业 RSS-A | 行业媒体 | RSS Feed | 不限 | 无 | 聚合站 API | 权重 0.6 |
| 行业 RSS-B | 行业媒体 | RSS Feed | 不限 | 无 | 聚合站 API | 权重 0.6 |
| 行业 RSS-C | 行业媒体 | RSS Feed | 不限 | 无 | 聚合站 API | 权重 0.6 |

> **凭证管理：** 所有 API Key / Token / Cookie 存储在 `.env` 文件中，不写入代码仓库。证书每 90 天轮换一次，过期前 7 天告警。

---

## JSON Schema — intelligence.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "IntelligencePipelineOutput",
  "type": "object",
  "required": [
    "pipeline_id",
    "timestamp",
    "status",
    "sources_summary",
    "trending_topics",
    "competitor_insights",
    "topic_recommendations"
  ],
  "properties": {
    "pipeline_id": { "type": "string", "pattern": "^\\d{8}T\\d{4}Z$" },
    "timestamp": { "type": "string", "format": "date-time" },
    "status": {
      "type": "string",
      "enum": ["complete", "limited", "empty", "failed"]
    },
    "sources_summary": {
      "type": "object",
      "patternProperties": {
        "^[a-z_]+$": {
          "type": "object",
          "properties": {
            "status": { "type": "string", "enum": ["ok", "degraded", "failed"] },
            "fetched": { "type": "integer", "minimum": 0 },
            "latency_ms": { "type": "integer", "minimum": 0 },
            "error": { "type": "string" }
          },
          "required": ["status", "fetched"]
        }
      }
    },
    "trending_topics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "topic_id": { "type": "string" },
          "title": { "type": "string" },
          "sources": {
            "type": "array",
            "items": { "type": "string" },
            "minItems": 1
          },
          "rrf_score": { "type": "number", "minimum": 0, "maximum": 100 },
          "trend": {
            "type": "string",
            "enum": ["rising", "stable", "declining"]
          },
          "cluster_size": { "type": "integer", "minimum": 1 },
          "first_seen_at": { "type": "string", "format": "date-time" }
        },
        "required": ["topic_id", "title", "sources", "rrf_score", "trend"]
      }
    },
    "competitor_insights": {
      "type": "object",
      "properties": {
        "total_accounts": { "type": "integer" },
        "alerts": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "account": { "type": "string" },
              "insight": { "type": "string" },
              "severity": { "type": "string", "enum": ["info", "warning", "critical"] }
            },
            "required": ["account", "insight", "severity"]
          }
        },
        "new_discovered": {
          "type": "array",
          "items": { "type": "string" }
        }
      },
      "required": ["total_accounts", "alerts"]
    },
    "topic_recommendations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "priority": { "type": "string", "enum": ["P0", "P1", "P2"] },
          "topic_title": { "type": "string" },
          "predicted_score": { "type": "number", "minimum": 0, "maximum": 100 },
          "angles": {
            "type": "array",
            "items": { "type": "string" },
            "minItems": 3,
            "maxItems": 5
          },
          "platform_hints": {
            "type": "object",
            "patternProperties": {
              "^[a-z_]+$": { "type": "string" }
            }
          },
          "rationale": { "type": "string" }
        },
        "required": ["priority", "topic_title", "predicted_score", "angles"]
      },
      "minItems": 3
    }
  }
}
```

---

## RRF 排序公式与超参数

### 公式

```
RRFscore(d) = Σᵢ [ 1 / (k + rankᵢ(d)) ]
```

其中：
- `d` = 候选话题条目
- `rankᵢ(d)` = 话题 d 在数据源 i 中的排名（1-based）
- `k` = 平滑常数（默认 60）
- `Σᵢ` = 对所有成功返回的数据源求和

### 加权变体

当需要按源质量加权时：

```
RRFscore_weighted(d) = Σᵢ [ wᵢ / (k + rankᵢ(d)) ]
```

默认权重：小红书=1.2, 抖音=1.2, 微博=1.0, 微信=0.8, 知乎=1.0, B站=1.0, 百度指数=1.5, 竞品=1.3, RSS=0.6

### 超参数表

| 参数 | 默认值 | 取值范围 | 说明 |
|---|---|---|---|
| k | 60 | 30-100 | k 越小高排名条目优势越大；k 越大偏向均匀分布 |
| weight_decay | 0.95 | 0.8-1.0 | 多日数据中，每天衰减权重 |
| cluster_threshold | 0.75 | 0.6-0.9 | 文本相似度阈值，低于此值视为不同话题 |
| boost_cross_source | 1.2 | 1.0-1.5 | 出现在 ≥3 个源中的话题的额外乘数 |

### 调优指南

- **k=30：** 短期热点（24h 时效内容，适合抖音/B站快跟）
- **k=60：** 平衡型（默认值，适合常规选题）
- **k=100：** 长期趋势（7d 周期，适合深度内容/系列策划）
- **weight_decay=0.95：** 每周衰减至上周权重的 ~70%（0.95⁷）
- **cluster_threshold < 0.6：** 过度合并，不同事件被误判为同一个
- **cluster_threshold > 0.9：** 过度拆分，同一事件被拆成多个 cluster

---

## 场景演练：一次完整的情报管道执行

### 场景：2026-05-19 周二 08:00-08:22

| 时间 | 阶段 | 事件 | 输出 |
|---|---|---|---|
| 08:00:00 | S1 | cron 触发，12 个 Adapter 并行启动 | — |
| 08:00:03 | S1 | 小红书 API 返回 429（限流），指数退避 3s 后重试成功 | degraded=1 |
| 08:00:12 | S1 | 竞品爆款 A API 超时（45s > 30s 阈值），标记 degraded | — |
| 08:00:15 | S1 | 百度指数认证失败 401，触发凭证轮换，新 Key 生效 | degrade=1, fail=0 |
| 08:02:31 | S1 | 全部源返回，统计：total_fetched=2,847, degraded=2, failed=0 ✅ | S1 完成 |
| 08:02:32 | S2 | 开始数据处理流程 | — |
| 08:02:35 | S2 | RRF 排序：k=60，2,847 条目 → fused top 200 | 排名完成 |
| 08:03:12 | S2 | 热点聚类：sentence-BERT 相似度计算，1,842 条目聚类为 47 个事件 | 47 clusters |
| 08:03:14 | S2 | 数据校验：verified count = 2,847，下游 count = 2,847 ✅ | S2 完成 |
| 08:03:15 | S3 | 竞品分析启动，10 个对标账号 | — |
| 08:05:40 | S3 | 策略变化检测：竞品 A 在抖音发布频率较上周 +40%（alert） | 1 insight |
| 08:06:11 | S3 | 新发现：竞品 B 账号在小红书粉丝 +200%，标记待观察 | — |
| 08:06:30 | S3 | 完成 | S3 完成 |
| 08:06:31 | S4 | 选题推荐启动，输入 47 个 events + 竞品 insights | — |
| 08:07:00 | S4 | 趋势分析：12 个 rising, 23 个 stable, 12 个 declining | — |
| 08:08:20 | S4 | LLM 生成角度建议（gpt-4o-mini），5/47 个 topic 使用了模板 fallback | 5 template fallbacks |
| 08:09:45 | S4 | XGBoost 爆款预测：P0=4, P1=7, P2=9 | — |
| 08:10:00 | S4 | 完成 | S4 完成 |
| 08:10:01 | S5 | 开始输出持久化 | — |
| 08:10:05 | S5 | intelligence.json 写入 → schema 校验通过 ✅ | 43KB |
| 08:10:08 | S5 | trending_topics.md 生成 → 包含 11 个推荐选题 ✅ | Markdown |
| 08:10:12 | S5 | competitor_analysis.md 生成 → 覆盖 10 个对标账号 ✅ | Markdown |
| 08:10:15 | S5 | relay 通知发送 → Worker 准备就绪 | message |
| 08:10:16 | S5 | **pipeline_complete** | 总计 ~10min 16s |

### 本次执行关键数据

- 总耗时：10 分 16 秒（预算上限 30 分钟 ✅）
- 热词总量：2,847 → 47 个事件 → 4 个 P0 选题
- 数据源健康度：10/12 ok, 2 degraded, 0 failed
- 告警：竞品 A 策略变化（抖音发布频率 +40%）
- 异常处理：1 次 429 退避、1 次超时降级、1 次凭证轮换，均未阻塞下游

---

## 冷启动数据

| 阶段 | 持续时间 | 能力 | 评判标准 |
|---|---|---|---|
| T0 原始收集 | 第 1-3 天 | 仅热词收集 + 竞品内容抓取，不做选题预测 | 每天至少收集 2,000 条原始热词 |
| T1 基线建立 | 第 4-7 天 | 简单选题推荐（基于频率统计，无 ML） | 能产出 P1/P2 选题，P0 仍为空 |
| T2 模型训练 | 第 8-14 天 | 收集 7 天数据 → 训练初始 XGBoost 模型 | AUC > 0.65 |
| T3 完整闭环 | 第 15 天起 | RRF + ML 预测 + 竞品分析全链路 | AUC > 0.75, 每天 ≥3 个 P0 选题 |

**关键里程碑：** 第 15 天反馈闭环建立时，情报输出质量才达到可稳定信赖水平。前两周的选题预测需人工复核。

**数据量预期（第 15 天时）：**
- 训练集样本：~2,000 条（14 天 × ~140 条/天）
- 特征维度：~30（含文本特征 + 互动特征 + 时间特征）
- 模型更新频率：每 7 天 re-train 一次

---

## 风险与应对

| 风险 | 概率 | 影响 | 检测方式 | 应对措施 |
|---|---|---|---|---|
| 所有 12 个数据源同时宕机 | 极低 (< 0.1%) | 严重（当天无情报输出） | Health check 持续fail | 降级至本地缓存数据（上一日 intelligence.json），标注 stale=true |
| intelligence.json 写入时损坏 | 低 (1%) | 中（下游 worker 用错误数据） | 写入后 checksum 校验 | 自动回滚至上一有效版本，触发告警 |
| cron 调度器 miss（08:00 未被触发） | 中 (3%) | 中（当天无 08:00 情报） | 10 分钟迟到容忍窗口 | 09:00 重试一次；仍 miss 则手动触发 |
| 单个源持续失效 > 3 天 | 中 (5%) | 低-中（剩余 11 源仍可用） | degradation 累计计数器 | 标记 DEAD，切换 fallback 源，发起工单修复 |
| 竞品账号 API 改版 | 中 (8%) | 中（竞品分析模块失效） | API 返回格式异常 | 临时切换至爬虫模式，同时更新 Adapter |
| RRF 排序过拟合至单个源 | 低 (2%) | 中（选题偏斜） | per-source score 分布跟踪 | 引入 diversity penalty：同源 > 40% 前 20 名时自动衰减权重 |
| 输出文件被其他进程误修改 | 低 (1%) | 低（仅影响本日数据） | 文件 mtime 监控 | 写时加锁 (flock)，异常修改触发告警 |
| XGBoost 模型过期（数据分布漂移） | 中 (10%) | 中（预测准确率下降） | AUC 监控 < 0.70 连续 3 天 | 触发 re-train pipeline，并通知数据团队 review |

---

## 反馈闭环

情报管线不是单向的。每天 11:00 数据回收后，实际数据分析结果反馈回情报层，调整热点评分权重、优化角度推荐算法、更新竞品分析策略。反馈数据类型包括选题准确度、热词转化率、误判记录、新信号发现。

### 反馈循环周期

| 时间 | 事件 |
|---|---|
| 08:00 | 情报管道输出 |
| 08:00-11:00 | Worker 使用情报创作内容并发布 |
| 11:00 | 数据回收：抓取已发布内容的互动数据 |
| 11:15 | feedback_loop.py 执行：对比预测 vs 实际表现 |
| 11:30 | 权重更新：RRF 权重、k 值、cluster_threshold 自动调优 |

### 反馈指标

| 指标 | 目标值 | 触发动作 |
|---|---|---|
| 选题命中率 | > 70% | < 60% 时执行回顾分析 |
| 热词 → 选题转化率 | > 40% | < 30% 时调整 RRF 阈值 |
| 误判率（推荐了但表现差） | < 20% | > 30% 时回滚至上一版权重 |
| 新信号发现率 | > 5% | < 3% 时 add source review |

---

## 附录

### A. 分支合并 — "The Joker" 说明

在极端情况下（如上日数据全部丢失或 cold-start 阶段），系统采用 Joker 分支策略：由 LLM 基于当前竞品动态和行业趋势生成一组种子选题，人工审核通过后作为初始推荐输入到 Worker 并同步存入 intelligence.json，待第二天 pipeline 正常执行后覆盖。

### B. 架构预留

- **全球化扩展：** 预留 adapter 接口，后续接入 TikTok 全球趋势、Google Trends
- **多模态情报：** 预留 image_analysis 和 video_transcript 字段（当前为 null）
- **AB 测试支持：** 支持两套 RRF 参数同时运行并对比输出质量
