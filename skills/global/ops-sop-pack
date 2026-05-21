---
name: ops-sop-pack
description: 墨维运维 Agent SOP 技能包 — 系统状态监控/组件维护/故障排查/部署管理
category: molin-org
version: 1.0.0
tags: [sop, ops, devops, monitoring, maintenance, deploy]
trigger: 所有运维任务（状态检查/故障排查/组件更新/部署）必须先加载此技能
---

# 墨维运维 Agent SOP 技能包

## 适用 Agent
- 墨维运维 (ops.py)
- 基座：molin-ops, ghost-os

---

## 一、Lead SOP（运维需求获取）

### 监控源

| 源 | 方式 | 频次 | 优先级 |
|------|------|------|--------|
| 系统健康状态 | 定时检查（molin-ops） | 每30分钟 | P0 |
| Cron 运行状态 | cronjob list 检查 | 每小时 | P0 |
| 磁盘/内存 | 系统资源监控 | 每小时 | P1 |
| 组件版本 | 依赖版本检查 | 每日 | P2 |
| 日志异常 | 系统日志扫描 | 每小时 | P1 |

### 状态分级

| 级别 | 含义 | 动作 |
|------|------|------|
| 🟢 正常 | 所有组件健康 | 记录 |
| 🟡 警告 | 单组件降级/性能下降 | 自动恢复或通知 |
| 🟠 异常 | 组件不可用/功能受损 | 立即恢复 + L1 通知 |
| 🔴 严重 | 系统级故障 | L3 董事会 |

---

## 二、Execution SOP（运维处理流程）

### 日常运维流水线

```
状态采集 → 健康评估 → 异常处理 → 记录归档
```

### Step 1: 系统状态采集

采集项：
- [ ] Hermes Agent 运行状态
- [ ] Cron 作业状态（有无失败/超时）
- [ ] 磁盘使用率（> 80% 预警）
- [ ] 内存使用率
- [ ] 网络连通性（API 端点可达性）
- [ ] ~/.hermes/ 关键文件完整性
- [ ] Git 仓库状态（有无未提交变更）

### Step 2: 健康评估

综合评分：
```yaml
health_score: 95  # 0-100
status: "healthy"
alerts: []
components:
  hermes_agent: {"status": "running", "uptime": "7d 3h"}
  cron_system: {"status": "ok", "total": 8, "failed": 0}
  disk: {"usage": 62, "status": "ok"}
  memory: {"usage": 45, "status": "ok"}
  network: {"reachable": ["deepseek", "github", "feishu"], "unreachable": []}
  git: {"status": "clean", "uncommitted": 0}
```

### Step 3: 异常处理

| 异常 | 处理方式 |
|------|----------|
| Cron 作业失败 | 检查错误日志，重启或修正 |
| 磁盘将满 | 清理缓存/tmp/日志 |
| API 端点不可达 | 重启网络或备用路由 |
| Git 冲突 | 标记 + L1 通知 |
| 进程僵死 | kill -9 + 重启 |

### Step 4: 记录归档

| 频次 | 产出 | 位置 |
|------|------|------|
| 每日 | 运维日报（含状态快照） | Obsidian `Agents/墨维运维/日报/` |
| 每周 | 运维周报（含趋势和问题） | Obsidian |

---

## 三、QA SOP

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 覆盖全面 | 30% | 所有关键组件是否被监控？ |
| 告警准确 | 25% | 告警是否必要？误报率？ |
| 响应时效 | 25% | 异常是否在 SLA 内处理？ |
| 文档完整 | 20% | 操作记录是否完整？ |

---

## 四、Escalation SOP

| 场景 | 触发 | 动作 |
|------|------|------|
| 磁盘 > 90% | 空间严重不足 | L1 通知 + 立即清理 |
| 核心 API 中断 > 30分钟 | 关键 Provider 不可用 | L2 审批 + 切换 Provider |
| 系统进程崩溃 | Hermes Agent 挂掉 | L3 董事会 + 手动重启 |
| 日志异常模式 | 持续报错 | L1 通知 + 根因分析 |

---

## 五、Cron 经营节奏

| 时间 | 任务 | 产出 |
|------|------|------|
| 每30分钟 | 系统健康检查 | 状态快照（到告警阈值才通知） |
| 每小时 | Cron 状态检查 | 失败任务告警 |
| 每日 07:00 | 运维日报 | Obsidian 日报 |
| 每日 23:30 | 系统健康总结（日报归档） | Obsidian |

---

## 六、参考

- 运维基座：`skill_view('molin-ops')`
- 系统关键文件：AGENTS.md "系统关键文件位置"
- 历史故障记录：参考故障存档
- Cron 作业：`cronjob(action='list')`
