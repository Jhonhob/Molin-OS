#!/usr/bin/env python3
"""
小红书发布 CLI — 供飞轮编排器（orchestrate_flywheel.py）调用

集成分发工作流：
  1. 读取 relay/copywriter_output.json
  2. 查找小红书平台内容
  3. 调用 publish/adapter.py XiaohongshuPublisher 发布
  4. 结果写入 relay/publish_results.json

使用方式：
  # 飞轮自动模式（默认）：从 copywriter_output.json 读取小红书内容并发布
  python3 publish_to_xiaohongshu.py

  # 指定平台过滤（未来多平台支持）
  python3 publish_to_xiaohongshu.py --platform 小红书

  # 发布单条内容（按 note_id 匹配）
  python3 publish_to_xiaohongshu.py --note-id xhs_12345

  # 发布全部平台内容
  python3 publish_to_xiaohongshu.py --all

  # 仅验证（不实际发布）
  python3 publish_to_xiaohongshu.py --dry-run

  # 直接指定标题和正文（绕过 copywriter_output.json）
  python3 publish_to_xiaohongshu.py --title "标题" --desc "正文"

返回码：
  0 = 发布成功（至少1条成功）
  1 = 参数/校验错误
  2 = 发布失败（全部失败）
"""

import argparse
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# 添加 media 根目录到路径，确保可以 import publish.adapter
_PROJECT_ROOT = "/Users/laomo/.hermes/profiles/media"
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from publish.adapter import XiaohongshuPublisher

logger = logging.getLogger("molin.script.publish_to_xiaohongshu")

# ─── 路径 ────────────────────────────────────────────────────────────────

MEDIA_ROOT = os.environ.get(
    "MEDIA_ROOT",
    "/Users/laomo/.hermes/profiles/media",
)
RELAY_DIR = Path(MEDIA_ROOT) / "relay"
COPYWRITER_OUTPUT = RELAY_DIR / "copywriter_output.json"
PUBLISH_RESULTS = RELAY_DIR / "publish_results.json"

# ─── 解析 copywriter_output ─────────────────────────────────────────────


def load_copywriter_output(path: Path) -> list[dict]:
    """从 copywriter_output.json 加载所有平台内容列表"""
    if not path.exists():
        logger.warning(f"copywriter_output.json 不存在: {path}")
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"copywriter_output.json 解析失败: {e}")
        return []

    contents = data.get("contents", [])
    if not contents:
        logger.warning("copywriter_output.json 中无内容 (contents 为空)")
        return []

    return contents


def find_xiaohongshu_content(
    contents: list[dict],
    platform_filter: str = None,
    note_id: str = None,
) -> list[dict]:
    """从内容列表中找出小红书（或指定平台）的内容

    Args:
        contents: copywriter_output.json 的 contents 列表
        platform_filter: 平台名称过滤（默认只匹配"小红书"）
        note_id: 按 note_id 精确匹配

    Returns:
        匹配的内容条目列表（每个条目含 platform, content, metadata）
    """
    target_platforms = ["小红书"]
    if platform_filter:
        target_platforms = [platform_filter]

    results = []
    for item in contents:
        platform = item.get("platform", "")
        if platform not in target_platforms:
            continue

        # 如果指定了 note_id，检查是否匹配
        if note_id:
            item_note_id = item.get("metadata", {}).get("note_id", "")
            content_title = item.get("content", {}).get("title", "")
            # 允许按 title 或 note_id 匹配
            if note_id not in (item_note_id, content_title):
                continue

        results.append(item)

    return results


# ─── 提取发布参数 ──────────────────────────────────────────────────────


def extract_publish_params(
    content_item: dict,
) -> tuple[str, str, list[str]]:
    """从内容条目中提取发布参数

    Args:
        content_item: copywriter_output 中的单条内容

    Returns:
        (title, desc, image_paths)
    """
    content = content_item.get("content", {})
    metadata = content_item.get("metadata", {})

    title = content.get("title", "")
    body = content.get("body", "")

    # 尝试获取图片路径
    image_paths = []
    platform_specs = metadata.get("platform_specs", {})
    if isinstance(platform_specs, dict):
        image_paths = platform_specs.get("image_paths", [])

    # 如果 content 中有 image_paths 字段
    if not image_paths and "image_paths" in content:
        image_paths = content["image_paths"]

    # 确保图片路径是绝对路径
    resolved_images = []
    for img in (image_paths or []):
        p = Path(img)
        if not p.is_absolute():
            p = Path(MEDIA_ROOT) / p
        resolved_images.append(str(p))

    return title, body, resolved_images


# ─── 发布执行 ────────────────────────────────────────────────────────────


def publish_single(
    publisher: XiaohongshuPublisher,
    title: str,
    desc: str,
    image_paths: list[str],
    dry_run: bool = False,
) -> dict:
    """发布单条笔记到小红书

    Returns:
        {
            "success": bool,
            "note_id": str or None,
            "url": str or None,
            "title": str,
            "mode": "text" or "image",
            "code": str or None,
            "message": str or None,
            ...
        }
    """
    has_images = bool(image_paths)

    if dry_run:
        if has_images:
            result = publisher.publish_image_note(
                title, desc, image_paths, dry_run=True
            )
        else:
            result = publisher.publish_text(title, desc, dry_run=True)
        # dry-run 时补充校验摘要
        result.setdefault("_checks", {})
        result["_checks"]["has_images"] = has_images
        result["_checks"]["title_length"] = len(title)
        result["_checks"]["desc_length"] = len(desc)
        result["mode"] = "image" if has_images else "text"
        return result

    if has_images:
        # 检查图片文件是否存在
        missing = [p for p in image_paths if not os.path.isfile(p)]
        if missing:
            return {
                "success": False,
                "code": "error.publish.xiaohongshu.file_not_found",
                "message": f"图片文件不存在: {', '.join(missing)}",
                "missing_images": missing,
            }
        result = publisher.publish_image_note(title, desc, image_paths)
    else:
        result = publisher.publish_text(title, desc)

    # 统一补充字段
    result["title"] = title
    result["mode"] = "image" if has_images else "text"
    return result


# ─── 结果输出 ────────────────────────────────────────────────────────────


def format_publish_results(
    all_results: list[dict],
    run_at: str,
    dry_run: bool = False,
) -> dict:
    """汇总发布结果为 relay/publish_results.json 格式

    Returns:
        {
            "run_at": "2026-05-15T15:00:00",
            "total": 3,
            "success_count": 2,
            "failure_count": 1,
            "dry_run": true/false,
            "results": [...],
            "summary": "发布 3 条，成功 2/3 条"
        }
    """
    success_count = sum(1 for r in all_results if r.get("success"))
    failure_count = len(all_results) - success_count

    return {
        "run_at": run_at,
        "total": len(all_results),
        "success_count": success_count,
        "failure_count": failure_count,
        "dry_run": dry_run,
        "results": all_results,
        "summary": (
            f"{'🟡 验证' if dry_run else '📤 发布'} "
            f"{len(all_results)} 条，"
            f"成功 {success_count}/{len(all_results)} 条"
            if len(all_results) > 0
            else "无发布内容"
        ),
    }


def write_publish_results(data: dict, path: Path):
    """写入发布结果到 relay 目录"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(f"发布结果已写入: {path}")


# ─── 命令行入口 ──────────────────────────────────────────────────────────


def parse_args(argv: list[str] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="小红书发布 CLI — 集成分发工作流",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # 内容来源
    content_group = parser.add_argument_group("内容来源")
    content_group.add_argument(
        "--source", type=str, default="copywriter",
        choices=["copywriter", "direct"],
        help="内容来源：copywriter=读取 copywriter_output.json, "
             "direct=直接指定参数 (默认: copywriter)",
    )
    content_group.add_argument(
        "--title", type=str, default=None,
        help="笔记标题 (<=20 字，direct 模式必填)",
    )
    content_group.add_argument(
        "--desc", "--description", type=str, default=None,
        dest="desc",
        help="笔记正文内容 (<=1000 字)",
    )
    content_group.add_argument(
        "--images", nargs="+", default=None,
        help="本地图片路径列表（图文笔记）",
    )

    # 分发控制
    dist_group = parser.add_argument_group("分发控制")
    dist_group.add_argument(
        "--dry-run", action="store_true", default=False,
        help="仅验证参数和 Cookie，不实际发布",
    )
    dist_group.add_argument(
        "--platform", type=str, default="小红书",
        help="指定发布平台 (默认: 小红书，未来支持多平台)",
    )
    dist_group.add_argument(
        "--note-id", type=str, default=None,
        help="按 note_id 或标题匹配发布某条内容（copywriter 模式）",
    )
    dist_group.add_argument(
        "--all", action="store_true", default=False,
        dest="publish_all",
        help="发布全部平台内容（copywriter 模式，未来扩展）",
    )

    # 输出控制
    output_group = parser.add_argument_group("输出控制")
    output_group.add_argument(
        "--output", type=str, default=None,
        help="额外输出 JSON 文件路径（默认写入 RELAY/publish_results.json）",
    )
    output_group.add_argument(
        "--no-write", action="store_true", default=False,
        help="不写入 publish_results.json（仅输出到 stdout）",
    )

    return parser.parse_args(argv)


def main(argv: list[str] = None) -> int:
    args = parse_args(argv)

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    run_at = datetime.now().isoformat(timespec="seconds")
    all_results: list[dict] = []
    dry_run = args.dry_run

    # ── 初始化发布器 ──────────────────────────────────────────────
    try:
        publisher = XiaohongshuPublisher()
    except Exception as e:
        logger.error(f"初始化发布器失败: {e}")
        result = {
            "success": False,
            "code": "error.publish.xiaohongshu.init_failed",
            "message": str(e),
        }
        # 写入失败结果
        summary_data = format_publish_results(
            [result], run_at, dry_run=dry_run
        )
        summary_data["summary"] = f"❌ 初始化失败: {e}"
        if not args.no_write:
            write_publish_results(summary_data, PUBLISH_RESULTS)
        print(json.dumps(summary_data, ensure_ascii=False, indent=2))
        return 1

    # ── 获取内容 ──────────────────────────────────────────────────
    if args.source == "direct":
        # 直接模式：使用命令行参数
        if not args.title:
            print(json.dumps({
                "success": False,
                "code": "error.publish.xiaohongshu.missing_title",
                "message": "direct 模式需要提供 --title 参数",
            }, ensure_ascii=False, indent=2))
            return 1

        title = args.title
        desc = args.desc or ""
        image_paths = args.images or []

        logger.info(
            f"{'🔍 DRY RUN' if dry_run else '📤 发布'} "
            f"direct: title='{title}' "
            f"images={len(image_paths)}"
        )

        result = publish_single(
            publisher, title, desc, image_paths, dry_run=dry_run
        )
        all_results.append(result)

    else:
        # copywriter 模式：从 copywriter_output.json 读取内容
        contents = load_copywriter_output(COPYWRITER_OUTPUT)
        if not contents:
            logger.warning("copywriter_output.json 中无内容，跳过发布")
            summary_data = format_publish_results(
                [], run_at, dry_run=dry_run
            )
            summary_data["summary"] = "⏭ 无发布内容（copywriter_output.json 为空）"
            if not args.no_write:
                write_publish_results(summary_data, PUBLISH_RESULTS)
            print(json.dumps(summary_data, ensure_ascii=False, indent=2))
            return 0

        # 筛选小红书（或指定平台）内容
        if args.publish_all:
            # --all 模式：发布所有平台内容
            # 当前只支持小红书，未来支持多平台
            platform_targets = ["小红书"]
            if args.platform:
                platform_targets = [args.platform]
            matched = find_xiaohongshu_content(
                contents, platform_filter=None, note_id=args.note_id
            )
        else:
            matched = find_xiaohongshu_content(
                contents,
                platform_filter=args.platform,
                note_id=args.note_id,
            )

        if not matched:
            platform_info = f"platform={args.platform}"
            if args.note_id:
                platform_info += f", note_id={args.note_id}"
            logger.warning(f"未找到匹配的发布内容 ({platform_info})")
            summary_data = format_publish_results(
                [], run_at, dry_run=dry_run
            )
            summary_data["summary"] = (
                f"⏭ 未找到匹配内容 ({platform_info})"
            )
            if not args.no_write:
                write_publish_results(summary_data, PUBLISH_RESULTS)
            print(json.dumps(summary_data, ensure_ascii=False, indent=2))
            return 0

        logger.info(
            f"找到 {len(matched)} 条{'🔍 待验证' if dry_run else '待发布'}内容"
        )

        # 逐条发布
        for item in matched:
            platform = item.get("platform", "未知")
            title, desc, image_paths = extract_publish_params(item)

            logger.info(
                f"  {'🔍' if dry_run else '📤'} "
                f"[{platform}] title='{title[:30]}{'...' if len(title) > 30 else ''}' "
                f"images={len(image_paths)}"
            )

            result = publish_single(
                publisher, title, desc, image_paths, dry_run=dry_run
            )
            # 补充平台信息
            result["platform"] = platform
            all_results.append(result)

    # ── 汇总结果 ──────────────────────────────────────────────────
    summary_data = format_publish_results(
        all_results, run_at, dry_run=dry_run
    )

    # 写入发布结果
    if not args.no_write:
        write_publish_results(summary_data, PUBLISH_RESULTS)

    # 额外输出到指定路径
    if args.output:
        extra_path = Path(args.output)
        extra_path.parent.mkdir(parents=True, exist_ok=True)
        extra_path.write_text(
            json.dumps(summary_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"结果已额外写入: {args.output}")

    # 打印摘要
    print(json.dumps(summary_data, ensure_ascii=False, indent=2))

    # 返回状态
    if summary_data["success_count"] > 0:
        logger.info(
            f"✅ 发布完成: {summary_data['success_count']}/"
            f"{summary_data['total']} 条成功"
        )
        return 0
    elif summary_data["total"] == 0:
        return 0  # 无内容也是"正常"退出
    else:
        logger.error(
            f"❌ 发布失败: {summary_data['failure_count']}/"
            f"{summary_data['total']} 条失败"
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
