# Vault Blueprint — Directory Tree Reference (v4)

```
Vault/ (iCloud)
├── Agents/
│   ├── media/          (银月传媒 — 全媒体内容)
│   │   ├── 决策/       ← CloakServe集成.md, 小红书适配器方案.md
│   │   ├── 知识/       ← SourceAdapter架构设计.md, 内容情报管线设计.md
│   │   ├── 流程/       ← 封面生成SOP.md, Agent-README.md, Skills-Map.md
│   │   └── 成果/       ← 百炼生图测试报告.md
│   ├── edu/            (元瑶教育 — 在线教育)
│   │   ├── 决策/       ← (empty)
│   │   ├── 知识/       ← 在线教育GitHub项目研究.md
│   │   ├── 流程/       ← Agent-README.md, Skills-Map.md, Toolchain.md
│   │   └── 成果/       ← (empty)
│   ├── global/         (梅凝出海 — 跨境电商)
│   │   ├── 决策/       ← 跨境电商运营.md
│   │   ├── 知识/       ← 跨境电商知识沉淀.md
│   │   ├── 流程/       ← Agent-README.md, Skills-Map.md, Toolchain.md, 环境配置.md
│   │   └── 成果/       ← (empty)
│   ├── shared/         (玄骨中枢 — 系统基建)
│   │   ├── 决策/       ← 系统部署方案.md
│   │   ├── 知识/       ← 研究沉淀.md, 运维经验沉淀.md
│   │   ├── 流程/       ← Agent-README.md, Skills-Map.md, Toolchain.md, 快速参考.md
│   │   └── 成果/       ← GitHubTrending日报_20260515.md, GitHubTrending深度日报_20260515.md
│   └── side/           (宋玉创业 — 创业探索)
│       ├── 决策/       ← 创业调研日志.md
│       ├── 知识/       ← 创业知识沉淀.md
│       ├── 流程/       ← Agent-README.md, Skills-Map.md, Toolchain.md, 创业调研流程.md
│       └── 成果/       ← (empty)
├── Daily/
│   └── 2026-05-15.md   ← Single aggregated daily file (not per-agent)
├── System/
│   ├── architecture.md
│   ├── memory-map.md
│   ├── README.md
│   ├── 知识库重构方案.md
│   ├── 执行规范v4.md
│   └── agents/
│       ├── edu.md
│       ├── global.md
│       ├── media.md
│       ├── shared.md
│       └── side.md
├── Archive/             ← Old v2/v3 structure backups (read-only)
│   ├── 旧结构备份/      ← ⚙️系统与配置 dirs
│   └── archives-v2_*/   ← Old 6-category archives per agent
```

Total: 5 agents × 4 categories = 20 category dirs + Daily/ (1 file) + System/ (9 items) + Archive/ = manageable.

## Migration Path (for reference)

| Version | Categories | Status | 
|---------|-----------|--------|
| v1 | 8 form-based | Archived |
| v2 | 6 emoji domain-based | Archived (moved to Archive/) |
| v3 | 4 business-category (项目/知识库/产出/对话记录) | Read-only legacy (files remain in place) |
| **v4 (current)** | **4 MECE (决策/知识/流程/成果)** | **Active — write new content here** |
