"""
墨麟 — Agentic Stack 便携大脑模块

吸收自 codejunkie99/agentic-stack (2K⭐, Apache 2.0)
"harness is dumb, brain is portable"

设计模式:
1. 四层记忆系统 (working/episodic/semantic/personal)
2. 渐进式技能披露 (manifest + trigger-based loading)
3. 教训生命周期 (candidate → graduate → reject)
4. Data Layer (跨 harness dashboard)
"""

from .memory import MemoryLayers, MemoryLayer, MemoryEntry
from .skill_manifest import SkillManifest, ManifestEntry
from .lesson_lifecycle import LessonLifecycle, Lesson, LessonStatus

__all__ = [
    "MemoryLayers", "MemoryLayer", "MemoryEntry",
    "SkillManifest", "ManifestEntry",
    "LessonLifecycle", "Lesson", "LessonStatus",
]
