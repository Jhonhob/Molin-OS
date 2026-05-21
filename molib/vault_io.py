"""
Obsidian 安全写入隔离缓冲区 (Secure Vault I/O)
===================================================
解决 Obsidian 文件并发死锁。所有 Worker 写 Obsidian 不再直接操作物理文件，
而是写入 DiskCache 缓冲区，由玄骨主枢（单线程）安全持久化。

核心特性：
- DiskCache SQLite 锁 → 进程/线程安全
- 指数退避重试 → 消除 iCloud/Git 同步冲突
- 事务性刷新 → 不丢数据

用法：
    from molib.vault_io import SecureVaultIO
    vault = SecureVaultIO()
    vault.async_write_knowledge("元瑶", "用户画像", content)
    vault.flush_buffer_to_obsidian()
"""

import time
import os
from pathlib import Path
from typing import Optional


class SecureVaultIO:
    """基于 DiskCache 的 Obsidian 安全写入缓冲区"""

    DEFAULT_CACHE_DIR = Path(__file__).parent.parent / "relay" / ".vault_cache"
    DEFAULT_VAULT_ROOT = Path(__file__).parent.parent / "vault"

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        vault_root: Optional[str] = None,
    ):
        self.cache_dir = Path(cache_dir or self.DEFAULT_CACHE_DIR)
        self.vault_root = Path(vault_root or self.DEFAULT_VAULT_ROOT)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 延迟导入 DiskCache（可选依赖）
        self._cache = None
        self._disk_cache_available = False
        try:
            from diskcache import Cache
            self._cache = Cache(str(self.cache_dir))
            self._disk_cache_available = True
        except ImportError:
            # 降级到内存 dict
            self._cache = {}
            print("⚠️ diskcache 未安装，降级为内存缓冲（重启丢失）。pip install diskcache")

    # ── Worker 写入 API ─────────────────────────

    def async_write_knowledge(self, domain: str, file_name: str, content: str):
        """
        Worker 调用：将数据写入安全缓冲区，避免直接撞击物理文件锁。
        """
        task_key = f"{domain}::{file_name}"

        if self._disk_cache_available:
            with self._cache.transact():
                existing = self._cache.get(task_key, default="")
                updated = existing + "\n\n" + content if existing else content
                self._cache.set(task_key, updated)
        else:
            existing = self._cache.get(task_key, "")
            updated = existing + "\n\n" + content if existing else content
            self._cache[task_key] = updated

        print(f"📥 [{domain}] 记忆已安全存入缓冲区: {file_name}")

    def async_overwrite_knowledge(self, domain: str, file_name: str, content: str):
        """Worker 调用：覆盖写入（如知识合并后的版本）"""
        task_key = f"{domain}::{file_name}"

        if self._disk_cache_available:
            with self._cache.transact():
                self._cache.set(task_key, content)
        else:
            self._cache[task_key] = content

        print(f"📝 [{domain}] 记忆已覆盖写入缓冲区: {file_name}")

    # ── 刷新 API（由玄骨主枢调用）───────────────

    def flush_buffer_to_obsidian(self, max_retries: int = 5) -> dict:
        """
        由「玄骨·墨维」在飞轮交接时调用：
        单线程安全地将缓冲数据固化到 Obsidian 物理盘。
        内置指数退避重试，消除 iCloud/Git 同步冲突。
        """
        if self._disk_cache_available:
            keys = list(self._cache.iterkeys())
        else:
            keys = list(self._cache.keys())

        if not keys:
            print("📭 缓冲区为空，无数据需要固化。")
            return {"flushed": 0, "failed": 0, "retries": 0}

        print(f"🔄 开始将 {len(keys)} 条缓冲记忆同步至 Obsidian...")

        flushed = 0
        failed = 0
        total_retries = 0

        for key in keys:
            domain, file_name = key.split("::", 1)
            target_dir = self.vault_root / "业务层" / domain
            target_dir.mkdir(parents=True, exist_ok=True)

            target_path = target_dir / f"{file_name}.md"

            try:
                content = (self._cache.get(key) if self._disk_cache_available
                           else self._cache[key])
            except (KeyError, Exception):
                continue

            # 指数退避重试
            success = False
            for attempt in range(max_retries):
                try:
                    # 原子写入：先写临时文件，再 rename
                    tmp_path = target_path.with_suffix(".tmp")
                    with open(tmp_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    os.replace(tmp_path, target_path)
                    success = True
                    break
                except (IOError, PermissionError, OSError) as e:
                    wait_time = 2 ** attempt
                    total_retries += 1
                    print(f"   ⚠️ {file_name} 被锁定，{wait_time}s 后重试 ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)

            if success:
                if self._disk_cache_available:
                    self._cache.delete(key)
                else:
                    del self._cache[key]
                flushed += 1
                print(f"   💾 固化完成: {domain}/{file_name}.md")
            else:
                failed += 1
                print(f"   ❌ 固化失败(已重试{max_retries}次): {file_name}，保留在缓冲区")

        return {
            "flushed": flushed,
            "failed": failed,
            "remaining": len(keys) - flushed,
            "retries": total_retries,
        }

    def get_pending_count(self) -> int:
        """缓冲区待写入条目数"""
        if self._disk_cache_available:
            return len(list(self._cache.iterkeys()))
        return len(self._cache)

    def clear_buffer(self):
        """清空缓冲区（危险操作）"""
        if self._disk_cache_available:
            self._cache.clear()
        else:
            self._cache.clear()
