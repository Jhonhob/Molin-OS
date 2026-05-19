#!/usr/bin/env python3
"""墨麟OS 系统架构采集器 — 将系统架构信息同步到 Obsidian"""

from __future__ import annotations
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

HOME = Path.home()
BEIJING_TZ = timezone(timedelta(hours=8))
NOW = datetime.now(BEIJING_TZ)

# ═══════════════════════════════════════════════
# 路径配置
# ═══════════════════════════════════════════════

VAULT = Path(
    os.environ.get(
        "OBSIDIAN_VAULT_PATH",
        f"{HOME}/Library/Mobile Documents/iCloud~md~obsidian/Documents",
    )
)
HERMES_HOME = HOME / ".hermes"
MOLIN_OS = HOME / "Molin-OS"
HERMES_OS = HOME / "hermes-os"

AGENTS = {
    "edu": {
        "name": "元瑶教育",
        "desc": "教育内容、课程设计、学习辅导",
        "supertag": "edu",
        "feishu_app_id": "cli_a956c83187395cd4",
        "workers": ["education.py"],
        "common_commands": [
            "python -m molib content write --topic 课程 --platform edu",
        ],
    },
    "global": {
        "name": "梅凝出海",
        "desc": "海外市场本地化运营、跨境营销",
        "supertag": "molin-global",
        "feishu_app_id": "cli_aa881c316d789bb5",
        "workers": ["global_marketing.py"],
        "common_commands": [
            "python -m molib content write --topic 出海 --platform global",
        ],
    },
    "media": {
        "name": "银月传媒",
        "desc": "全媒体内容创作、社交媒体运营、视频音频",
        "supertag": "molin-media",
        "feishu_app_id": "cli_a966ede1d9789bd2",
        "workers": ["content_writer.py", "designer.py", "short_video.py", "voice_actor.py"],
        "common_commands": [
            "python -m molib content write --topic 内容 --platform media",
            "python -m molib design image --prompt ...",
            "python -m molib video script --topic ...",
        ],
    },
    "shared": {
        "name": "玄骨中枢",
        "desc": "CRM客户管理、运维部署、财务记账、数据分析",
        "supertag": "molin-shared",
        "feishu_app_id": "cli_aa884b4a88bc9bb4",
        "workers": ["crm.py", "customer_service.py", "ops.py", "finance.py", "data_analyst.py", "ecommerce.py"],
        "common_commands": [
            "python -m molib crm segment ...",
            "python -m molib finance record ...",
            "python -m molib order list ...",
        ],
    },
    "side": {
        "name": "宋玉创业",
        "desc": "创业项目、副业探索、市场调研",
        "supertag": "molin-side",
        "feishu_app_id": "cli_a9513691d4f89bcf",
        "workers": [],
        "common_commands": [],
    },
}


# ═══════════════════════════════════════════════
# 数据采集
# ═══════════════════════════════════════════════


def read_file_safe(path: Path) -> str:
    try:
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        pass
    return ""


def collect_agent_configs() -> dict[str, dict]:
    """采集所有 agent 的配置"""
    result = {}
    for agent_id, info in AGENTS.items():
        profile_dir = HERMES_HOME / "profiles" / agent_id

        # config.yaml
        config_text = read_file_safe(profile_dir / "config.yaml")


        # .env
        env_text = read_file_safe(profile_dir / ".env")
        env_vars = {}
        for line in env_text.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip()[:30] + "..." if len(v.strip()) > 30 else v.strip()

        result[agent_id] = {
            "name": info["name"],
            "desc": info["desc"],
            "config_yaml": config_text,
            "env_vars": env_vars,
            "workers": info["workers"],
            "feishu_app_id": info["feishu_app_id"],
            "supertag": info["supertag"],
            "entity_context": sm_config.get("entity_context", "")[:200],
        }
    return result


def collect_system_info() -> dict:
    """采集系统级信息"""
    agents_md = ""
    soul_md = ""

    for path in [MOLIN_OS / "AGENTS.md", HERMES_OS / "AGENTS.md"]:
        text = read_file_safe(path)
        if text:
            agents_md += f"\n--- from {path.name} ---\n{text[:5000]}"

    for path in [MOLIN_OS / "SOUL.md", HERMES_OS / "SOUL.md"]:
        text = read_file_safe(path)
        if text:
            soul_md += f"\n--- from {path.name} ---\n{text[:5000]}"

    return {
        "agents_md": agents_md,
        "soul_md": soul_md,
        "hermes_config": read_file_safe(HERMES_HOME / "config.yaml"),
    }


def collect_vault_state() -> dict:
    """采集当前 vault 的结构状态（扁平分类）"""
    vault_data = {}
    if VAULT.exists():
        for cat_dir in VAULT.glob('*'):
            if cat_dir.is_dir() and cat_dir.name in ('决策','知识','流程','成果','报告','配置'):
                cat = cat_dir.name
                files = list(cat_dir.glob('*.md'))
                vault_data[cat] = len(files)
    return vault_data
    return vault_data


# ═══════════════════════════════════════════════
# Obsidian 输出
# ═══════════════════════════════════════════════


def write_obsidian_architecture(agents_data: dict, sys_info: dict, vault_state: dict):
    """写入系统架构总览"""
    sys_dir = VAULT / "配置"
    sys_dir.mkdir(parents=True, exist_ok=True)

    # ── 主架构文档 ──
    lines = [
        "---",
        f"date: {NOW.strftime('%Y-%m-%d')}",
        "agent: system",
        "category: architecture",
        "category_name: 系统架构",
        "tags: [system, architecture, auto-sync]",
        "source: 架构采集器",
        "---",
        "",
        f"# 墨麟AI集团 · 系统架构 ({NOW.strftime('%Y-%m-%d %H:%M')})",
        "",
        f"_自动采集时间: {NOW.strftime('%Y-%m-%d %H:%M:%S %Z')}_",
        "",
    ]

    # Agent 总览表
    lines += [
        "## Agent 总览",
        "",
        "| Agent | 名称 | 容器 | 飞书 App | 关联 Workers |",
        "|-------|------|-----------------|----------|-------------|",
    ]
    for agent_id, ad in agents_data.items():
        lines.append(
            f"| {agent_id} | {ad['name']} | `{ad['supertag']}` | {ad['feishu_app_id']} | {', '.join(ad['workers']) or '—'} |"
        )
    lines += ["", ""]

    # 每个 Agent 详情
    for agent_id, ad in agents_data.items():
        lines += [
            f"## {ad['name']} (`{agent_id}`)",
            "",
            f"- **描述**: {ad['desc']}",
            f"- **容器**: `{ad['supertag']}`",
            f"- **飞书 App ID**: `{ad['feishu_app_id']}`",
            f"- **关联 Workers**: {', '.join(ad['workers']) or '无'}",
        ]
        if ad["entity_context"]:
            lines += [f"- **记忆上下文**: {ad['entity_context']}"]
        lines += ["", ""]

    # Vault 状态
    lines += [
        "## Vault 同步状态",
        "",
        "| Agent | 分类 | 文件数 |",
        "|-------|------|-------|",
    ]
    for agent, cats in vault_state.items():
        for cat, count in cats.items():
            lines.append(f"| {agent} | {cat} | {count} |")
    if not vault_state:
        lines.append("| — | 暂无同步文件 | 0 |")
    lines += ["", ""]

    # 记忆系统架构
    lines += [
        "## 记忆系统架构",
        "",
        "```",
        "每个 Agent 拥有独立 容器（container_tag）",
        "记忆自动写入 → Obsidian vault（Markdown 全文检索）",
        "定时同步 → Obsidian iCloud Vault（人工阅读 + 结构化）",
        "",
        "Obsidian Vault 结构:",
        "  决策/ → 不可逆选择（技术选型、架构定稿）",
        "  知识/ → 沉淀积累（研究、架构理解）",
        "  流程/ → 可执行步骤（SOP、配置、操作手册）",
        "  成果/ → 可交付物（报告、产出、数据）",
        "  配置/ → 系统架构元数据（含 Agent 配置快照）",
        "  报告/ → 每日报告、定期产出",
        "```",
        "",
    ]

    (sys_dir / "系统｜架构.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ 配置/architecture.md")

    # ── 每个 Agent 的详情文档 ──
    for agent_id, ad in agents_data.items():
        agent_dir = sys_dir / "agents"
        agent_dir.mkdir(parents=True, exist_ok=True)

        lines = [
            "---",
            f"date: {NOW.strftime('%Y-%m-%d')}",
            f"agent: {agent_id}",
            "category: profile",
            f"category_name: {ad['name']} 配置",
            f"tags: [{agent_id}, profile, auto-sync]",
            "source: 架构采集器",
            "---",
            "",
            f"# {ad['name']} (`{agent_id}`) — 配置详情",
            "",
            f"_更新于 {NOW.strftime('%Y-%m-%d %H:%M')}_",
            "",
        ]

        if ad["entity_context"]:
            lines += [

        lines += [
            "## 配置 (config.yaml)",
            "```yaml",
            ad["config_yaml"].strip() or "(空)",
            "```",
            "",
            "## 环境变量",
            "```",
        ]
        for k, v in ad.get("env_vars", {}).items():
            lines.append(f"{k}={v}")
        lines += [
            "```",
            "",
            "",
        ]

    (sys_dir / "系统｜记忆映射.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ 配置/系统｜记忆映射.md (Agent配置详情)")
    lines = [
        "---",
        f"date: {NOW.strftime('%Y-%m-%d')}",
        "agent: system",
        "category: memory-map",
        "category_name: 记忆映射",
        "tags: [system, memory, auto-sync]",
        "source: 架构采集器",
        "---",
        "",
        f"# 记忆映射 ({NOW.strftime('%Y-%m-%d')})",
        "",
        "## 容器映射",
        "",
        "| Agent | 容器 tag | 用途 |",
        "|-------|---------|------|",
    ]
    for agent_id, ad in agents_data.items():
        lines.append(f"| {ad['name']} (`{agent_id}`) | `{ad['supertag']}` | {ad['desc']} |")
    lines += [
        "",
        "## Obsidian Vault 映射",
        f"",
        f"**Vault 路径**: `{VAULT}`",
        "",
        "| 路径 | 内容 |",
        "|------|------|",
        "| `决策/` | 不可逆选择（技术选型、架构定稿） |",
        "| `知识/` | 沉淀积累（研究、架构理解、思维模型） |",
        "| `流程/` | 可执行步骤（SOP、配置、操作手册） |",
        "| `成果/` | 可交付物（报告、产出物、数据） |",
        "| `配置/` | 系统架构元数据 |",
        "| `配置/agents/<agent>.md` | Agent 配置快照 |",
        "| `报告/` | 每日报告、定期产出 |",
        "",
        "## 基础设施",
        "",
        "| 服务 | 端口 | 用途 |",
        "|------|------|------|",
        "| CloakServe CDP 池 | `localhost:9222` | 共享 stealth 浏览器（5 种子池） |",
        "| Phoenix Live Dashboard | N/A | 监控集群 (如有) |",
        "",
    ]
    # v3.0: 追加记忆映射到已有文件（不覆写 Agent 配置详情段）
    mem_map_path = sys_dir / "系统｜记忆映射.md"
    if mem_map_path.exists():
        existing = mem_map_path.read_text(encoding="utf-8")
        mem_map_path.write_text(existing + "\n\n" + "\n".join(lines), encoding="utf-8")
    else:
        mem_map_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ 配置/系统｜记忆映射.md (记忆映射追加)")


# ═══════════════════════════════════════════════
# ═══════════════════════════════════════════════


# ═══════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════


def main():
    print(f"🔍 采集系统架构...")
    print(f"   Vault: {VAULT}")
    print(f"")

    # 采集
    agents_data = collect_agent_configs()
    sys_info = collect_system_info()
    vault_state = collect_vault_state()

    print(f"   采集到 {len(agents_data)} 个 Agent 配置")
    print(f"")

    # 写入 Obsidian
    print(f"📝 写入 Obsidian...")
    write_obsidian_architecture(agents_data, sys_info, vault_state)


    print(f"\n✅ 架构同步完成")


if __name__ == "__main__":
    main()
