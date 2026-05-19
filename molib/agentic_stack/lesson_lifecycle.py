"""
墨麟 — 教训生命周期 (Lesson Lifecycle)

吸收自 agentic-stack 的 Review Protocol：
- auto_dream.py 每晚机械聚类/staging candidate lessons
- graduate.py / reject.py / reopen.py 审查
- 已毕业的教训写入 semantic/lessons.jsonl

状态流转:
    candidate → staged → graduated (永久)
             → rejected (保留原因)
    graduated → reopened → candidate (循环)
"""

import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List
from pathlib import Path


class LessonStatus:
    """教训状态常量"""
    CANDIDATE = "candidate"
    STAGED = "staged"
    GRADUATED = "graduated"
    REJECTED = "rejected"
    REOPENED = "reopened"

    _ALL = [CANDIDATE, STAGED, GRADUATED, REJECTED, REOPENED]


@dataclass
class Lesson:
    """单条教训"""
    id: str
    content: str
    category: str = "general"
    status: str = LessonStatus.CANDIDATE
    significance: float = 0.5  # 0-1
    source: str = ""
    """来源（skill名、session_id）"""
    created_at: str = ""
    updated_at: str = ""
    reject_reason: str = ""
    """拒绝原因（当 status=rejected 时）"""

    def __post_init__(self):
        now = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Lesson":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class LessonLifecycle:
    """
    教训生命周期管理器。

    用法:
        ll = LessonLifecycle()
        lesson = ll.candidate("不要在 cron 任务中用 curl，用 urllib.request")
        ll.stage(lesson.id)
        ll.graduate(lesson.id)
        ll.reject(lesson.id, "太具体，不适合长期记忆")
    """

    base_dir: str = "~/.hermes/agentic_memory"
    _lessons: List[Lesson] = field(default_factory=list)

    def __post_init__(self):
        self._load()

    def _path(self) -> Path:
        return Path(self.base_dir).expanduser() / "lessons.jsonl"

    def _load(self):
        path = self._path()
        if path.exists():
            for line in path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    try:
                        self._lessons.append(Lesson.from_dict(json.loads(line)))
                    except (json.JSONDecodeError, TypeError):
                        continue

    def _save(self):
        path = self._path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for lesson in self._lessons:
                f.write(json.dumps(lesson.to_dict(), ensure_ascii=False) + "\n")

    def _find(self, lesson_id: str) -> Optional[Lesson]:
        for l in self._lessons:
            if l.id == lesson_id:
                return l
        return None

    def _transition(self, lesson_id: str, to_status: str, reason: str = ""):
        lesson = self._find(lesson_id)
        if not lesson:
            raise ValueError(f"Lesson not found: {lesson_id}")
        lesson.status = to_status
        lesson.updated_at = datetime.now().isoformat()
        if reason:
            if to_status == LessonStatus.REJECTED:
                lesson.reject_reason = reason
        self._save()

    # ── 公开 API ─────────────────────────────────────────────

    def candidate(self, content: str, category: str = "general",
                  significance: float = 0.5, source: str = "") -> Lesson:
        """创建候选教训"""
        lesson = Lesson(
            id=f"lesson_{int(time.time())}_{len(self._lessons)}",
            content=content,
            category=category,
            significance=min(max(significance, 0.0), 1.0),
            source=source,
        )
        self._lessons.append(lesson)
        self._save()
        return lesson

    def stage(self, lesson_id: str):
        """标记为待审查"""
        self._transition(lesson_id, LessonStatus.STAGED)

    def graduate(self, lesson_id: str):
        """毕业为永久教训"""
        self._transition(lesson_id, LessonStatus.GRADUATED)

    def reject(self, lesson_id: str, reason: str = ""):
        """拒绝教训（保留原因）"""
        self._transition(lesson_id, LessonStatus.REJECTED, reason)

    def reopen(self, lesson_id: str):
        """重新打开已毕业的教训"""
        self._transition(lesson_id, LessonStatus.REOPENED)

    def list(self, status: Optional[str] = None) -> List[Lesson]:
        """获取教训列表，可按状态过滤"""
        if status:
            return [l for l in self._lessons if l.status == status]
        return list(self._lessons)

    def get_graduated(self) -> List[Lesson]:
        """获取所有已毕业的教训"""
        return [l for l in self._lessons if l.status == LessonStatus.GRADUATED]

    def get_candidates(self) -> List[Lesson]:
        """获取所有候选/待审查的教训"""
        return [
            l for l in self._lessons
            if l.status in (LessonStatus.CANDIDATE, LessonStatus.STAGED)
        ]

    def render_as_markdown(self) -> str:
        """渲染为 LESSONS.md 格式"""
        graduated = self.get_graduated()
        candidates = self.get_candidates()
        lines = [
            "---",
            "created: " + datetime.now().isoformat(),
            "agent: system",
            "category: 知识",
            "---",
            "",
            "# Lessons Learned",
            "",
            f"**Graduated**: {len(graduated)} | **Candidates**: {len(candidates)}",
            "",
        ]
        if graduated:
            lines.append("## Graduated Lessons")
            for l in graduated:
                lines.append(f"\n### {l.category}: {l.content[:60]}")
                lines.append(f"- Significance: {l.significance:.1f}")
                lines.append(f"- Source: {l.source or 'unknown'}")
        if candidates:
            lines.append("\n## Candidates (Pending Review)")
            for l in candidates:
                lines.append(f"\n- [{l.status}] {l.content[:80]}...")
        return "\n".join(lines)
