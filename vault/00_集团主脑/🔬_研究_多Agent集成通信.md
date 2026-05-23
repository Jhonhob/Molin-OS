---
created: 2026-05-19
updated: 2026-05-19
agent: system
category: 标准规范
status: 活跃
---

# 多Agent集成与通信标准

## SCQA — 为什么是多Agent架构？

**Situation（情境）：** 墨麟OS承载教育、出海、内容、增长、系统运维五大业务域，每个域有独立的Worker集群、飞书AppID、知识库（Supermemory）和配置体系。

**Complication（冲突）：** 单一Agent架构下，所有业务共享同一个上下文窗口和推理引擎。随着Worker数量增长（当前15+ Worker），单一Agent的上下文碎片化严重，指令优先级冲突频发，且任一业务的配置变更都需要全局重启。

**Question（问题）：** 如何在不牺牲业务间协作能力的前提下，实现隔离自治、独立迭代、按需扩展的多Agent体系？

**Answer（答案）：** 采用多Agent + 消息总线架构。每个Agent拥有独立进程、独立Supermemory容器、独立飞书App入口，通过事件驱动总线进行跨Agent通信。Worker层作为可插拔的执行单元，按Agent域归属。

本文档定义所有Agent的集成配置快照、Supermemory容器映射、Agent画像定义、通信协议、安全边界及飞书集成规范，作为系统层多Agent集成与通信的唯一参考标准。

---

## 一、Agent总览

| Agent | 名称 | 容器tag | 飞书AppID | 关联Worker |
|-------|------|---------|-----------|------------|
| edu | 元瑶教育 | edu | cli_a956c83187395cd4 | education.py |
| global | 梅凝出海 | molin-global | cli_aa881c316d789bb5 | global_marketing.py |
| media | 银月传媒 | molin-media | cli_a966ede1d9789bd2 | content_writer/designer/short_video/voice_actor |
| shared | 玄骨中枢 | molin-shared | cli_aa884b4a88bc9bb4 | crm/customer_service/ops/finance/data_analyst/ecommerce |
| side | 宋玉创业 | molin-side | cli_a9513691d4f89bcf | — |

**会话量统计（周均）：**

| Agent | 周会话数 | 平均响应时间 | 峰值并发 |
|-------|---------|-------------|---------|
| edu | 1,200 | 2.3s | 45 |
| media | 3,500 | 3.1s | 120 |
| global | 680 | 2.8s | 30 |
| shared | 2,100 | 1.9s | 80 |
| side | 420 | 2.5s | 15 |

---

## 二、Agent画像定义

**元瑶教育：** 教育业务大脑，专注逻辑思维课程全链路运营，可调用8个子公司Worker覆盖招生→交付→服务→复购。

**银月传媒：** 内容品牌主Agent，覆盖设计、文案、运维、财务、调研、出海、客服全栈能力，是内容飞轮的核心执行者。

**梅凝出海：** 出海专线Agent，专注台湾和东南亚市场的本地化内容运营和平台变现，从内容本地化起步逐步建立海外分发矩阵。

**玄骨中枢：** 系统治理与审计Agent，负责共享服务层的文档审查、合规管理、系统运维，是墨麟OS的运维中枢。

**宋玉创业：** 增长策略Agent，负责数据分析、增长实验、副业探索，驱动墨麟OS的商业化增长。

---

## 三、Supermemory容器映射

每个Agent拥有独立的Supermemory容器（独立知识库空间），支持长期记忆与跨会话上下文检索。

| Agent | 容器ID | Vault路径 | 存储内容 |
|-------|--------|----------|---------|
| edu | sm-cnt-edu-01 | `/vaults/edu/` | 课程体系、学员成长档案、题库、知识图谱 |
| global | sm-cnt-global-01 | `/vaults/global/` | 海外市场调研、本地化词典、平台规则库 |
| media | sm-cnt-media-01 | `/vaults/media/` | 品牌资产库、设计模版、内容SOP、素材库 |
| shared | sm-cnt-shared-01 | `/vaults/shared/` | 共享知识库、审计日志、系统配置快照、合规标准 |
| side | sm-cnt-side-01 | `/vaults/side/` | 增长实验记录、数据看板、商业模型库 |

**容器访问规则：**
- 每个Agent默认只读写自己的容器。
- 跨容器读取需通过共享Agent（玄骨中枢）的授权访问接口，不可直接跨容器操作。
- 所有跨容器访问在共享Agent审计日志中记录。

---

## 四、飞书集成规范

飞书App作为Agent的统一交互入口，CLI作为技术操作入口，REST API作为系统集成入口。三个入口共享同一套DARE推理框架，确保交互一致性。

Agent在飞书的回复必须使用飞书友好格式——纯文字分段、适配飞书卡片消息模版、避免不支持Markdown格式。

**飞书API限流：** 飞书开放平台对每个AppID的API调用存在频次限制（默认100次/秒，消息发送50次/秒）。超出限制时，返回 `HTTP 429` 并在响应头携带 `X-RateLimit-Reset`。Agent必须实现指数退避重试（初始间隔1s，最大间隔30s，最大重试3次）。

---

## 五、环境变量与配置

所有Agent共享以下环境变量体系：`DEEPSEEK_API_KEY`、`SUPERMEMORY_API_KEY`、`GITHUB_TOKEN`。各Agent通过profile级 `.env` 文件配置独立变量。`GATEWAY_ALLOW_ALL_USERS` 必须在每个profile的 `.env` 中独立设置。

---

## 六、安全与权限边界

### 6.1 GATEWAY_ALLOW_ALL_USERS 影响分析

`GATEWAY_ALLOW_ALL_USERS=true` 意味着Agent Gateway不对终端用户做身份过滤。在多Agent环境中，此配置允许任意用户通过任意Agent Gateway发送请求。**风险：** 用户可通过edu Gateway向shared Agent发送命令，绕过shared Agent自身的权限校验。

**建议：** 仅对公共入口Agent（如media）开启此标志。内部治理Agent（如shared）应设置为 `false`，并结合飞书token进行用户角色校验。

### 6.2 Token作用域

| 类型 | 作用域 | 有效期 | 存储位置 |
|------|-------|-------|---------|
| Agent内部token | 该Agent及其Worker | 24h | 内存 + `.env` |
| 跨Agent token | 经shared Agent签发的临时令牌 | 15min | 消息头 |
| 飞书App token | 飞书API鉴权 | 2h | 自动续期 |

### 6.3 跨Agent权限边界

```
用户 → 飞书App → Agent Gateway ─┬─ 本Agent Worker（允许）
                                  ├─ 跨Agent消息（需shared Agent审计）
                                  └─ 外部API调用（限频+白名单）
```

- Agent之间不允许直接访问对方的Supermemory容器。
- Agent之间的消息传递必须经过事件总线，并携带调用链ID（trace_id）。
- 敏感操作（删除、修改系统配置）需要shared Agent二次确认。

---

## 七、Agent间通信协议

### 7.1 服务发现

Agent启动时向事件总线注册自身元信息：

```json
{
  "agent_id": "edu",
  "capabilities": ["education", "curriculum", "student_management"],
  "endpoint": "http://edu-agent:8080",
  "status": "active",
  "version": "1.2.0"
}
```

其他Agent通过总线查询能力匹配（例如media需要学生数据时，查询 `capabilities` 包含 `student_management` 的Agent），得到edu的端点信息。

### 7.2 消息总线

采用事件驱动架构，基于Redis Stream实现轻量级消息总线。

| 事件类型 | 发送者 | 订阅者 | 用途 |
|---------|-------|-------|------|
| `agent.query` | 任意Agent | 能力匹配的Agent | 跨Agent数据查询 |
| `agent.notify` | 任意Agent | 全部Agent | 状态广播通知 |
| `agent.task.assign` | shared Agent | 目标Agent | 任务分配 |
| `agent.health` | 各Agent | shared Agent | 心跳上报 |

### 7.3 消息格式

```json
{
  "event_id": "evt_20260519_a1b2c3d4",
  "trace_id": "trace_edu_media_001",
  "event_type": "agent.query",
  "source": "media",
  "target": "edu",
  "payload": {
    "query_type": "student_enrollment",
    "params": {"course_id": "CS101", "date_range": "2026-05"}
  },
  "timestamp": 1716123456
}
```

### 7.4 交互场景示例

**场景：银月传媒（media）为某个课程制作推广视频，需要从元瑶教育（edu）获取学员画像数据。**

```
1. media Agent 构建查询 → 发送 agent.query 事件到消息总线
2. 总线根据 target=edu 路由消息
3. edu Agent 接收事件 → 查询本地 Supermemory 容器 /vaults/edu/
4. edu 返回结果（脱敏处理的学员画像摘要）
5. media 将画像数据注入 content_writer Worker 的 Prompt
6. content_writer 生成文案 → designer 制作素材 → short_video 合成视频
7. 完成通知经总线回传 shared Agent 归档审计日志
```

**关键原则：** 跨Agent数据请求必须返回脱敏/摘要数据，不传递原始PII。脱敏策略由数据持有方（edu）自主决定。

---

## 八、健康检查与容灾

### 8.1 Agent心跳机制

每个Agent每30秒向事件总线发送 `agent.health` 事件：

```json
{
  "event_type": "agent.health",
  "source": "edu",
  "status": "active",
  "uptime_seconds": 86400,
  "last_query_latency_ms": 230,
  "worker_count": 8,
  "memory_usage_pct": 62
}
```

### 8.2 失效检测

共享Agent（玄骨中枢）作为健康检查中心，对每个Agent维护状态表：

| Agent | 最后心跳 | 状态 | 连续失败次数 |
|-------|---------|------|------------|
| edu | 2026-05-19 18:14:23 | active | 0 |
| media | 2026-05-19 18:14:20 | active | 0 |

- 超过90秒未收到心跳 → 标记为 `degraded`
- 超过180秒未收到心跳 → 标记为 `down`，触发告警通知
- 连续失败次数 ≥ 6 → 自动关闭该Agent关联的飞书App入口（通过飞书API禁用Bot）

### 8.3 断路器

Agent间通信的断路器按目标Agent独立维护：

| 目标Agent | 失败阈值 | 半开窗口 | 当前状态 |
|-----------|---------|---------|---------|
| edu | 5次/60s | 30s | closed |
| shared | 3次/60s | 15s | closed |

- **closed**: 正常转发
- **open**: 拒绝转发，返回 `CIRCUIT_OPEN` 错误码
- **half-open**: 尝试发送1条探测消息，成功后回退closed，失败继续open

### 8.4 飞书API限流失效场景

当飞书API返回 `429 Too Many Requests` 时：

```
1. Agent 记录限流日志（含 retry_after 值）
2. 排入重试队列，按指数退避重试（1s, 2s, 4s, 8s, 16s, 30s）
3. 超过 3 次重试仍失败 → 消息降级：缓存至本地队列，标记为 PENDING
4. 每 5 分钟轮询重试队列
5. 若 30 分钟内仍无法发送 → 通过 shared Agent 发送管理员告警
```

### 8.5 Agent Gateway宕机

场景：某个Agent的Gateway进程崩溃，不响应心跳。

```
1. 180秒无心跳 → shared Agent 标记该 Agent 为 down
2. 飞书App入口自动禁用（避免用户发送消息但无响应）
3. 分配给该Agent的Worker任务重新路由到 shared Agent 的临时队列
4. 自动重启脚本（systemd/launchd）尝试重启 Gateway 进程
5. 重启成功 → Agent 发送注册事件 → shared 将其标记为 active
6. 恢复飞书App入口 → 处理临时队列积压消息
```

---

## 九、系统拓扑

```
                             ┌─────────────────────┐
                             │    飞书开放平台       │
                             │  (5个AppID入口)       │
                             └────────┬─────────────┘
                                      │ HTTPS / Webhook
                                      ▼
         ┌─────────────────────────────────────────────┐
         │         Agent Gateway Layer                  │
         │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌────┐ │
         │  │ edu  │ │media │ │global│ │shared│ │side│ │
         │  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └─┬──┘ │
         └─────┼─────────┼─────────┼─────────┼──────────┘
               │         │         │         │
         ┌─────┴─────────┴─────────┴─────────┴──────────┐
         │          事件总线 (Redis Stream)               │
         └─────┬─────────┬─────────┬─────────┬──────────┘
               │         │         │         │
         ┌─────┴─────────┴─────────┴─────────┴──────────┐
         │         Worker 执行层                          │
         │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌────┐ │
         │  │ edu  │ │media │ │global│ │shared│ │side│ │
         │  │ .py  │ │Wkr.  │ │ .py  │ │Wkr.  │ │Wkr.│ │
         │  └──────┘ └──────┘ └──────┘ └──────┘ └────┘ │
         └──────────────┬────────────────────────────────┘
                        │
         ┌──────────────┼────────────────────────────────┐
         │              ▼                                 │
         │   ┌─────────────────────┐   ┌──────────────┐  │
         │   │  Supermemory Layer  │   │  CLI 入口     │  │
         │   │  5个独立容器/Vault   │   │  (终端工具链)  │  │
         │   └─────────────────────┘   └──────────────┘  │
         └────────────────────────────────────────────────┘
```

**关系说明：**
- **飞书入口 → Agent Gateway**: 用户消息经飞书Webhook路由到对应Agent
- **Agent → 事件总线**: 内部Agent间通信不经过飞书，直接通过总线
- **Agent → Worker**: 每个Agent调用其域下的Worker集群（RPC调用）
- **Agent → Supermemory**: 各Agent独占各自的Supermemory容器，跨容器需授权
- **CLI入口**: 直接连接事件总线，供技术操作用户绕过飞书发送命令

---

## 十、风险矩阵

| 风险 | 概率 | 影响 | 触发条件 | 降级策略 |
|------|------|------|---------|---------|
| 某Agent Gateway宕机 | 低 | 高 | 进程崩溃 / OOM | 重启 + 队列重路由 |
| 飞书API限流429 | 中 | 中 | 消息峰值超过50次/秒 | 指数退避 + 消息降级 |
| Supermemory写入失败 | 低 | 中 | 存储配额满 / 网络分区 | 本地缓存 + 异步重试 |
| 事件总线（Redis）故障 | 极低 | 极高 | Redis宕机 | 降级为直连模式，告警 |
| 跨Agent权限泄露 | 中 | 高 | 配置错误 / token泄漏 | shared Agent审计拦截 |
| Agent上下文溢出（LLM） | 中 | 低 | 会话过长 | 自动截断 + Supermemory RAG |

---

## 附录A：配置示例

```bash
# edu/.env
DEEPSEEK_API_KEY=sk-xxx
SUPERMEMORY_API_KEY=sm-xxx
SUPERMEMORY_VAULT=/vaults/edu/
GATEWAY_ALLOW_ALL_USERS=true
AGENT_HEARTBEAT_INTERVAL=30
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=30
```

```bash
# shared/.env
DEEPSEEK_API_KEY=sk-xxx
SUPERMEMORY_API_KEY=sm-xxx
SUPERMEMORY_VAULT=/vaults/shared/
GATEWAY_ALLOW_ALL_USERS=false  # 内部治理Agent不开放公共入口
AGENT_HEARTBEAT_INTERVAL=30
HEALTH_CHECK_INTERVAL=30
CIRCUIT_BREAKER_THRESHOLD=3
CIRCUIT_BREAKER_TIMEOUT=15
```

## 附录B：修订历史

| 版本 | 日期 | 修改内容 | 修订人 |
|------|------|---------|-------|
| v1.0 | 2026-05-19 | 初始版本：Agent总览、画像、飞书集成、环境变量 | — |
| v2.0 | 2026-05-19 | 升级：SCQA架构说明、Supermemory容器映射、通信协议、安全边界、健康检查、拓扑图、风险矩阵 | Hermes Agent |
