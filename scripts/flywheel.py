"""
墨麟OS — 内容飞轮管线

三棒自动化管线，每棒检查上游产出，失败自动告警。

时间线:
  🕐 08:00  第一棒：情报银行 — 情报采集 → relay/intelligencemorning.json
  🕐 09:20  第二棒：内容工厂 — 内容生成 → relay/contentmorning.json
  🕐 10:45  第三棒：增长引擎 — SEO优化+审计 → relay/growthmorning.json

保护规则:
  1. 每棒先检查上游 relay/ 文件是否存在且 < 90分钟前
  2. 上游缺失 → 日志记录 + 飞书告警，不执行
  3. 执行失败 → relay/flywheel_error.{stage}.json 记录
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Optional

FLYWHEEL_DIR = os.path.expanduser("~/Molin-OS/relay")
ERROR_DIR = os.path.join(FLYWHEEL_DIR, "errors")
MAX_UPSTREAM_AGE = 90 * 60  # 90 minutes in seconds

STAGES = {
    "intelligence": {
        "name": "情报银行",
        "output_file": "intelligencemorning.json",
        "upstream_file": None,  # 第一棒无上游
        "schedule": "08:00",
    },
    "content": {
        "name": "内容工厂",
        "output_file": "contentmorning.json",
        "upstream_file": "intelligencemorning.json",
        "schedule": "09:20",
    },
    "growth": {
        "name": "增长引擎",
        "output_file": "growthmorning.json",
        "upstream_file": "contentmorning.json",
        "schedule": "10:45",
    },
}


def ensure_dirs():
    os.makedirs(FLYWHEEL_DIR, exist_ok=True)
    os.makedirs(ERROR_DIR, exist_ok=True)


def check_upstream(stage: str) -> Optional[str]:
    """检查上游产出是否存在且未过期。返回 None 表示正常，否则返回错误信息。"""
    info = STAGES.get(stage)
    if not info:
        return f"未知阶段: {stage}"

    upstream = info["upstream_file"]
    if upstream is None:
        return None  # 第一棒无上游

    path = os.path.join(FLYWHEEL_DIR, upstream)
    if not os.path.isfile(path):
        return f"上游文件 {upstream} 不存在 — 飞轮断裂"

    age = time.time() - os.path.getmtime(path)
    if age > MAX_UPSTREAM_AGE:
        return (f"上游文件 {upstream} 已过期 ({age/60:.0f}分钟 > {MAX_UPSTREAM_AGE/60}分钟)"
                f" — 飞轮断裂")

    return None


def write_output(stage: str, data: dict):
    """写入阶段产出到 relay/"""
    info = STAGES.get(stage)
    if not info:
        return
    path = os.path.join(FLYWHEEL_DIR, info["output_file"])
    data["_flywheel_stage"] = stage
    data["_timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_error(stage: str, error: str):
    """写入飞轮断裂记录到 relay/errors/"""
    path = os.path.join(ERROR_DIR, f"flywheel_{stage}.json")
    record = {
        "stage": stage,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)


def run_stage(stage: str) -> dict:
    """执行指定阶段的飞轮检查

    返回 {"gate": "ok"|"broken"|"unknown", "message": "..."}
    """
    ensure_dirs()

    # 1. 上游检查
    upstream_error = check_upstream(stage)
    if upstream_error:
        write_error(stage, upstream_error)
        return {"gate": "broken", "message": upstream_error}

    # 2. 输出可用信号（实际工作由 cron 任务的 agent 完成）
    write_output(stage, {"gate": "passed", "message": f"{stage} gate check passed"})
    return {"gate": "ok", "message": f"{stage} gate check passed"}


def check_flywheel_health() -> dict:
    """检查飞轮整体健康状态"""
    status = {}
    for stage in STAGES:
        error_file = os.path.join(ERROR_DIR, f"flywheel_{stage}.json")
        output_file = os.path.join(FLYWHEEL_DIR, STAGES[stage]["output_file"])

        has_output = os.path.isfile(output_file)
        has_error = os.path.isfile(error_file)

        if has_error:
            with open(error_file) as f:
                err = json.load(f)
            status[stage] = {"status": "broken", "error": err.get("error", "unknown")}
        elif has_output:
            output_age = time.time() - os.path.getmtime(output_file)
            status[stage] = {"status": "ok" if output_age < MAX_UPSTREAM_AGE else "stale",
                             "age_minutes": int(output_age / 60)}
        else:
            status[stage] = {"status": "pending"}

    return {"flywheel_health": status}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "check":
            stage = sys.argv[2] if len(sys.argv) > 2 else "intelligence"
            result = run_stage(stage)
            print(json.dumps(result, ensure_ascii=False))
        elif action == "health":
            print(json.dumps(check_flywheel_health(), ensure_ascii=False))
        else:
            print("Usage: python3 flywheel.py [check|health]")
    else:
        print("Usage: python3 flywheel.py check <stage>")
