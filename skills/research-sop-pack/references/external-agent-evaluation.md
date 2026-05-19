# 外部 Agent 仓库评估方法论

> 适用场景：用户要求评估 GitHub 上的 AI Agent 定义仓库对墨麟OS的补强价值。

## 评估框架

### 1. 仓库元数据分析

通过 `raw.githubusercontent.com` 获取：
- README.md：Agent 清单、目录结构、使用方法
- GitHub API `/repos/{owner}/{repo}`：Stars、Topics、活跃度
- GitHub API `/contents/`：完整文件树

网络策略：
1. **首选**：`raw.githubusercontent.com` — 直读文件，无需认证，限速宽松
2. **次选**：`api.github.com/repos/{repo}/readme` — 需要 Accept header
3. **降级**：`api.github.com/search/repositories` — 搜索替代
4. **兜底**：`github.com/{repo}` 浏览器渲染（最慢，限静态分析）

### 2. Agent 定义结构识别

每个外部 Agent 定义文件通常包含以下模块：

| 模块 | 典型标题 | 可吸收性 |
|------|---------|---------|
| 身份定义 | `## Identity`, `## Role Definition` | 🟡 低（人格不可移植） |
| 核心使命 | `## Core Mission`, `## Purpose` | 🟢 高（职责可作为 Skill 描述） |
| 工作流程 | `## Workflow`, `## Process`, `### Phase N` | 🔴 核心（直接补强 SOP 步骤） |
| 交付物规范 | `## Deliverables`, `## Output` | 🔴 核心（质量标准 + 格式模板） |
| 成功指标 | `## Success Metrics` | 🟢 高（可量化的验收标准） |
| 工具列表 | `tools: [...]` (frontmatter) | 🟡 中（替换为墨麟等效工具） |
| 人格/沟通风格 | `## Personality`, `## Communication` | ⚫ 低（各 Agent 自有风格） |

### 3. 匹配度评分矩阵

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| 领域匹配 | 35% | Agent 领域是否与墨麟子公司核心业务一致 |
| 流程补缺 | 30% | 工作流步骤是否填补现有 SKILL.md 的空白 |
| 标准先进性 | 20% | 交付物/质量标准的严格程度是否高于现有 |
| 可移植性 | 15% | 内容是否可直接转换为墨麟 SOP（语言/工具/平台独立） |

总分 ≥ 80 → Tier 1（立即吸收）
总分 65-79 → Tier 2（当周吸收）
总分 50-64 → Tier 3（择机吸收）
总分 < 50 → Skip

### 4. 吸收执行清单

```
□ 读取外部 Agent 源文件到工作内存
□ 提取 Identity / Mission / Workflow / Deliverables / Metrics
□ 在 vault 知识/ 下创建评估报告（系统｜{仓库名}评估·{date}.md）
□ 对每个 Tier 1/2 Agent：
  □ 定位匹配的墨麟子公司 + 现有 SKILL.md
  □ diff 对比：标记「新增」「增强」「替代」
  □ 翻译流程步骤为中文 SOP
  □ 替换外部工具引用为墨麟等效工具
  □ 注入 v3.0 vault 路径约束
  □ skill_manage action=patch 合并到目标 SKILL.md
□ 验证：gatekeeper-sop 质量门控
```

### 5. 常见陷阱

| 陷阱 | 规避 |
|------|------|
| 全量照搬，导致 SOP 臃肿 | 只取Δ（增量）—— 补缺不覆盖 |
| 保留英文人格描述 | 翻译为中文，适配墨麟 Agent 语气 |
| 引用外部工具（Google Trends 等） | 替换为国内等效工具（百度指数/新榜/5118） |
| 忽略路径兼容性 | 所有 Obsidian 路径必须符合 v3.0 flat vault |
| 一次性吸收过多 | 单次会话最多吸收 3 个，保持 SOP 精简 |

### 6. 案例：agency-agents 评估

**仓库**：`msitarzewski/agency-agents`
**规模**：140+ Agent，19 事业部，MIT 协议
**评估结果**：Tier 1 (8个) + Tier 2 (10个) + Tier 3 (4个) + Skip (~118个)

Tier 1 示例映射：
- `Private Domain Operator` → 墨域私域（95% 匹配，309 行完整 SOP）
- `Xiaohongshu Specialist` → 银月传媒（95% 匹配，品牌定位→微内容→算法→UGC）
- `Trend Researcher` → 墨研竞情（95% 匹配，弱信号→跨行业模式→创新评分）
- `Reality Checker` → 门禁Agent（95% 匹配，默认拒绝哲学，三维度审计）

详见 vault：`知识/系统｜TheAgency仓库评估·20260517.md`
