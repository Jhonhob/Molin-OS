---
title: 多Agent集成与通信标准
status: 活跃
last_updated: 2026-05-19
agent_sync: true
frameworks_applied:
  - MECE
---

本文档定义所有Agent的集成配置快照、Supermemory容器映射、Agent画像定义及飞书集成规范，作为系统层多Agent集成与通信的唯一参考标准。

---

## 一、Agent总览

| Agent | 名称 | 容器tag | 飞书AppID | 关联Worker |
|-------|------|---------|-----------|------------|
| edu | 元瑶教育 | edu | cli_a956c83187395cd4 | education.py |
| global | 梅凝出海 | molin-global | cli_aa881c316d789bb5 | global_marketing.py |
| media | 银月传媒 | molin-media | cli_a966ede1d9789bd2 | content_writer/designer/short_video/voice_actor |
| shared | 玄骨中枢 | molin-shared | cli_aa884b4a88bc9bb4 | crm/customer_service/ops/finance/data_analyst/ecommerce |
| side | 宋玉创业 | molin-side | cli_a9513691d4f89bcf | — |

## 二、Agent画像定义

元瑶教育：教育业务大脑，专注逻辑思维课程全链路运营，可调用8个子公司Worker覆盖招生→交付→服务→复购。

银月传媒：内容品牌主Agent，覆盖设计、文案、运维、财务、调研、出海、客服全栈能力，是内容飞轮的核心执行者。

梅凝出海：出海专线Agent，专注台湾和东南亚市场的本地化内容运营和平台变现，从内容本地化起步逐步建立海外分发矩阵。

玄骨中枢：系统治理与审计Agent，负责共享服务层的文档审查、合规管理、系统运维，是墨麟OS的运维中枢。

宋玉创业：增长策略Agent，负责数据分析、增长实验、副业探索，驱动墨麟OS的商业化增长。

## 三、飞书集成规范

飞书App作为Agent的统一交互入口，CLI作为技术操作入口，REST API作为系统集成入口。三个入口共享同一套DARE推理框架，确保交互一致性。

Agent在飞书的回复必须使用飞书友好格式——纯文字分段、适配飞书卡片消息模版、避免不支持Markdown格式。

## 四、环境变量与配置

所有Agent共享以下环境变量体系：DEEPSEEK_API_KEY、SUPERMEMORY_API_KEY、GITHUB_TOKEN。各Agent通过profile级.env文件配置独立变量，GATEWAY_ALLOW_ALL_USERS必须在每个profile的.env中独立设置。
