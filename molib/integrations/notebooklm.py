"""Molib 集成模块 — Qiaomu Anything → NotebookLM

自动识别多种内容源（URL/文件/YouTube/播客），
上传到 NotebookLM 并生成播客/PPT/思维导图/深度分析等。

配合 Hermes skill 使用：
  python -m molib notebooklm upload <path|url> [--title TITLE] [--output FORMAT]
  python -m molib notebooklm analyze <path|url> [--to-feishu]
  python -m molib notebooklm generate <path|url> [--output podcast|slide-deck|mind-map|quiz|report]
  python -m molib notebooklm pipeline           # 从 relay/ 读取情报并处理

依赖:
  - notebooklm-py (v0.4.1 via Python 3.11)
  - markitdown (文件转换)
  - 可选: Get笔记 API (小宇宙/喜马拉雅/B站转写)
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

# ── 常量 ──

NOTEBOOKLM_PYTHON = "/opt/homebrew/bin/python3.11"
RELAY_DIR = Path(os.environ.get("MOLIN_RELAY", "/Users/laomo/molin/relay"))
OBSIDIAN_VAULT = Path(os.environ.get("OBSIDIAN_VAULT", "")) or \
    Path(os.environ.get("OBSIDIAN_VAULT_PATH", "/Users/laomo/Library/Mobile Documents/iCloud~md~obsidian/Documents"))

# ── NotebookLM CLI 封装 ──

def _nb(*args: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """调用 notebooklm CLI（通过 Python 3.11）"""
    cmd = [NOTEBOOKLM_PYTHON, "-m", "notebooklm"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def login_status() -> dict:
    """检查 NotebookLM 登录状态"""
    r = _nb("status")
    if r.returncode != 0:
        return {"status": "not_logged_in", "error": r.stderr.strip()}
    return {"status": "ok", "output": r.stdout.strip()}


def login() -> dict:
    """启动 NotebookLM 浏览器登录"""
    print("🔐 请在打开的浏览器窗口中登录 Google 账号")
    r = _nb("login", timeout=300)
    if r.returncode != 0:
        return {"status": "failed", "error": r.stderr.strip()}
    return {"status": "ok", "message": "登录成功"}


def list_notebooks() -> list:
    """列出所有笔记本"""
    r = _nb("list")
    if r.returncode != 0:
        print(f"❌ 获取笔记本列表失败: {r.stderr}", file=sys.stderr)
        return []
    lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
    return lines


def create_notebook(title: str) -> bool:
    """创建新笔记本"""
    r = _nb("create", title)
    if r.returncode != 0:
        print(f"❌ 创建笔记本失败: {r.stderr}", file=sys.stderr)
        return False
    print(f"✅ 已创建笔记本: {title}")
    return True


def use_notebook(title_or_id: str) -> bool:
    """切换到指定笔记本"""
    r = _nb("use", title_or_id)
    if r.returncode != 0:
        print(f"❌ 切换笔记本失败: {r.stderr}", file=sys.stderr)
        return False
    return True


def add_source(source: str, title: str = "", notebook: str = "") -> bool:
    """添加内容源到 NotebookLM

    支持: URL、本地文件、YouTube 链接
    """
    args = ["source", "add"]
    if notebook:
        args += ["--notebook", notebook]
    args.append(source)
    if title:
        args += ["--title", title]

    r = _nb(*args, timeout=180)
    if r.returncode != 0:
        print(f"❌ 添加源失败: {r.stderr}", file=sys.stderr)
        return False
    print(f"✅ 已添加源: {source[:80]}")
    return True


def generate_artifact(output_type: str, notebook: str = "",
                      timeout: int = 300) -> Optional[str]:
    """生成并下载 NotebookLM 制品

    output_type: audio, slide-deck, mind-map, quiz, report, flashcards, infographic
    返回下载的文件路径，或 None
    """
    args = ["generate", output_type]
    if notebook:
        args += ["--notebook", notebook]

    r = _nb(*args, timeout=timeout)
    if r.returncode != 0:
        print(f"❌ 生成{output_type}失败: {r.stderr}", file=sys.stderr)
        return None

    # 解析输出，提取文件路径
    output = r.stdout.strip()
    print(f"✅ {output_type} 生成完成")
    if output:
        print(f"   {output}")

    # 尝试下载
    dl_args = ["download", output_type]
    if notebook:
        dl_args += ["--notebook", notebook]
    r2 = _nb(*dl_args, timeout=timeout)
    if r2.returncode == 0 and r2.stdout.strip():
        path = r2.stdout.strip().split("\n")[-1].strip()
        if os.path.exists(path):
            return path

    return None


def ask_question(question: str, notebook: str = "") -> Optional[str]:
    """向 NotebookLM 当前笔记本提问"""
    args = ["ask", question]
    if notebook:
        args += ["--notebook", notebook]

    r = _nb(*args, timeout=120)
    if r.returncode != 0:
        print(f"⚠️ 提问失败: {r.stderr[:200]}", file=sys.stderr)
        return None

    answer = r.stdout.strip()
    if answer and len(answer) > 10:
        return answer
    return None


# ── 内容检测与转换 ──

def detect_input_type(input_path: str) -> str:
    """检测输入类型"""
    if input_path.startswith("http"):
        if "mp.weixin.qq.com" in input_path:
            return "weixin"
        elif "youtube.com" in input_path or "youtu.be" in input_path:
            return "youtube"
        elif "xiaoyuzhoufm.com" in input_path or "ximalaya.com" in input_path or "bilibili.com" in input_path:
            return "podcast"
        elif "x.com" in input_path or "twitter.com" in input_path:
            return "x_twitter"
        else:
            return "url"

    path = Path(input_path).expanduser()
    if not path.exists():
        return "search"

    suffix = path.suffix.lower()
    if suffix == ".epub":
        return "epub"
    elif suffix in (".pdf", ".txt", ".md"):
        return "document"
    elif suffix in (".docx", ".pptx", ".xlsx"):
        return "office"
    elif suffix in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        return "image"
    elif suffix in (".mp3", ".wav"):
        return "audio"
    elif suffix == ".zip":
        return "zip"
    return "unknown"


def extract_file_to_text(file_path: str) -> Optional[str]:
    """用 markitdown 将文件转为文本"""
    ext = Path(file_path).suffix.lower()
    if ext == ".epub":
        return _extract_epub(file_path)

    # 其它文件尝试用 markitdown
    try:
        import markitdown
        md = markitdown.MarkItDown()
        result = md.convert(file_path)
        return result.text_content if result else None
    except ImportError:
        print("⚠️ 请安装 markitdown: pip3 install markitdown[all]", file=sys.stderr)
        return None
    except Exception as e:
        print(f"⚠️ markitdown 转换失败: {e}", file=sys.stderr)
        return None


def _extract_epub(epub_path: str) -> Optional[str]:
    """提取 EPUB 内容为文本"""
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup

        book = epub.read_epub(epub_path)
        content = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), "html.parser")
                content.append(soup.get_text())
        return "\n\n".join(content)
    except ImportError:
        print("⚠️ 需要 ebooklib: pip3 install ebooklib beautifulsoup4", file=sys.stderr)
        return None


# ── 深度分析 ──

def label_for(content_type: str) -> str:
    labels = {
        "epub": "本书", "document": "这份文档", "podcast": "这期播客",
        "x_twitter": "这条推文", "youtube": "这个视频",
        "url": "这篇文章", "weixin": "这篇文章", "search": "这份内容",
    }
    return labels.get(content_type, "这份内容")


def generate_questions_progressive(content_type: str) -> list[tuple[str, list[str]]]:
    """生成三轮回合递进的深度分析问题"""
    name = label_for(content_type)

    round1 = [
        f"请用一段话概括{name}的核心主题和写作目的。完全基于已上传的文档内容回答，不要搜索网络。",
        f"{name}的整体结构是什么？请按章节或逻辑模块逐一列出，每个模块用2-3句话概括核心内容。",
        f"{name}提出了哪些核心论点或主张？请逐一列出并用文档中的具体内容支撑每个论点。",
        f"{name}中最具颠覆性或反常识的内容是什么？请列出3-5条，并解释每条为什么让人意外。",
    ]

    if content_type in ("epub", "document"):
        round2 = [
            f"请拆解{name}的核心论证逻辑：前提假设、推理过程、最终结论。引用具体文本段落。",
            f"{name}中引用了哪些关键案例、数据或文本证据？请逐一列出并说明每个证据的作用。",
            f"{name}中是否存在内部矛盾或值得商榷的观点？如果有请指出并分析。",
            f"{name}最独特的贡献或核心洞察是什么？如果只能用一句话概括，应该是什么？",
            f"如果要对{name}提出一个最尖锐的批评，会是什么？请从论证完整性、证据充分性等角度分析。",
        ]
    elif content_type == "youtube":
        round2 = [
            "这个视频的核心论点是什么？演讲者用哪些论据来支撑？",
            "视频中提到了哪些具体案例、数据或研究？",
            "这个视频的立场是否存在偏向或漏洞？",
            "这个视频最独特的信息或洞察是什么？",
            "如果请一位持反对立场的专家回应，他最可能提出的三个反驳点是什么？",
        ]
    else:
        round2 = [
            f"请拆解{name}的论证或叙事结构：开头如何建立框架？中间如何展开？结尾如何收束？",
            f"{name}中引用了哪些关键案例、数据或引用？请逐一列出并评估可信度。",
            f"{name}的立场或视角是否存在局限？有没有重要的反例或未被讨论的维度？",
            f"{name}最令人印象深刻的一个洞察或观点是什么？",
            f"如果要给{name}的作者写一封简短的反馈信，你会提出哪三个建设性意见或质疑？",
        ]

    round3 = [
        f"读完{name}后，读者最应该带走的一个认知改变是什么？",
        f"从{name}中可以提取出哪些可操作的行动指南、实践建议或决策原则？列出3-5条。",
        f"请用三个最有力的理由，说服一个没接触过{name}的人去认真阅读它。",
    ]

    return [
        ("【第一轮：概览与框架】", round1),
        ("【第二轮：深度挖掘】", round2),
        ("【第三轮：综合与反刍】", round3),
    ]


def run_deep_analysis(source: str, title: str, content_type: str,
                      notebook: str = "", to_feishu: bool = False) -> dict:
    """全自动深度分析：上传 → 三轮提问 → 输出结果"""
    print(f"\n{'='*60}")
    print(f"🔍 深度分析: {title}")
    print(f"{'='*60}\n")

    # 1. 创建/使用笔记本
    nb_name = notebook or f"深度分析 - {title[:30]}"
    if not use_notebook(nb_name):
        create_notebook(nb_name)
        use_notebook(nb_name)

    # 2. 添加源
    if not add_source(source, title=title):
        return {"status": "error", "step": "add_source"}

    # 等待处理
    print("⏳ 等待 NotebookLM 处理内容...")
    time.sleep(5)

    # 3. 生成三轮问题
    rounds = generate_questions_progressive(content_type)
    total_q = sum(len(qs) for _, qs in rounds)
    print(f"\n📝 共 {len(rounds)} 轮 {total_q} 个问题\n")

    # 4. 逐轮提问
    all_questions = []
    all_answers = []

    for round_label, questions in rounds:
        print(f"\n📌 {round_label}")
        for i, q in enumerate(questions, 1):
            print(f"  [{i}/{len(questions)}] {q[:60]}...", end=" ", flush=True)
            answer = ask_question(q)
            if answer:
                print(f"✅ {len(answer)} 字符")
                all_answers.append(answer)
            else:
                print("⚠️ 跳过")
                all_answers.append("")
            all_questions.append(q)
            time.sleep(2)

    # 5. 组装结果
    result = {
        "status": "success",
        "title": title,
        "source": source,
        "content_type": content_type,
        "rounds": len(rounds),
        "total_questions": total_q,
        "answered": sum(1 for a in all_answers if a),
        "qa_pairs": [
            {"question": q, "answer": a}
            for q, a in zip(all_questions, all_answers)
        ],
    }

    # 6. 可选：写入 Feishu
    if to_feishu:
        _write_to_feishu(title, all_questions, all_answers)

    # 7. 保存结果到 relay/
    safe_title = re.sub(r'[：:/\\?|<>*"\']', "_", title).strip("_")[:40]
    relay_path = RELAY_DIR / "shared" / f"notebooklm_analysis_{safe_title}_{int(time.time())}.json"
    relay_path.parent.mkdir(parents=True, exist_ok=True)
    with open(relay_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 结果已保存: {relay_path}")

    return result


def _write_to_feishu(title: str, questions: list[str], answers: list[str]):
    """通过已有的 Feishu gateway 写入飞书文档"""
    lines = [f"# {title} - 深度解读", "", "> 由 NotebookLM 分析生成", ""]
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        lines.append(f"## {i}. {q}")
        lines.append("")
        lines.append(a if a else "*（未回答）*")
        lines.append("")

    # TODO: 使用 molib.feishu_ext 已有接口写入飞书
    print("\n📝 飞书文档输出准备就绪")
    print("可通过现有 Feishu gateway 发送:")
    print(lines[0])
    print(f"...（共 {len(lines)} 行）")


# ── 管道集成 ──

def pipeline_from_intel() -> dict:
    """从 relay/shared/daily_intel.json 读取情报 → NotebookLM 处理

    读取每日情报中的高价值链接，自动上传到 NotebookLM 并生成摘要。
    这是 content-sop-pack 管线集成点。
    """
    intel_path = RELAY_DIR / "shared" / "daily_intel.json"
    if not intel_path.exists():
        return {"status": "skip", "reason": f"情报文件不存在: {intel_path}"}

    with open(intel_path, encoding="utf-8") as f:
        intel = json.load(f)

    results = []
    processed = set()

    # 提取所有链接
    links = []
    if isinstance(intel, dict):
        for section in intel.values():
            if isinstance(section, list):
                for item in section:
                    if isinstance(item, dict) and "url" in item:
                        links.append(item)
    elif isinstance(intel, list):
        links = [{"url": item} if isinstance(item, str) else item for item in intel]

    # 最多处理前 3 个链接
    for item in links[:3]:
        url = item.get("url", "")
        if not url or url in processed:
            continue
        processed.add(url)

        title = item.get("title", url.split("/")[-1][:40])
        ctype = detect_input_type(url)

        print(f"\n📋 [{ctype}] {title[:60]}")
        result = run_deep_analysis(url, title, ctype)
        results.append(result)

    return {
        "status": "ok",
        "processed": len(results),
        "results": results,
    }


# ── CLI 入口 ──

def cmd_notebooklm(args: list[str]) -> dict:
    """python -m molib notebooklm <subcommand> [args...]

    子命令:
      login           — 浏览器登录 NotebookLM
      status          — 检查登录状态
      list            — 列出笔记本
      upload <源>     — 上传内容到 NotebookLM [--title T] [--output 格式]
      generate <源>   — 上传并生成制品 [--output audio|slide-deck|mind-map|quiz|report]
      analyze <源>    — 深度分析（3轮递归提问）[--to-feishu]
      pipeline        — 从 relay 情报管线自动处理
      ask <问题>      — 向当前笔记本提问
      help            — 显示帮助
    """
    if not args or args[0] in ("help", "--help", "-h"):
        return {
            "usage": "python -m molib notebooklm <subcommand> [args]",
            "commands": {
                "login": "浏览器登录 NotebookLM",
                "status": "检查登录状态",
                "list": "列出笔记本",
                "upload <源> --title T [--output 格式]": "上传内容",
                "generate <源> --output 格式": "上传并生成制品 (audio/slide-deck/mind-map/quiz/report)",
                "analyze <源> [--to-feishu]": "深度分析（3轮递归提问）",
                "pipeline": "从 relay 情报管线自动处理",
                "ask <问题>": "向当前笔记本提问",
            },
        }

    subcmd = args[0]
    subargs = args[1:]

    if subcmd == "login":
        return login()
    elif subcmd == "status":
        return login_status()
    elif subcmd == "list":
        nbs = list_notebooks()
        return {"notebooks": nbs, "count": len(nbs)}
    elif subcmd == "upload":
        if not subargs:
            return {"error": "需要提供源路径或URL", "usage": "upload <path|url> [--title T] [--output 格式]"}
        source = subargs[0]
        title = ""
        output_type = ""
        for i, a in enumerate(subargs):
            if a == "--title" and i + 1 < len(subargs):
                title = subargs[i + 1]
            elif a == "--output" and i + 1 < len(subargs):
                output_type = subargs[i + 1]

        ctype = detect_input_type(source)
        if not title:
            title = Path(source).stem if not source.startswith("http") else source.split("/")[-1][:40]

        # 本地文件先转文本
        upload_source = source
        if not source.startswith("http"):
            text = extract_file_to_text(source)
            if text:
                tmp = tempfile.mktemp(suffix=".txt", prefix="nb_")
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(text)
                upload_source = tmp

        if not add_source(upload_source, title=title):
            return {"status": "error"}

        if output_type:
            path = generate_artifact(output_type)
            return {"status": "ok", "artifact_path": path, "title": title}

        return {"status": "ok", "message": f"已上传: {title}"}

    elif subcmd == "generate":
        if not subargs:
            return {"error": "需要提供源路径或URL", "usage": "generate <path|url> --output 格式"}
        source = subargs[0]
        output_type = "audio"
        for i, a in enumerate(subargs):
            if a == "--output" and i + 1 < len(subargs):
                output_type = subargs[i + 1]

        title = Path(source).stem if not source.startswith("http") else source.split("/")[-1][:40]
        ctype = detect_input_type(source)

        upload_source = source
        if not source.startswith("http"):
            text = extract_file_to_text(source)
            if text:
                tmp = tempfile.mktemp(suffix=".txt", prefix="nb_")
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(text)
                upload_source = tmp

        if not add_source(upload_source, title=title):
            return {"status": "error"}

        path = generate_artifact(output_type)
        return {"status": "ok", "artifact_path": path, "title": title, "output_type": output_type}

    elif subcmd == "analyze":
        if not subargs:
            return {"error": "需要提供源路径或URL", "usage": "analyze <path|url> [--to-feishu]"}
        source = subargs[0]
        to_feishu = "--to-feishu" in subargs

        title = Path(source).stem if not source.startswith("http") else source.split("/")[-1][:40]
        ctype = detect_input_type(source)

        upload_source = source
        if not source.startswith("http"):
            text = extract_file_to_text(source)
            if text:
                tmp = tempfile.mktemp(suffix=".txt", prefix="nb_")
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(text)
                upload_source = tmp

        result = run_deep_analysis(upload_source, title, ctype, to_feishu=to_feishu)
        return result

    elif subcmd == "pipeline":
        return pipeline_from_intel()

    elif subcmd == "ask":
        if not subargs:
            return {"error": "需要提供问题"}
        question = " ".join(subargs)
        answer = ask_question(question)
        return {"question": question, "answer": answer}

    return {"error": f"未知子命令: {subcmd}", "hint": "使用 'notebooklm help' 查看可用命令"}
