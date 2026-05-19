"""
墨麟 — 四层记忆系统

吸收自 agentic-stack 的四层记忆模式：
- working: 当前任务状态（2天后自动归档）
- episodic: 历史运行记录（JSONL，按显著性评分）
- semantic: 长期模式/教训（LESSONS.md）
- personal: 用户偏好（永不合并到 semantic）
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path


# ── 记忆层级 ─────────────────────────────────────────────────────

@dataclass
class MemoryEntry:
    """单条记忆条目"""
    id: str
    content: str
    layer: str  # working / episodic / semantic / personal
    timestamp: str = ""
    significance: float = 0.0  # 0-1 显著性评分
    tags: List[str] = field(default_factory=list)
    source: str = ""  # 来源（skill名 / 任务ID）

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


MemoryLayer = List[MemoryEntry]
"""单个记忆层 = MemoryEntry 列表"""


@dataclass
class MemoryLayers:
    """
    四层记忆容器。

    用法:
        ml = MemoryLayers(base_dir="~/.hermes/agentic_memory")
        ml.add("今天解决了 SmartDispatcher 的 bug", layer="episodic", significance=0.8)
        lessons = ml.query(layer="semantic", tags=["lesson"])
    """

    base_dir: str = os.path.expanduser("~/.hermes/agentic_memory")
    _layers: dict = field(default_factory=lambda: {
        "working": [],
        "episodic": [],
        "semantic": [],
        "personal": [],
    })

    def __post_init__(self):
        self._load_all()

    # ── 持久化 ─────────────────────────────────────────────────

    def _layer_path(self, layer: str) -> Path:
        return Path(self.base_dir) / f"{layer}.jsonl"

    def _load_all(self):
        """从磁盘加载所有层"""
        for layer in self._layers:
            path = self._layer_path(layer)
            if path.exists():
                entries = []
                for line in path.read_text(encoding="utf-8").strip().split("\n"):
                    if line.strip():
                        try:
                            entries.append(MemoryEntry.from_dict(json.loads(line)))
                        except json.JSONDecodeError:
                            continue
                self._layers[layer] = entries

    def _save_layer(self, layer: str):
        """持久化单层到 JSONL"""
        path = self._layer_path(layer)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for entry in self._layers[layer]:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    # ── CRUD ───────────────────────────────────────────────────

    def add(
        self,
        content: str,
        layer: str = "episodic",
        significance: float = 0.5,
        tags: Optional[List[str]] = None,
        source: str = "",
    ) -> MemoryEntry:
        """添加一条记忆"""
        if layer not in self._layers:
            raise ValueError(f"Unknown layer: {layer}. Use: working/episodic/semantic/personal")
        entry = MemoryEntry(
            id=f"{layer}_{int(time.time())}_{len(self._layers[layer])}",
            content=content,
            layer=layer,
            significance=min(max(significance, 0.0), 1.0),
            tags=tags or [],
            source=source,
        )
        self._layers[layer].append(entry)
        self._save_layer(layer)
        return entry

    def query(
        self,
        layer: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_significance: float = 0.0,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        """查询记忆"""
        results = []
        layers = [layer] if layer else self._layers.keys()
        for l in layers:
            for entry in self._layers.get(l, []):
                if entry.significance < min_significance:
                    continue
                if tags and not any(t in entry.tags for t in tags):
                    continue
                results.append(entry)
        # 按显著性排序
        results.sort(key=lambda e: e.significance, reverse=True)
        return results[:limit]

    def archive_working(self, max_age_days: int = 2):
        """将超过 max_age_days 的 working 记忆归档到 episodic"""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        archived = []
        remaining = []
        for entry in self._layers["working"]:
            try:
                ts = datetime.fromisoformat(entry.timestamp)
                if ts < cutoff:
                    entry.layer = "episodic"
                    entry.significance = max(entry.significance, 0.3)
                    archived.append(entry)
                else:
                    remaining.append(entry)
            except (ValueError, TypeError):
                remaining.append(entry)
        self._layers["working"] = remaining
        self._layers["episodic"].extend(archived)
        self._save_layer("working")
        self._save_layer("episodic")
        return len(archived)

    def summarize(self) -> dict:
        """返回各层统计"""
        return {
            layer: {
                "count": len(entries),
                "avg_significance": round(
                    sum(e.significance for e in entries) / len(entries), 2
                ) if entries else 0,
            }
            for layer, entries in self._layers.items()
        }
