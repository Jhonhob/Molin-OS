# iCloud 幽灵目录删除

在 Molin-OS 运维中，iCloud Drive 同步可能导致目录在 `rm -rf` 后自动恢复。

## 根因

iCloud Drive 的同步引擎在云端维护目录记录。本地 `rm -rf` 后，iCloud 检测到"本地删了但云端还有"，视为同步冲突，自动恢复目录。

特征：
- `rm -rf` 不报错但目录仍在
- `ls -laO` 可能显示 `uchg` 标志（用户不可变）
- `mv` 到其他位置也无效
- `sudo rm` 需要密码

## 修复步骤

### 方案 A：暂停 iCloud 服务后删除（推荐）

```bash
# 1. 暂停 iCloud Drive 文件提供者
launchctl bootout gui/$(id -u)/com.apple.cloudd 2>/dev/null

# 2. 删除目标目录
rm -rf "/path/to/ghost-directory"

# 3. 恢复 iCloud 服务
launchctl bootstrap gui/$(id -u) /System/Library/LaunchAgents/com.apple.cloudd.plist 2>/dev/null
```

### 方案 B：系统设置重启

系统设置 → Apple ID → iCloud → 关掉 iCloud 云盘 → 删除目录 → 重新打开 iCloud 云盘

## 陷阱

- ❌ **不要先设 `chflags -R uchg`**：这会锁定目录，导致不可删除且难以解锁
- ❌ **不要用 `sudo rm`**：在非交互式环境下无法输入密码
- ✅ **先清空文件内容再删目录**：防止 iCloud 恢复时带回文件
  ```bash
  find /path/to/dir -type f -exec sh -c 'echo "" > "$1"' _ {} \;
  rm -rf /path/to/dir
  ```

## 预防

- 所有写入脚本使用正确的 vault 路径：`~/Library/Mobile Documents/iCloud~md~obsidian/Documents/`
- 避免创建 `agent-outputs/` 等多条写入路径
- vault_health_check.py 自动检测遗留目录
