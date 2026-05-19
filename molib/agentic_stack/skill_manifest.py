"""
墨麟 — 渐进式技能披露 (Skill Manifest)

吸收自 agentic-stack 的渐进式技能加载：
- _index.md + _manifest.jsonl 始终在上下文中
- 完整 SKILL.md 仅在触发器匹配时加载
- 条件触发基于任务类型/关键词
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class ManifestEntry:
    """单条技能清单条目"""
    name: str
    description: str
    triggers: List[str] = field(default_factory=list)
    """触发关键词/任务类型列表"""
    path: str = ""
    """技能路径（相对于 manifest 所在目录）"""
    priority: int = 0
    """加载优先级（越高越优先）"""

    def matches(self, task_description: str) -> bool:
        """检查任务描述是否匹配触发条件"""
        task_lower = task_description.lower()
        return any(t.lower() in task_lower for t in self.triggers)


@dataclass
class SkillManifest:
    """
    技能清单管理器。

    用法:
        manifest = SkillManifest.load("~/.hermes/agentic_memory/_manifest.jsonl")
        matched = manifest.find_matching("帮我分析股票趋势")
        for skill in matched:
            print(f"加载技能: {skill.name}")
    """

    entries: List[ManifestEntry] = field(default_factory=list)
    base_path: str = ""

    @classmethod
    def load(cls, path: str) -> "SkillManifest":
        """从 JSONL 文件加载清单"""
        p = Path(path).expanduser()
        entries = []
        if p.exists():
            for line in p.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    try:
                        data = json.loads(line)
                        entries.append(ManifestEntry(**data))
                    except (json.JSONDecodeError, TypeError):
                        continue
        return cls(entries=entries, base_path=str(p.parent))

    def save(self, path: Optional[str] = None):
        """持久化到 JSONL"""
        p = Path(path or Path(self.base_path) / "_manifest.jsonl").expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            for entry in self.entries:
                f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")

    def add(self, entry: ManifestEntry):
        """添加清单条目"""
        self.entries.append(entry)

    def find_matching(self, task_description: str, max_results: int = 3) -> List[ManifestEntry]:
        """查找匹配任务描述的技能"""
        matched = [e for e in self.entries if e.matches(task_description)]
        matched.sort(key=lambda e: e.priority, reverse=True)
        return matched[:max_results]

    def to_dict(self) -> List[Dict[str, Any]]:
        return [asdict(e) for e in self.entries]
