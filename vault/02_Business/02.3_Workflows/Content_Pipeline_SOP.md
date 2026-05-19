---
title: 内容情报管道标准作业程序
status: 迭代中 (Active)
last_updated: 2026-05-19
agent_sync: true
---

## 内容情报管道

## 结论

内容情报管线的核心使命：**在内容创作之前，先知道"什么在赢"**。

传统的内容创作流程是"凭感觉写→发出去看效果"，效率极低且不确定性高。内容情报管道要做的是在落笔之前完成：

1. 识别当前平台的热门话题和趋势信号
2. 分析竞品的爆款内容和互动数据
3. 预测哪些选题有更高的爆款概率
4. 生成结构化的选题建议给下游Worker

**适用位置**：墨麟全媒体内容飞轮的"情报层 (08:00)"。

## 方法

### 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         内容情报管线                              │
│                                                                  │
│  08:00 定时触发                                                  │
│     │                                                            │
│     ├── S1: 热词收集 ──── 从12+数据源并行拉取热词                 │
│     │      ├── 小红书热词（搜索趋势+笔记热词）                    │
│     │      ├── 抖音热词（热点榜+话题标签）                       │
│     │      ├── 微博热搜                                          │
│     │      ├── 微信话题（公众号热文+视频号热点）                  │
│     │      ├── 知乎热榜                                          │
│     │      ├── B站热门                                           │
│     │      ├── 百度指数/微信指数                                 │
│     │      ├── 竞品账号最新爆款                                  │
│     │      └── 行业新闻/RSS                                      │
│     │                                                            │
│     ├── S2: 数据处理 ──── 归一化+评分+融合                       │
│     │      ├── URL/文本归一化                                    │
│     │      ├── 互动率计算（统一公式）                             │
│     │      ├── 跨源RRF融合排序                                   │
│     │      └── 热点聚类（同一事件合并）                          │
│     │                                                            │
│     ├── S3: 竞品分析 ──── 深度对标                               │
│     │      ├── 对标账号列表维护                                  │
│     │      ├── 竞品最新内容抓取                                  │
│     │      ├── 互动数据对比                                      │
│     │      └── 打法识别和模式提取                                │
│     │                                                            │
│     ├── S4: 选题推荐 ──── 结构化输出                             │
│     │      ├── 热度趋势分析（上升/稳定/下降）                     │
│     │      ├── 角度建议（5个差异化角度）                         │
│     │      ├── 平台适配建议                                      │
│     │      └── 爆款概率预测                                      │
│     │                                                            │
│     └── S5: 输出持久化 ──── relay/media/intelligence.json        │
│            ├── intelligence.json（结构化情报数据）                 │
│            ├── trending_topics.md（人工可读的热点简报）            │
│            └── competitor_analysis.md（竞品分析报告）             │
│                                                                  │
│  数据回收反馈（11:00后）                                          │
│     ↑  ← 墨镜数据 → 哪些选题预测准确？                           │
│     ↑  ← 墨镜数据 → 哪些热词转化率高？                           │
│     ↑  ← 墨镜数据 → 什么角度效果最好？                           │
└─────────────────────────────────────────────────────────────────┘
```

### 数据源接入（Source Adapter 模式）

借鉴 last30days 的 BYOK（Bring Your Own Keys）设计，每种数据源作为一个独立的 Adapter。

#### 免费数据源（零配置可用）

| 数据源 | 接入方式 | 获取内容 | 成本 |
|--------|---------|---------|------|
| 微博热搜 | 公开API/爬虫 | 实时热搜榜 | 免费 |
| GitHub Trending | GitHub API | 热门项目 | 免费 |
| Hacker News | Algolia API | 热门讨论 | 免费 |
| Reddit | 公共JSON API | 热门帖子+评论 | 免费 |
| 知乎热榜 | 公开页面解析 | 实时热榜 | 免费 |
| B站热门 | 公开API | 热门视频列表 | 免费 |

#### 需认证的数据源

| 数据源 | 接入方式 | 获取内容 | 成本 |
|--------|---------|---------|------|
| 小红书热词 | 自有API / 浏览器Cookie | 搜索热词+笔记数据 | 免费（自有） |
| 抖音热词 | 自有API / 浏览器Cookie | 热点榜+话题标签 | 免费（自有） |
| 微信指数 | 微信开放平台 | 微信趋势数据 | 免费 |
| 百度指数 | 百度API | 搜索趋势数据 | 有免费额度 |
| 新榜/飞瓜 | 付费API | 行业竞品数据 | 付费 |

#### Adapter 接口规范

```
interface SourceAdapter {
    name: string;
    isReady(): boolean;
    collect(context: CollectionContext): Promise<CollectionResult>;
    getQuota(): { remaining: number, limit: number, resetAt: string };
}

interface CollectionResult {
    source: string;
    items: SourceItem[];
    errors: AdapterError[];
    collectedAt: string;
    duration: number;
}

interface SourceItem {
    id: string;
    title: string;
    url: string;
    platform: string;
    metrics: {
        engagement_score: number;
        views?: number;
        likes?: number;
        comments?: number;
        shares?: number;
    };
    content_type: string;
    published_at: string;
    tags: string[];
    summary: string;
}
```

### 数据处理管线细节

#### S1：热词收集

每个 Adapter 独立运行，互不干扰：
- ThreadPoolExecutor 并行拉取（最多8并发）
- 每个源超时30秒
- 429限流时自动降频
- 一个源失败不影响其他源

#### S2：数据归一化流程

```
原始拉取数据
  │
  ├── 文本清洗（去HTML标签、特殊字符、表情符号标准化）
  │
  ├── 互动评分计算
  │   engagement_score = (likes×2 + comments×3 + shares×5) / max(views, 1) × 10000
  │
  ├── 标签提取（关键词/分类/话题标签）
  │
  ├── 跨源RRF融合排序
  │   RRF_score = Σ(1 / (k + rank_per_source))
  │   k = 60（与last30days一致）
  │
  └── 热点聚类
      提取实体（大写词/数字/专有名词）
      Overlap Coefficient 实体重叠检测
      MMR多样性保留，λ=0.75
```

#### S4：选题推荐结构

```json
{
  "date": "2026-05-15",
  "hot_topics": [
    {
      "keyword": "AI一人公司",
      "trend": "up",
      "sources": ["小红书", "抖音", "微信"],
      "avg_engagement": 12.5,
      "cluster_count": 8,
      "suggested_angles": [
        {
          "angle": "从0到1搭建AI一人公司的全链路",
          "target_platform": "小红书",
          "predicted_score": 8.5,
          "reasoning": "教程类内容在小红书互动率高于平均值35%"
        }
      ]
    }
  ],
  "competitor_highlights": [],
  "feedback_loop_input": {
    "previous_recommendations": [
      {
        "topic": "AI工具推荐",
        "predicted_score": 7.5,
        "actual_avg_score": 8.2,
        "accuracy": "good"
      }
    ]
  }
}
```

### 输出规范

输出到 relay/media/intelligence.json，被所有下游Worker消费：

```json
{
  "meta": {
    "collected_at": "2026-05-15T08:00:00+08:00",
    "duration_ms": 45000,
    "sources_used": 8,
    "sources_failed": 0,
    "total_items_collected": 342,
    "version": "1.0.0"
  },
  "hot_topics": [],
  "competitor_analysis": [],
  "trending_formats": {
    "小红书": { "winning_types": [], "avg_engagement_by_format": {} },
    "抖音": { "winning_types": [], "avg_completion_rate": {} }
  },
  "platform_timing": {
    "小红书": { "best_time": "08:00", "second_best": "12:00", "worst_time": "03:00" },
    "抖音": { "best_time": "19:00", "second_best": "12:30", "worst_time": "04:00" }
  },
  "ready_for_consumption": true
}
```

### 反馈闭环

情报管线不是单向的。每天 11:00 数据回收后，墨镜数据会输出 feedback 回情报层：

```
墨镜数据 → writes relay/media/analytics_feedback.json
    ↑
情报管线 → 在下次(08:00)读取feedback
    → 调整热点评分权重
    → 优化角度推荐算法
    → 更新竞品分析策略
```

反馈数据类型：
1. **选题准确度** — 昨天推荐的选题，哪些实际效果更好？
2. **热词转化率** — 哪些热词带来的内容互动率更高？
3. **误判记录** — 哪些推荐效果差？原因分析？
4. **新信号发现** — 内容实际数据中出现的、情报层没捕捉到的信号

## 下一步

- [ ] **冷启动第一周**：仅做热词收集+竞品分析，不做选题预测（无基准数据）
- [ ] **冷启动第二周**：基于第一周数据做简单选题推荐
- [ ] **冷启动第三周后**：完整反馈闭环建立，使用数据驱动选题
- [ ] 创建 relay/media/intelligence_config.json（对标账号列表、权重配置、平台配置）
- [ ] 实现首个 Adapter（微博热搜/知乎热榜等免费源先行）
- [ ] 建立竞品对标账号列表
- [ ] 对接墨镜数据反馈格式

## 修订日志 (Changelog)

- **2026-05-19**: 从流程/系统｜内容情报管道.md 迁移
