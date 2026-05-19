#!/usr/bin/env python3
"""
Vault Git 同步桥 — iCloud Drive Obsidian vault → Molin-OS vault/ (main 分支)

原理：
  iCloud Drive 的文件锁与 git mmap 冲突，导致 git fetch/push 随机失败。
  本脚本放弃独立的 git 镜像仓库，改为直接 rsync iCloud vault → Molin-OS/vault/，
  然后在 Molin-OS 仓库中 git add/commit/push。

用法：
  python3 vault_git_sync.py          # 推送本地改动
  python3 vault_git_sync.py --pull   # 无操作（vault 在 main 分支中，无需单独拉取）
  python3 vault_git_sync.py --dry-run  # 仅检查，不执行

Cron（建议每小时一次）：
  0 * * * * cd ~/Molin-OS/scripts && python3 vault_git_sync.py >> /tmp/vault-git-sync.log 2>&1
"""
import os
import sys
import subprocess
import datetime
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────────
VAULT_PATH = Path(os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents"
))
MOLIN_OS_PATH = Path(os.path.expanduser("~/Molin-OS"))
VAULT_TARGET = MOLIN_OS_PATH / "vault"
GIT_REMOTE = "git@github.com:moye-tech/Molin-OS.git"
GIT_BRANCH = "main"

# rsync 同步的文件类型（与 iCloud vault 一致）
RSYNC_INCLUDE = ["*.md", "*.json", "*.canvas", "*.css", "*.js"]
RSYNC_EXCLUDE = [".git/", ".obsidian/", ".*", "*.png", "*.jpg", "*.jpeg",
                 "*.gif", "*.webp", "*.mp3", "*.mp4", "*.mov", "*.pdf"]

DRY_RUN = "--dry-run" in sys.argv
PULL_MODE = "--pull" in sys.argv


def run(cmd, cwd=None, check=True, timeout=120):
    """运行命令，返回 (stdout, stderr, returncode)。"""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True,
        cwd=cwd, timeout=timeout,
        errors='replace'  # 容错中文文件名
    )
    if check and result.returncode != 0:
        print(f"❌ 命令失败: {cmd[:80]}")
        print(f"   stderr: {result.stderr.strip()[:200]}")
        if not DRY_RUN:
            sys.exit(1)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def ensure_git_config():
    """确保 Molin-OS 仓库有 HTTP/1.1 配置（防 HTTPS 超时）。"""
    if not DRY_RUN:
        run(f"git config http.https://github.com.version HTTP/1.1",
            cwd=MOLIN_OS_PATH, check=False)


def rsync_to_vault_target():
    """将 iCloud vault 的改动同步到 Molin-OS/vault/。返回变更文件列表。"""
    include_args = " ".join(f"--include='{p}'" for p in RSYNC_INCLUDE)
    exclude_args = " ".join(f"--exclude='{p}'" for p in RSYNC_EXCLUDE)

    flag = "n" if DRY_RUN else ""
    cmd = (f'rsync -a{flag} --delete '
           f'{include_args} {exclude_args} '
           f'"{VAULT_PATH}/" "{VAULT_TARGET}/"')

    stdout, stderr, rc = run(cmd, timeout=180)
    if stderr:
        print(f"   ⚠️  rsync: {stderr[:100]}")

    if DRY_RUN:
        return 0, []

    # 用 git status 获取 vault/ 目录的实际变更
    out, _, _ = run("git status --porcelain vault/", cwd=MOLIN_OS_PATH)
    changed = [l[3:] for l in out.split('\n') if l.strip()]
    return len(changed), changed


def git_push():
    """在 Molin-OS 仓库上 git add/commit/push vault/。"""
    # 检查是否有改动
    stdout, _, _ = run("git status --porcelain vault/", cwd=MOLIN_OS_PATH)
    if not stdout.strip():
        print("📭 vault 无本地改动，跳过 push")
        return False

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if DRY_RUN:
        print(f"[dry-run] git add vault/ && git commit -m 'vault sync: {now}' && git push")
        return True

    run("git add vault/", cwd=MOLIN_OS_PATH)
    run(f'git commit -m "vault sync: {now}"', cwd=MOLIN_OS_PATH)
    run(f"git push origin {GIT_BRANCH}", cwd=MOLIN_OS_PATH)
    print(f"✅ 已推送 (commit: vault sync: {now})")
    return True


def git_pull():
    """从远程拉取 vault/ 内容（仅需 git pull）。"""
    if DRY_RUN:
        print(f"[dry-run] git pull origin {GIT_BRANCH}")
        return

    stdout, _, _ = run(f"git pull origin {GIT_BRANCH}", cwd=MOLIN_OS_PATH)
    if "Already up to date" in stdout:
        print("📭 远程无新改动")
        return False
    print("✅ 已拉取远程改动")
    return True


def main():
    print(f"🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   vault (iCloud): {VAULT_PATH}")
    print(f"   target:         {VAULT_TARGET}")
    print(f"   mode:           {'DRY-RUN' if DRY_RUN else 'PULL' if PULL_MODE else 'PUSH'}")
    print()

    ensure_git_config()

    if PULL_MODE:
        # ── Pull: git pull → 更新 vault/ ──
        # Pull 模式只是拉取 git 最新内容，vault/ 由 Molin-OS 仓库管理
        print("   🔄 Pull 模式：拉取 Molin-OS 主仓库最新内容")
        pulled = git_pull()
        if pulled:
            print("   📥 已拉取远程 vault 同步")
    else:
        # ── Push: iCloud vault → Molin-OS/vault/ → git push ──
        count, files = rsync_to_vault_target()
        if count > 0:
            print(f"   📤 检测到 {count} 个文件变更")
            if files and len(files) <= 10:
                for f in files:
                    print(f"      ~ {f}")
        else:
            print("   📤 vault 无变更")
        git_push()

    if DRY_RUN:
        print("\n⚠️  DRY-RUN 模式，未执行实际操作")
    else:
        print("\n✅ 完成")


if __name__ == "__main__":
    main()
