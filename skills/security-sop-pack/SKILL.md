---
name: security-sop-pack
description: 墨安安全 Agent SOP 技能包 — 系统安全审计/API密钥管理/异常检测/渗透测试/应用安全工程/威胁建模/安全代码审查
category: molin-org
version: 1.1.0
tags: [sop, security, audit, vulnerability, api-key, compliance, threat-modeling, code-review, appsec]
trigger: 所有安全相关任务（安全审计/密钥轮转/异常检测/漏洞扫描）必须先加载此技能
---

# 墨安安全 Agent SOP 技能包

## 适用 Agent
- 墨安安全 (security.py)
- 集成：red-teaming, ag-vulnerability-scanner

---

## 一、Lead SOP（安全需求获取）

### 安全监控源

| 源 | 方式 | 频次 | 优先级 |
|------|------|------|--------|
| API 密钥状态 | 密钥有效期/使用量检查 | 每日 | P0 |
| 异常 API 调用 | 调用模式分析（频率/地域/时点） | 每小时 | P0 |
| 依赖项 CVE | 第三方依赖安全漏洞通报 | 每周 | P1 |
| 代码安全扫描 | 代码仓库安全扫描 | PR 提交时 | P1 |
| 系统日志异常 | 登录失败/权限异常 | 每小时 | P0 |

### 风险分级

| 级别 | 含义 | 响应时间 | 处理方式 |
|------|------|----------|----------|
| CRITICAL | 密钥泄露/数据泄露 | 立即 | 自动阻断 + 人工介入 |
| HIGH | 漏洞可利用/异常模式 | 1小时 | 自动修复或阻断 |
| MEDIUM | 潜在风险/配置不当 | 24小时 | 评估后修复 |
| LOW | 最佳实践偏离 | 7天 | 排入修复计划 |

---

## 二、Execution SOP（安全运营流程）

```
监控采集 → 异常分析 → 风险评估 → 处置行动 → 记录归档
```

### Step 1: API 密钥管理

密钥安全检查：
- 检查所有配置的 API Key 有效期
- 检查 Key 是否有异常地域访问
- 检查 Key 权限是否最小化
- 检查各 profile 是否使用独立 Key（不应共享同一 Key，否则无法追踪调用来源）
- 检查密钥文件最后修改时间（应 < 90 天，需轮换）
- 过期前 7 天预警

密钥轮转策略：
```yaml
github_token: 每90天轮转，降级为 Fine-grained token（仅 repo + workflow）
deepseek_api: 每90天轮转
openrouter_key: 每90天轮转
dashscope_api: 每90天轮转
feishu_app_secret: 每90天轮转
supermemory_api: 每90天轮转
feishu_webhook: 按需（泄露时即时轮转）
本地存储: 密钥仅存于 ~/.hermes/.env + ~/.hermes/profiles/*/.env（不上 Git）
```

密钥检查命令行参考：
```bash
# 检查密钥文件最后修改时间（macOS）
stat -f "%Sm" ~/.hermes/.env
stat -f "%Sm" ~/.hermes/profiles/*/.env

# 检查 GITHUB_TOKEN 权限范围
curl -sI -H "Authorization: token $(grep GITHUB_TOKEN ~/Molin-OS/.env | cut -d= -f2)" \
  https://api.github.com/ | grep -i x-oauth-scopes

# 检查 Git 历史中是否有密钥泄露
cd ~/Molin-OS && git log --all --name-only --format="%h %s" | grep -i '\.env\|secret\|credential'
cd ~/Molin-OS && git grep -n 'ghp_\|sk-\|sm_\|fc-\|api_key\|TOKEN=' HEAD -- ':!.env' ':!**/.env' ':!*.example'
```

### Step 2: 依赖 CVE 扫描

CVE 扫描流程：
1. 收集依赖文件：`requirements.txt`、`setup.py`、`pyproject.toml`、`package.json` 等
2. 检查已安装的 Python 依赖版本
3. 使用 pip-audit 自动化扫描（如果已安装）：
   ```bash
   pip-audit --requirement requirements.txt --desc
   ```
4. 若 pip-audit 不可用，记录当前版本并通过 web 搜索已知 CVE（重点关注 aiohttp, cryptography, requests, pillow 等关键包）
5. 仅报告 HIGH/CRITICAL 级别的 CVE（MEDIUM/LOW 按周排期）

注意事项：
- 检查 `python3 -m pip list --format=columns` 获取实际安装版本（不等同于 requirements.txt 中的版本范围）
- `pip-audit` 需手动安装：`pip3 install pip-audit`
- 若 pip-audit 因依赖解析失败（如 Python 版本不匹配），降级为人工检查最新版本

### Step 3: 系统安全审计

每周审计清单：
- [ ] API Key 未过期且未被滥用
- [ ] GitHub Token 权限未扩大（检查命令见参考文件）
- [ ] 密钥文件最后修改时间距当前 < 90 天（检查命令见参考文件）
- [ ] ~/.hermes/ 下无私密文件泄露
- [ ] .gitignore 覆盖敏感文件模式
- [ ] Git 历史中无密钥提交记录（检查命令见参考文件）
- [ ] 所有 Webhook URL 未暴露
- [ ] 飞书/企微 Bot Token 安全
- [ ] 各 profile 的 API Key 是否隔离（不应共享相同 Key）

### Step 4: 异常检测

检测规则：
- 同一 API Key 短时间高频调用（> 正常 3x）
- 非工作时间批量调用（00:00-06:00 密集调用）
- 非常用模型被调用（如闪调用 GPT-4 而非常用 DeepSeek）
- 未知 IP 来源访问

### Step 5: 报告输出

使用 `molib.memory.output_writer.write_agent_output()` 写入结构化报告：
```python
from molib.memory.output_writer import write_agent_output

write_agent_output(
    agent_id="security",
    output_type="active_audit",  # 或 daily_report / cve_scan
    goal="审计目标描述",
    summary="审计摘要（风险总览、关键发现）",
    analysis="详细分析（表格、证据）",
    actions="处置行动（按 CRITICAL/HIGH/MEDIUM/LOW 分级）",
    risks="风险与异常清单",
    learnings="可复用知识",
    relay_path=f"security/audit_{date_compact}.json",
)
```

同时写入 relay 标记文件：
- 路径：`relay/security/audit_{YYYYMMDD}.json`
- 包含 findings 数组（id, severity, title, recommendation, deadline）
- 供上游 KPI 看板消费

Obsidian 输出路径（由 output_writer 自动处理）：
- 物理路径：`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/产出/玄骨｜{output_type}·{date}.md`
- 这是正确的 iCloud Obsidian vault 路径

### Step 6: 处置行动

| 异常类型 | 动作 |
|----------|------|
| 密钥疑似泄露 | 立即轮转 + 审计调用记录 |
| 异常 API 调用模式 | 降级限流 + 告警 |
| CVE 高危漏洞 | 更新依赖 + 检查受影响范围 |
| 代码安全漏洞 | 阻止 PR 合并 + 通知开发者 |

---

## 三、QA SOP（安全质量质检）

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 覆盖全面性 | 25% | 所有安全维度是否覆盖？ |
| 发现准确率 | 25% | 告警中误报率是否 < 30%？ |
| 响应时效 | 25% | CRITICAL 是否立即响应？ |
| 修复闭环 | 25% | 发现的问题是否全部修复？ |

---

## 四、Escalation SOP

| 场景 | 触发 | 动作 |
|------|------|------|
| 密钥泄露确认 | 发现未授权访问 | L3 董事会：立即轮转 + 全面审计 |
| 数据泄露风险 | 敏感文件被访问 | L3 董事会：封锁 + 通知 |
| 持续攻击 | 异常模式持续 > 1小时 | L2 审批：临时停服或降级 |

---

## 五、Cron 经营节奏

| 时间 | 任务 | 产出 |
|------|------|------|
| 每日 06:00 | API 密钥检查 + 异常调用分析 | 安全日报 |
| 每小时 | 调用模式异常检测 | 告警（如有） |
| 每周一 | 系统安全审计 | 审计报告 |
| PR 提交时 | 代码安全扫描 | 扫描结果 |

---

## 六、应用安全工程（吸收自 Agency Security Engineer）

> 源：Agency Agents Security Engineer · 吸收日期：2026-05-18

本节覆盖应用安全工程全生命周期，补充原有运维安全（密钥/CVE/审计）以形成完整安全体系。

### 对抗性思维框架

审查任何系统时始终追问：
1. **什么可被滥用？** — 每个功能都是攻击面
2. **失败时会发生什么？** — 假设每个组件都会失败；设计优雅、安全的失败模式
3. **谁会从中获益？** — 理解攻击者动机以优先防守
4. **爆炸半径多大？** — 被攻陷的组件不应拖垮整个系统

### 严重性评级标准

| 级别 | 定义 | 示例 |
|------|------|------|
| **Critical** | RCE、认证绕过、可访问数据的 SQL 注入 | 未认证的 SSTI 导致服务器接管 |
| **High** | 存储型 XSS、敏感数据 IDOR、权限提升 | 通过 IDOR 访问其他用户文档 |
| **Medium** | CSRF、缺失安全头、详细错误信息 | 状态变更操作无 CSRF 防护 |
| **Low** | 非敏感页点击劫持、轻微信息泄露 | 未设置 X-Frame-Options |
| **Informational** | 最佳实践偏离、纵深防御改进 | 缺少 CSP 但无直接利用路径 |

### 漏洞评估方法

**Web 应用测试清单**：
- 注入：SQLi、NoSQLi、命令注入、模板注入（SSTI）
- XSS：反射型、存储型、DOM 型
- CSRF、SSRF、认证/授权缺陷
- 批量赋值、IDOR、业务逻辑缺陷（竞态条件 TOCTOU）

**API 安全测试**（OWASP API Security Top 10）：
- 失效的认证、BOLA（对象级授权）、BFLA（功能级授权）
- 过度数据暴露、速率限制绕过
- GraphQL 内省/批量攻击、WebSocket 劫持

**云安全态势**：
- IAM 过度授权检测
- 公开存储桶检查
- 网络分段审查
- 环境变量中的密钥检测

### 安全架构设计

**纵深防御层次**：
```
WAF → 速率限制 → 输入验证 → 参数化查询 → 输出编码 → CSP
```

**核心原则**：
- 零信任架构 + 最小权限访问控制
- 身份认证：OAuth 2.0 + PKCE、OpenID Connect、Passkeys/WebAuthn、MFA
- 授权模型：RBAC / ABAC / ReBAC — 匹配应用需求
- 密钥管理：HashiCorp Vault / AWS Secrets Manager / SOPS，含轮转策略
- 加密：TLS 1.3（传输）、AES-256-GCM（静态）、正确密钥管理
- 默认拒绝：白名单优于黑名单
- 安全失败：错误不泄露堆栈跟踪、内部路径、数据库模式

### CI/CD 安全流水线

```yaml
# 安全扫描流水线（PR 触发）
jobs:
  sast:        # Semgrep: OWASP Top 10 + CWE Top 25
  dependency-scan:  # Trivy: CRITICAL/HIGH 阻断
  secrets-scan:     # Gitleaks: 全量历史扫描
```

**强制门禁**：
- SAST 发现 HIGH+ → 阻断合并
- 依赖 CVE CRITICAL/HIGH → 阻断合并
- 密钥泄露检测 → 阻断合并 + 立即轮转

### 供应链安全

- 审计第三方依赖已知 CVE 和维护状态
- 生成和监控 SBOM（软件物料清单）
- 验证包完整性（校验和、签名、锁文件）
- 防范依赖混淆和拼写欺骗攻击
- 锁定依赖版本，使用可复现构建

### AI/LLM 应用安全

- **Prompt 注入**：直接和间接注入检测与缓解
- **模型输出验证**：防止敏感数据通过响应泄露
- **API 安全**：速率限制、输入净化、输出过滤
- **护栏**：输入/输出内容过滤、PII 检测和脱敏

### 安全测试覆盖清单

| 类别 | 测试项 |
|------|--------|
| **认证** | 缺失 token、过期 token、算法混淆、错误签发者/受众 |
| **授权** | IDOR、权限提升、批量赋值、水平越权 |
| **输入验证** | 边界值、特殊字符、超大载荷、非预期字段 |
| **注入** | SQLi、XSS、命令注入、SSRF、路径遍历、模板注入 |
| **安全头** | CSP、HSTS、X-Content-Type-Options、X-Frame-Options |
| **速率限制** | 登录/敏感端点暴力破解防护 |
| **错误处理** | 无堆栈跟踪、通用认证错误、生产环境无调试端点 |
| **会话安全** | Cookie 标记（HttpOnly、Secure、SameSite）、登出失效 |
| **业务逻辑** | 竞态条件、负值、价格操纵、流程绕过 |
| **文件上传** | 可执行文件拒绝、魔术字节验证、大小限制、文件名净化 |

### 事件响应

- 安全事件分类、遏制和根因分析
- 日志分析和攻击模式识别
- 事后修复和加固建议
- 泄露影响评估和遏制策略

---

## 七、安全工程工作流

### 阶段 1：侦察与威胁建模
1. 映射架构：阅读代码、配置和基础设施定义
2. 识别数据流：敏感数据在何处进入、流转、离开系统
3. 编目信任边界：控制权在组件/用户/权限级别间转换的位置
4. 执行 STRIDE 分析：按威胁类别系统评估每个组件
5. 风险排序：结合利用难度（可能性）与影响（损失）

### 阶段 2：安全评估
1. 代码审查：认证、授权、输入处理、数据访问、错误处理
2. 依赖审计：CVE 数据库检查 + 维护健康度评估
3. 配置审查：安全头、CORS、TLS、云 IAM 策略
4. 认证测试：JWT 验证、会话管理、密码策略、MFA
5. 授权测试：IDOR、权限提升、角色边界、API 范围
6. 基础设施审查：容器安全、网络策略、密钥管理、备份加密

### 阶段 3：修复与加固
1. 优先级报告：Critical/High 优先，含具体代码 diff
2. 安全头与 CSP：部署硬化头 + nonce-based CSP
3. 输入验证层：在每个信任边界添加/加强验证
4. CI/CD 安全门禁：集成 SAST、SCA、密钥检测、容器扫描
5. 监控与告警：为识别出的攻击向量设置安全事件检测

### 阶段 4：验证与回归
1. 先写安全测试：每个发现——先写一个展示漏洞的失败测试
2. 验证修复：重测每个发现以确认修复有效
3. 回归测试：确保安全测试在每个 PR 运行，失败时阻断合并
4. 追踪指标：按严重性的发现数量、修复时间、漏洞类别测试覆盖率

---

## 八、参考

- API 密钥配置：`~/.hermes/config.yaml`
- 安全审计实际命令速查：`references/audit-command-cookbook.md`
- 密钥轮转记录：`supermemory_search("API密钥轮转记录")`
- 已知 CVE：`supermemory_search("依赖安全漏洞")`
- 安全异常历史：`supermemory_search("安全事件记录")`
- 结构化报告工具：`molib.memory.output_writer.write_agent_output()`
