# Vault 全线硬化方法论 · 2026-05-18

## 背景

2026-05-17 v3.0 vault 硬化完成后，用户发现 `产出/edu/` 和 `产出/shared/` 仍然存在。根因分析揭示：之前的审计遗漏了第四层写入源（`~/.hermes/scripts/` 全局脚本目录），且 `~/MolinOS-Wiki` symlink 在后台将所有旧路径引用静默重定向到 iCloud vault，导致 ghost 目录复活。

## 五层写入源全量审计法

以前的审计覆盖三层（Molin-OS 脚本 + Hermes 技能 + Agent 技能），遗漏了：

| 层 | 路径 | 本session发现 |
|---|------|-------------|
| 1 | `~/Molin-OS/scripts/` | sync_memory.py (backbone管道引擎) |
| 2 | `~/.hermes/skills/` | molin-memory-pipeline 等 |
| 3 | `~/.hermes/profiles/{agent}/skills/` | agent-profile 技能 |
| **4** | **`~/.hermes/scripts/`** | **relay_to_obsidian.py, sync_memory_edu.py, sync_growth_full.py, molin-sync-all.sh** |
| **5** | **Symlink 静默重定向** | **`~/MolinOS-Wiki → iCloud vault`** |

## 五阶段硬化流程

### Phase 0: 全面扫描
```bash
# 必须覆盖所有5层
for pattern in 'MolinOS-Wiki' 'agent-outputs' '产出/edu' '产出/shared' 'Daily/' '02_Agent_Outputs' '知识/每日·'; do
  echo "=== $pattern ==="
  grep -rn "$pattern" \
    ~/.hermes/scripts/ \
    ~/.hermes/profiles/*/scripts/ \
    ~/.hermes/profiles/*/bin/ \
    ~/Molin-OS/scripts/ \
    ~/.hermes/skills/ \
    --include='*.py' --include='*.sh' --include='*.md' \
    2>/dev/null | grep -v '.json:' | grep -v '__pycache__' | grep -v '.git/'
done
```

### Phase 1: 删除 symlink（根因封堵）
```bash
rm ~/MolinOS-Wiki
```
不删 symlink，任何残留旧路径引用都会静默写入 vault，无法被检测到。

### Phase 2: 逐个修复写入源
- 路径变量：`MolinOS-Wiki` → iCloud 绝对路径
- 子目录：`产出/edu/` → `产出/元瑶｜`
- 文件名：`每日·xxx.md` → `玄骨｜每日·xxx.md`
- 管道引擎：添加 `BIZ_PREFIX` 映射 + `业务线｜topic.md`

### Phase 3: 禁用无法升级的旧脚本
不可简单修复的旧脚本（如 `obsidian_sync.py`, `vault_compliance_check.py`）→ rename to `.disabled_*`。

### Phase 4: 清理 vault 垃圾
- 删除子目录（`产出/edu/`, `产出/shared/`, `Daily/`）
- 删除垃圾文件（prompt碎片、截断文件名）
- 重命名无 `｜` 前缀的文件

### Phase 5: 验证 + 防复发
```bash
python3 ~/Molin-OS/scripts/vault_health_check.py
# 检查：8目录、0子目录、0无｜文件、0旧路径引用
```

## 本 session 修复清单

| # | 文件 | 修复 |
|---|------|------|
| 1 | `~/MolinOS-Wiki` symlink | 删除 |
| 2 | `~/Molin-OS/scripts/sync_memory.py` | 添加 BIZ_PREFIX + `业务线｜topic.md` |
| 3 | `~/.hermes/scripts/relay_to_obsidian.py` | `每日·` → `玄骨｜每日·` |
| 4 | `~/Molin-OS/scripts/relay_to_obsidian.py` | 同上（双副本！） |
| 5 | `~/.hermes/scripts/sync_memory_edu.py` | `MolinOS-Wiki/agent-outputs/` → iCloud + `元瑶｜` |
| 6 | `~/.hermes/scripts/moling-sync-all.sh` | 禁用 obsidian_sync 步骤 |
| 7 | `~/.hermes/profiles/edu/scripts/sync_memory.py` | `MolinOS-Wiki/产出/edu/` → iCloud + `元瑶｜` |
| 8 | `~/.hermes/profiles/edu/scripts/sync_growth_full.py` | `MolinOS-Wiki/产出/edu/` → iCloud |
| 9 | `~/.hermes/profiles/media/scripts/sync_memory.py` | `MolinOS-Wiki/银月/` → iCloud + `银月｜` |
| 10 | `~/Molin-OS/scripts/vault_compliance_check.py` | 禁用（写 Daily/） |
| 11 | `~/Molin-OS/scripts/obsidian_sync.py` | 禁用（写 Daily/） |

## 关键教训

1. **Symlink 是静默杀手**：只要 `MolinOS-Wiki` symlink 存在，任何残留旧路径都会继续污染 vault
2. **双副本陷阱**：`relay_to_obsidian.py` 存在于两个位置（`~/.hermes/scripts/` 和 `~/Molin-OS/scripts/`），修一个漏一个
3. **全量扫描 > 逐个排查**：第一轮修 output_writer + memory_bridge，再扫描发现 side/shared sync，再扫描发现 start_all/sync_edu，再扫描发现 5个 SKILL。一次性全量扫描 + 批量修复才是正确做法
4. **Cron 输出是活证据**：`hermes cron list` 的 stdout 直接暴露了哪些脚本在写什么路径，比静态 grep 更准确
