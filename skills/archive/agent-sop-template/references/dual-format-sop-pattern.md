# 双格式 SOP 模式

## 背景

Molin-OS 中 SOP 有两种格式共存，职责互补：

| 格式 | 位置 | 加载方式 | 职责 |
|------|------|----------|------|
| **YAML** | `sop/definitions/{id}.yaml` | SOP Engine (`sop/engine.py`) | 结构化步骤、触发条件、变量、治理级别 |
| **Markdown** | `~/.hermes/skills/{name}/SKILL.md` | Hermes `skill_view()` | 执行知识、最佳实践、检查清单、模板 |

## 何时用哪种

**创建新 SOP 时：先建 Hermes Skill（Markdown），运行稳定后补 YAML 定义。** 因为：
- Hermes Skill 是 Agent 的工作指引，内容灵活，可快速迭代
- YAML 定义是 Engine 的执行蓝图，需要结构稳定后才值得写

## 目录约定

```
sop/definitions/              ← SOP Engine YAML 定义（结构化）
  auto_dream_sop.yaml
  crm_private_domain_sop.yaml
  ...

~/.hermes/skills/{name}/      ← Hermes 技能文件（知识型）
  autodream-sop-pack/SKILL.md
  crm-sop-pack/SKILL.md
  ...
```

## 关联方式

Hermes Skill 的 SKILL.md 最后应包含 SOP Engine 引用：

```markdown
## 系统集成

### SOP Engine 关联
本技能对应的 SOP Engine 定义文件：
`sop/definitions/{id}.yaml` — 由 SOP Engine 加载，提供结构化执行步骤和触发条件。
当 `SOP_AUTOMATION_ENABLED=true` 时，SOP Engine 与本技能协同工作：Engine 负责步骤控制，本技能提供具体执行知识。
```

## 治理级别对照

YAML 中的 `governance_level` 与 Hermes 的 L0-L4 一一对应：

| YAML 值 | 含义 | Hermes 对应 |
|---------|------|-------------|
| L0 | 自动执行 | auto |
| L1 | 通知后执行 | notify |
| L2 | 审批后执行 | approve |
| L3 | 董事会审批 | board_approve |
| L4 | 绝对禁止 | forbidden |

## 完整 SOP 生命周期

```
1. 识别需求（用户/审计/运营反馈）
2. 创建 Hermes Skill（Markdown）→ 立即可用
3. 运行验证（3-5 次执行）
4. 创建 SOP Engine YAML 定义（结构化）
5. 在 Skill 中添加 YAML 引用
6. 设置 Cron 经营节奏
7. 持续迭代（双文件同步更新）
```
