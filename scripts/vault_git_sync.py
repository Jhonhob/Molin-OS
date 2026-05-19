#!/usr/bin/env python3
"""
Vault Git 同步桥 — iCloud Drive 下 git mmap 冲突的永久解决方案。

原理：
  iCloud Drive 的文件锁与 git mmap 冲突，导致 git fetch/push 随机失败。
  本脚本维护一份 vault 的 git 镜像（在普通文件系统上），
  所有 git 操作都在镜像上执行，rsync 负责 vault ↔ 镜像的文件同步。

用法：
  python3 vault_git_sync.py          # 推送本地改动
  python3 vault_git_sync.py --pull   # 拉取远程改动到 vault
  python3 vault_git_sync.py --dry-run  # 仅检查，不执行

Cron（建议 15 分钟一次）：
  */15 * * * * cd ~/Molin-OS/scripts && python3 vault_git_sync.py >> /tmp/vault-git-sync.log 2>&1
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
MIRROR_PATH = Path(os.path.expanduser("~/Molin-OS/.vault-git-mirror"))
GIT_REMOTE = "git@github.com:moye-tech/Molin-OS.git"
GIT_BRANCH = "vault"

# rsync 同步的文件类型
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


def ensure_mirror():
    """确保镜像目录存在，首次运行时 clone。"""
    if not (MIRROR_PATH / ".git").exists():
        print(f"🔧 初始化镜像: {MIRROR_PATH}")
        MIRROR_PATH.parent.mkdir(parents=True, exist_ok=True)
        if DRY_RUN:
            print(f"   [dry-run] git clone --depth 1 {GIT_REMOTE} {MIRROR_PATH}")
            return
        # 浅克隆减少 iCloud 无关开销
        run(f"git clone --depth 1 {GIT_REMOTE} {MIRROR_PATH}")
        # 确保 HTTP/1.1（防 HTTP/2 超时）
        run(f"git -C {MIRROR_PATH} config http.https://github.com.version HTTP/1.1")
        print("✅ 镜像初始化完成")


def rsync_vault_to_mirror():
    """将 vault 的改动同步到镜像。返回变更文件列表。"""
    include_args = " ".join(f"--include='{p}'" for p in RSYNC_INCLUDE)
    exclude_args = " ".join(f"--exclude='{p}'" for p in RSYNC_EXCLUDE)
    
    # rsync 静默执行，变更数从 git status 获取（避免中文编码问题）
    flag = "n" if DRY_RUN else ""
    cmd = (f'rsync -a{flag} --delete '
           f'{include_args} {exclude_args} '
           f'"{VAULT_PATH}/" "{MIRROR_PATH}/"')
    
    stdout, stderr, rc = run(cmd, timeout=180)
    if stderr:
        print(f"   ⚠️  rsync: {stderr[:100]}")
    
    # 用 git status 获取实际变更
    if DRY_RUN:
        return 0, []
    out, _, _ = run("git status --porcelain", cwd=MIRROR_PATH)
    changed = [l[3:] for l in out.split('\n') if l.strip()]
    return len(changed), changed


def rsync_mirror_to_vault():
    """将镜像的改动同步回 vault（pull 模式）。返回变更文件列表。"""
    include_args = " ".join(f"--include='{p}'" for p in RSYNC_INCLUDE)
    exclude_args = " ".join(f"--exclude='{p}'" for p in RSYNC_EXCLUDE)
    
    flag = "n" if DRY_RUN else ""
    cmd = (f'rsync -a{flag} '
           f'{include_args} {exclude_args} '
           f'"{MIRROR_PATH}/" "{VAULT_PATH}/"')
    
    stdout, stderr, rc = run(cmd, timeout=180)
    if stderr:
        print(f"   ⚠️  rsync: {stderr[:100]}")
    
    # 用 git status 获取实际变更
    if DRY_RUN:
        return 0, []
    out, _, _ = run("git status --porcelain", cwd=MIRROR_PATH)
    changed = [l[3:] for l in out.split('\n') if l.strip()]
    return len(changed), changed


def git_push():
    """在镜像上 git add/commit/push。"""
    # 检查是否有改动
    stdout, _, _ = run("git status --porcelain", cwd=MIRROR_PATH)
    if not stdout.strip():
        print("📭 无本地改动，跳过 push")
        return False
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    if DRY_RUN:
        print(f"[dry-run] git add -A && git commit -m 'vault backup: {now}' && git push")
        return True
    
    run("git add -A", cwd=MIRROR_PATH)
    run(f'git commit -m "vault backup: {now}"', cwd=MIRROR_PATH)
    run(f"git push origin {GIT_BRANCH}", cwd=MIRROR_PATH)
    print(f"✅ 已推送 (commit: vault backup: {now})")
    return True


def git_pull():
    """从远程拉取到镜像。"""
    if DRY_RUN:
        print(f"[dry-run] git pull origin {GIT_BRANCH}")
        return
    
    stdout, _, _ = run(f"git pull origin {GIT_BRANCH}", cwd=MIRROR_PATH)
    if "Already up to date" in stdout:
        print("📭 远程无新改动")
        return False
    print("✅ 已拉取远程改动")
    return True


def main():
    print(f"🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   vault:  {VAULT_PATH}")
    print(f"   mirror: {MIRROR_PATH}")
    print(f"   mode:   {'DRY-RUN' if DRY_RUN else 'PULL' if PULL_MODE else 'PUSH'}")
    print()
    
    ensure_mirror()
    
    if PULL_MODE:
        # ── Pull: 远程 → 镜像 → vault ──
        pulled = git_pull()
        if pulled:
            count, files = rsync_mirror_to_vault()
            print(f"   📥 同步 {count} 文件到 vault")
            if files and len(files) <= 10:
                for f in files:
                    print(f"      + {f}")
    else:
        # ── Push: vault → 镜像 → 远程 ──
        count, files = rsync_vault_to_mirror()
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
