# CloakServe Installation Notes

## GFW / China Network Workarounds

The CloakBrowser binary (~140-200MB) is hosted at `cloakbrowser.dev` (primary) and GitHub Releases (fallback). Both can be slow or drop mid-download from behind the GFW.

### Fastest approach: resume download via cloakbrowser.dev

```bash
cd /tmp
curl -L -C - --connect-timeout 10 --max-time 600 \
  "https://cloakbrowser.dev/chromium-v145.0.7632.109.2/cloakbrowser-darwin-arm64.tar.gz" \
  -o cloakbrowser-darwin-arm64.tar.gz
```

Parameters:
- `-C -` enables resume — if the download drops at 115MB/147MB, re-run and it picks up
- `--max-time 600` allows 10 minutes for completion
- The URL uses `cloakbrowser.dev` (not GitHub) which routes through a different CDN (~260 KB/s vs GitHub's ~40 KB/s)

### After download

```bash
tar xzf cloakbrowser-darwin-arm64.tar.gz -C ~/.cloakbrowser/chromium-145.0.7632.109.2/
```

### If downloads consistently time out

The `python3 -m cloakbrowser install` command uses `httpx` internally with a 10-min cumulative timeout. If it keeps failing, download manually as above, then verify:

```bash
python3 -m cloakbrowser info
# Expected: "Installed: True"
```

### Platform-specific versions

| Platform | Version | Archive |
|----------|---------|---------|
| darwin-arm64 (M1/M2/M3/M4) | 145.0.7632.109.2 | `cloakbrowser-darwin-arm64.tar.gz` |
| darwin-x64 (Intel Mac) | 145.0.7632.109.2 | `cloakbrowser-darwin-x64.tar.gz` |
| linux-x64 | 146.0.7680.177.3 | `cloakbrowser-linux-x64.tar.gz` |
| linux-arm64 | 146.0.7680.177.3 | `cloakbrowser-linux-arm64.tar.gz` |
| windows-x64 | 146.0.7680.177.4 | `cloakbrowser-windows-x64.tar.gz` |

## launchd Service

plist location: `~/Library/LaunchAgents/com.molin.cloakserve.plist`

### Known issues

- `KeepAlive=true` means launchd restarts cloakserve if it crashes. If the binary download is incomplete or the binary doesn't exist, it will keep crashing and restarting. Ensure binary is installed first.
- Environment PATH in the plist must include the Python bin directory where `pip install`d packages reside (`~/Library/Python/3.9/bin` for system Python, or the venv path for brew Python).

## Profile Seeds

Defined in `~/.cloakbrowser/cloakserve.conf.yaml`:

```yaml
port: 9222
headless: true
data_dir: /Users/laomo/.cloakbrowser/cloakserve

profiles:
  media-yinyue:
    description: 银月传媒 — 社媒自动化
    default_timezone: Asia/Shanghai
    default_locale: zh-CN
  global-meining:
    description: 梅凝出海 — 跨境电商
    default_timezone: ~
    default_locale: en-US
  edu-yuanyao:
    description: 元瑶教育 — 教育数据
    default_timezone: Asia/Shanghai
    default_locale: zh-CN
  side-songyu:
    description: 宋玉创业 — 市场调研
    default_timezone: Asia/Shanghai
    default_locale: zh-CN
  core-xuangu:
    description: 玄骨中枢 — 共享服务
    default_timezone: UTC
    default_locale: en-US
```

## Port Allocation

cloakserve dynamically allocates CDP ports starting at 5100:

| Seed | Typical CDP Port |
|------|-----------------|
| (first connection) | 5100 |
| (second connection) | 5101 |
| ... | increments |

Ports are allocated on-demand and freed when the Chrome process is killed.

## Logs

```bash
tail -f ~/.cloakbrowser/cloakserve.log
tail -f ~/.cloakbrowser/cloakserve.err.log
```
