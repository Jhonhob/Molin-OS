# Vault 硬化方法论 — 全量排查 → 根因封堵 → 防复发

> 从 2026-05-17 的 v3.0 vault 硬化实战中提炼的可重复方法论。
> 适用场景：vault 反复出现不合规文件/目录、旧路径幽灵复活、命名规范不统一。

## 五阶段流程

### Phase 1: 全量审计（不只是用户指出的那几个）

```bash
VAULT="/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents"

# 1. 目录审计 — 必须恰好 8 个
find "$VAULT" -mindepth 1 -maxdepth 1 -type d ! -name '.git' ! -name '.obsidian' ! -name '.trash'

# 2. 文件命名审计 — 所有 .md 必须含 ｜
find "$VAULT" -maxdepth 2 -name '*.md' ! -path '*/.git/*' | while read f; do
  bn=$(basename "$f")
  [[ "$bn" != *｜* ]] && echo "NO PIPE: ${f#$VAULT/}"
done

# 3. 旧路径模式扫描
for pat in 'MolinOS-Wiki' 'agent-outputs' '02_Agent_Outputs' 'Agents/' 'System/' 'Daily/'; do
  echo "=== $pat ==="
  grep -rn "$pat" "$VAULT" --include='*.md' | grep -v '.git/' | grep -v '已废弃\|已消灭\|v3.0\|迁移\|历史记录'
done
```

### Phase 2: 根因溯源（四层扫描）

每个不合规文件追查其写入源：

```bash
HOME="/Users/laomo"

# 层1: Molin-OS 核心代码
grep -rn 'OLD_PATH' "$HOME/Molin-OS"/{scripts,molib,tools} --include='*.py' --include='*.sh'

# 层2: Hermes 技能
grep -rn 'OLD_PATH' "$HOME/.hermes/skills" --include='*.md'

# 层3: Agent Profile（关键！最常被遗漏）
for agent in edu shared side media global; do
  echo "=== $agent ==="
  grep -rn 'OLD_PATH' "$HOME/.hermes/profiles/$agent"/{skills,scripts,memories,plans,bin} 2>/dev/null
done

# 层4: 系统文档
grep -rn 'OLD_PATH' "$HOME/Molin-OS/SYSTEM.md" "$HOME/Molin-OS/产出写入规范.md"
```

### Phase 3: 源头封堵（一次性全部修复）

按优先级：
1. **活跃代码**（Python/Shell 脚本中的写入路径）— 最高优
2. **活跃技能**（SKILL.md 中指导 Agent 写入的路径）— 次高优
3. **Agent 记忆**（MEMORY.md 中记录的路径偏好）— 中优
4. **历史文档**（审计报告/参考文档中的提及）— 低优（只读，可保留但加标注）

修复模式：
- `MolinOS-Wiki` → iCloud vault 绝对路径
- `产出/{agent_id}/{date}.md` → `产出/业务线｜{type}·{date}.md`
- `agent-outputs/` → 物理删除目录
- `02_Agent_Outputs/` → 物理删除目录
- `学习档案/{agent}/github-absorb/` → `学习档案/业务线｜{topic}·{date}.md`

### Phase 4: 防复发护栏

1. **vault_health_check.py** — 检查子目录 + 命名 + 无效目录
2. **产出写入规范.md** — 单一线人真源，含禁止路径列表
3. **output_writer.py** — 强制走业务线前缀映射，物理上不可能创建 agent_id 子目录
4. **记忆固化** — 禁止路径写入 memory，后续 Agent 不会习得旧路径

### Phase 5: 全域验证归零

```bash
# 最终扫描 — 应返回 0 活跃命中
for pat in 'MolinOS-Wiki' '02_Agent_Outputs' '产出/edu/' '产出/side/' '产出/media/' '产出/shared/' 'agent-outputs/'; do
  grep -rn --include='*.py' --include='*.sh' --include='*.yaml' --include='*.md' "$pat" \
    "$HOME/Molin-OS"/{molib,tools,scripts} \
    "$HOME/.hermes/skills" \
    "$HOME/.hermes/profiles/"{edu,shared,side,media,global}"/"{skills,scripts,bin} \
    2>/dev/null \
    | grep -v 'references/' | grep -v 'session_' | grep -v 'deprecated' | grep -v 'v3.0 flat'
done
```

## 关键教训

### 教训1: 用户指出的3个文件只是冰山一角
本次会话：用户指出3个不合规文件 → 全量审计发现 3个无效目录 + 9个不合规文件 + 13个活跃写入源。

### 教训2: 剖面脚本是最常被遗漏的第四层
三层审计（Molin-OS 脚本 + Hermes 技能 + Agent 技能）不够 → `shared/bin/memory_sync.py` 和 `side/scripts/memory_sync.py` 属于第四层（profile bin/scripts），之前的审计都漏了它们。

### 教训3: 文件名冲突在 v3.0 中合法
跨目录同名（`决策/系统｜GitHub.md` + `成果/系统｜GitHub.md`）在 v3.0 flat vault 中是正常的 — 目录即命名空间。vault_health_check.py 的跨目录同名重复检测已移除。

### 教训4: 修一个漏一个是常见反模式
第一次修复只改了 `output_writer.py` 和 `memory_bridge.py` → 再扫描又发现 `side/memory_sync.py` 和 `shared/bin/memory_sync.py` → 再扫描又发现 `start_all.sh` 和 `sync_memory_edu.py` → 再扫描又发现 5个 SKILL 文件。正确做法是一次性全量扫描后批量修复。
