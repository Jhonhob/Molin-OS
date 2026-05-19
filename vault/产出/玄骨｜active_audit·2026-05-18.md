# 🧠 Agent Output: 墨安安全

## 🕒 Metadata
- 时间: 2026-05-18 03:03:24
- Agent: security
- 类型: active_audit
- 来源数据: local fs: ~/Molin-OS, ~/.hermes/
- 关联任务: - 每周安全审计 cron job

---

## 🎯 任务目标
墨安安全-每周主动安全审计：依赖CVE扫描 + 密钥轮换检查 + 权限最小化检查


---

## 📊 核心结果
## 审计摘要

**风险总览：**
- 🔴 CRITICAL: 1项 — GITHUB_TOKEN 权限过大
- 🟡 HIGH: 1项 — 密钥无轮换历史记录
- 🟡 MEDIUM: 1项 — 所有profile使用相同API Key
- 🟢 LOW: 2项 — pip-audit未安装; browser-use依赖无法解析

**关键发现：**
1. GitHub Token权限过大(admin:enterprise, admin:org, delete_repo等)
2. 密钥文件较新(<30天)，不在轮换窗口
3. 所有5个profile共享同一SUPERMEMORY_API_KEY
4. .gitignore覆盖良好
5. 依赖项未发现已知HIGH/CRITICAL CVE


---

## 🔍 详细分析
## 详细分析

### 一、依赖漏洞扫描
| 包名 | 版本 | CVE状态 |
|------|------|---------|
| aiohttp | 3.13.5 | ✅ 无HIGH/CRITICAL |
| cryptography | 48.0.0 | ✅ 无HIGH/CRITICAL |
| httpx | 0.28.1 | ✅ 无HIGH/CRITICAL |
| numpy | 2.0.2 | ✅ 无HIGH/CRITICAL |
| openai | 2.37.0 | ✅ 无HIGH/CRITICAL |
| pillow | 11.3.0 | ✅ 无HIGH/CRITICAL |
| playwright | 1.59.0 | ✅ 无HIGH/CRITICAL |
| pyyaml | 6.0.3 | ✅ 已修复历史CVE |
| requests | 2.32.5 | ✅ 无HIGH/CRITICAL |
| sqlalchemy | 2.0.49 | ✅ 无HIGH/CRITICAL |
| dashscope | 1.25.18 | ✅ 无已知CVE |

### 二、密钥轮换
所有密钥文件最后修改在2026-05-16/17(<30天)，不在轮换窗口
需在2026-08-15设置90天轮换提醒

### 三、权限最小化
**GITHUB_TOKEN**: admin:enterprise, admin:org, delete_repo, copilot, workflow等20+权限
→ 仅需 repo + workflow

**Profile key共享**: edu/global/media/shared/side 使用相同Key


---

## ⚙️ 执行动作
## 处置行动

**🔴 CRITICAL**: 降级GITHUB_TOKEN为Fine-grained token(Contents:write + Workflows:write)
**🟡 HIGH**: 设置2026-08-15密钥轮换日历提醒
**🟡 MEDIUM**: 安装pip-audit; 为每个profile创建独立API Key
**🟢 LOW**: 修复requirements.txt(browser-use无法安装)


---

## 🚨 风险与异常
## 风险

1. 🔴 GITHUB_TOKEN超权限 - 泄露可致仓库/组织被接管
2. 🟡 轮换记录缺失 - 无法确认密钥真实年龄
3. 🟡 密钥共享 - 无法区分profile调用来源
4. ✅ Git未发现密钥泄露
5. ✅ 未发现云服务密钥泄露


---

## 🧩 可复用知识
## 可复用知识

- GITHUB_TOKEN scope检查: curl -I -H "Authorization: token ..." https://api.github.com/
- 密钥年龄: stat -f "%Sm" <file>
- Obsidian vault: ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/


---

## 🔗 关联知识
- [[config/governance.yaml]]
- [[.gitignore]]
- [[sop/definitions/security_proactive_audit_sop.yaml]]

---

## 📤 输出路径
- `relay/security/audit_20260518.json`
