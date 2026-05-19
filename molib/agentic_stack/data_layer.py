"""
墨麟 — Data Layer (本地监控面板)

吸收自 agentic-stack 的 data_layer_export.py：
- 跨 harness 统一 dashboard
- harness events, cron timelines, KPI, token/cost
- 输出 dashboard.html, daily-report.md
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class DashboardMetrics:
    """看板指标"""
    sessions_today: int = 0
    total_tool_calls: int = 0
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    estimated_cost_usd: float = 0.0
    cron_jobs_active: int = 0
    cron_jobs_failed: int = 0
    skills_loaded: int = 0
    lessons_graduated: int = 0
    memory_entries: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    def to_html_row(self) -> str:
        """渲染为 HTML 表格行"""
        return f"""<tr>
    <td>{self.sessions_today}</td>
    <td>{self.total_tool_calls}</td>
    <td>{self.total_tokens_input:,}</td>
    <td>{self.total_tokens_output:,}</td>
    <td>${self.estimated_cost_usd:.4f}</td>
    <td>{self.cron_jobs_active}</td>
    <td>{self.cron_jobs_failed}</td>
    <td>{self.skills_loaded}</td>
    <td>{self.lessons_graduated}</td>
    <td>{self.memory_entries}</td>
</tr>"""


@dataclass
class DataLayer:
    """
    本地监控面板。

    用法:
        dl = DataLayer()
        dl.record_session(tool_calls=12, tokens_in=5000, tokens_out=2000)
        dl.export_html()  # 输出 dashboard.html
        dl.export_report()  # 输出 daily-report.md
    """

    base_dir: str = "~/.hermes/agentic_memory/data"
    _events: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        Path(self.base_dir).expanduser().mkdir(parents=True, exist_ok=True)

    def record_event(self, event_type: str, data: Dict[str, Any]):
        """记录事件"""
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        self._events.append(event)
        # 追加到 events.jsonl
        path = Path(self.base_dir).expanduser() / "events.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def record_session(self, **kwargs):
        """快捷记录一次会话"""
        self.record_event("session", kwargs)

    def get_metrics(self) -> DashboardMetrics:
        """从 events.jsonl 聚合指标"""
        metrics = DashboardMetrics()
        events_path = Path(self.base_dir).expanduser() / "events.jsonl"
        if not events_path.exists():
            return metrics
        for line in events_path.read_text(encoding="utf-8").strip().split("\n"):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                if event.get("type") == "session":
                    data = event.get("data", {})
                    metrics.sessions_today += 1
                    metrics.total_tool_calls += data.get("tool_calls", 0)
                    metrics.total_tokens_input += data.get("tokens_in", 0)
                    metrics.total_tokens_output += data.get("tokens_out", 0)
                    metrics.estimated_cost_usd += data.get("cost_usd", 0.0)
            except (json.JSONDecodeError, TypeError):
                continue
        return metrics

    def export_html(self) -> str:
        """导出 dashboard.html"""
        metrics = self.get_metrics()
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>Agentic Dashboard</title>
<style>
body {{ font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 2rem; }}
h1 {{ color: #58a6ff; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #30363d; }}
th {{ color: #8b949e; }}
tr:hover {{ background: #161b22; }}
.metric {{ font-size: 1.5rem; font-weight: bold; color: #58a6ff; }}
</style></head>
<body>
<h1>Hermes Agentic Dashboard</h1>
<p>Generated: {datetime.now().isoformat()}</p>
<table>
<thead><tr>
<th>Sessions</th><th>Tool Calls</th><th>Input Tokens</th><th>Output Tokens</th>
<th>Cost</th><th>Cron Active</th><th>Cron Failed</th>
<th>Skills</th><th>Lessons</th><th>Memory</th>
</tr></thead>
<tbody>{metrics.to_html_row()}</tbody>
</table>
</body></html>"""
        path = Path(self.base_dir).expanduser() / "dashboard.html"
        path.write_text(html, encoding="utf-8")
        return str(path)

    def export_report(self) -> str:
        """导出 daily-report.md"""
        metrics = self.get_metrics()
        report = f"""---
created: {datetime.now().isoformat()}
agent: system
category: 报告
---

# Daily Agentic Report

| 指标 | 值 |
|------|-----|
| Sessions Today | {metrics.sessions_today} |
| Tool Calls | {metrics.total_tool_calls} |
| Input Tokens | {metrics.total_tokens_input:,} |
| Output Tokens | {metrics.total_tokens_output:,} |
| Estimated Cost | ${metrics.estimated_cost_usd:.4f} |
| Cron Jobs Active | {metrics.cron_jobs_active} |
| Cron Jobs Failed | {metrics.cron_jobs_failed} |
| Skills Loaded | {metrics.skills_loaded} |
| Lessons Graduated | {metrics.lessons_graduated} |
| Memory Entries | {metrics.memory_entries} |
"""
        path = Path(self.base_dir).expanduser() / "daily-report.md"
        path.write_text(report, encoding="utf-8")
        return str(path)
