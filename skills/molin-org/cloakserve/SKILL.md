---
name: cloakserve
version: "1.0.0"
description: "CloakBrowser CDP multiplexer access through XuanGu CDP proxy — shared stealth browser pool for all Molin-OS agents"
allowed-tools: Terminal, Read, Write, ExecuteCode
trigger-keywords:
  - cloaks
  - cloak
  - stealth browser
  - anti-detect
  - 反爬
  - CDP
  - 浏览器指纹
invocation-context: "Load this skill when an agent needs to browse the web stealthily, bypass Cloudflare/Turnstile/reCAPTCHA, or collect data from anti-scraping sites"
input:
  format: |
    To access the shared CloakBrowser stealth browser pool:
    playwright.chromium.connect_over_cdp("http://localhost:9222?fingerprint=<seed>&<params>")

    Parameters:
      fingerprint=<seed>     — Profile identity (e.g. media-yinyue, global-meining, edu-yuanyao, side-songyu, core-xuangu)
      timezone=<tz>          — Timezone override (e.g. America/New_York, Asia/Shanghai)
      locale=<locale>        — Locale override (e.g. en-US, zh-CN)
      proxy=<url>            — SOCKS5/HTTP proxy to use
      geoip=true             — Auto-detect timezone/locale from proxy IP
      <any_other_param>      — Mapped to --fingerprint-{param}={value}
output:
  format: |
    Returns a standard Playwright Browser object via CDP.
    All standard playwright methods work: new_page(), goto(), close(), etc.
---

# CloakServe — Shared Stealth Browser Pool

## Setup (one-time)

### Prerequisites

```bash
# 1. Install cloakbrowser (also installs its own patched Playwright)
pip3 install cloakbrowser aiohttp websockets

# 2. Install Playwright browsers (needed for CDP client)
pip3 install playwright
python3 -m playwright install chromium

# 3. Download the cloakserve CDP multiplexer script
mkdir -p ~/Molin-OS/bin
curl -sL https://cdn.jsdelivr.net/gh/CloakHQ/CloakBrowser@main/bin/cloakserve \
  -o ~/Molin-OS/bin/cloakserve
chmod +x ~/Molin-OS/bin/cloakserve

# 4. Create profile pool directories
mkdir -p ~/.cloakbrowser/cloakserve/{media-yinyue,global-meining,edu-yuanyao,side-songyu,core-xuangu}

# 5. First download of the stealth Chromium binary (~200MB)
python3 -m cloakbrowser install
```

### Auto-start (macOS launchd)

The launchd plist at `~/Library/LaunchAgents/com.molin.cloakserve.plist` starts cloakserve on boot. To install:

```bash
launchctl load ~/Library/LaunchAgents/com.molin.cloakserve.plist
```

### Verification

```bash
# Check cloakserve is accepting connections
python3 ~/Molin-OS/bin/cloakserve_test.py
# Expected: "cloakserve status: ok", "Active processes: 0" (launches on demand)
```

## Overview

[CloakBrowser](https://github.com/CloakHQ/CloakBrowser) is a MIT-licensed stealth Chromium with **49 C++ source-level fingerprint patches**. It passes 30/30 bot detection tests including Cloudflare Turnstile, reCAPTCHA v3 (score 0.9), and FingerprintJS.

**cloakserve** is CloakBrowser's CDP multiplexer — runs on 玄骨中枢 (core agent) at `localhost:9222`, serving stealth browser instances to all 5 Molin-OS agents.

> **Behind GFW / China**: Binary download (~200MB) may timeout. See `references/installation-notes.md` for manual download with resume (`curl -C -`), mirror URLs, and known workarounds.
> **Verification**: Run `scripts/cloakserve_test.py [seed]` to check status.

```
┌──────────────────────────────────────────┐
│           玄骨中枢 (core-xuangu)           │
│  ┌────────────────────────────────────┐  │
│  │        cloakserve (port 9222)       │  │
│  │  CDP Multiplexer — aiohttp server   │  │
│  └──────┬──────┬──────┬──────┬────────┘  │
│         │      │      │      │           │
│    ┌────┘ ┌────┘ ┌────┘ ┌────┘           │
│  media  global  edu   side               │
│  yinyue meining yuanyao songyu           │
│  seed   seed    seed   seed              │
└──────────────────────────────────────────┘
         │  connect_over_cdp()
    ┌────┴────┐
    │ Agent   │  (any agent connects via Chromium CDP)
    └─────────┘
```

## Connecting

### Python (Playwright)

```python
from playwright.sync_api import sync_playwright

# Basic: connect to default seed (gets a random fingerprint)
pw = sync_playwright().start()
browser = pw.chromium.connect_over_cdp("http://localhost:9222")

# Named seed: consistent fingerprint per agent
browser = pw.chromium.connect_over_cdp(
    "http://localhost:9222?fingerprint=media-yinyue"
)
page = browser.new_page()
page.goto("https://protected-site.com")
# ... standard Playwright API
browser.close()

# With proxy + geoip auto-detection
browser = pw.chromium.connect_over_cdp(
    "http://localhost:9222"
    "?fingerprint=global-meining"
    "&proxy=socks5://user:pass@proxy:1080"
    "&geoip=true"
)

# For persistent sessions (cookies, localStorage survive restarts)
# Use launch_persistent_context from cloakbrowser directly:
from cloakbrowser import launch_persistent_context
ctx = launch_persistent_context(
    "./profiles/global-meining",
    headless=False,
    proxy="http://proxy:8080",
)
```

### JavaScript (Playwright)

```javascript
import { chromium } from 'playwright-core';

const browser = await chromium.connectOverCDP(
    'http://localhost:9222?fingerprint=media-yinyue'
);
const page = await browser.newPage();
await page.goto('https://protected-site.com');
await browser.close();
```

## Profile Seeds

| Agent | Seed | Purpose | Proxy Pattern |
|-------|------|---------|---------------|
| 银月传媒 | `media-yinyue` | 社媒自动化、竞品监控 | Residential proxies |
| 梅凝出海 | `global-meining` | 跨境电商采集、价格监控 | Target-country proxies |
| 元瑶教育 | `edu-yuanyao` | 教育数据采集 | None / local |
| 宋玉创业 | `side-songyu` | 市场调研、竞品分析 | General proxies |
| 玄骨中枢 | `core-xuangu` | 共享服务、CDP 回收 | None / loopback |

## Advanced Usage

### Connection Status

Check which seeds are active and their connection counts:

```bash
curl http://localhost:9222/
```

Returns JSON with active processes, PIDs, CDP ports, and connection counts per seed.

### Framework Integrations

CloakBrowser works drop-in with:

| Framework | Connection Method |
|-----------|-----------------|
| **Crawl4AI** | Set `browser_type="chromium"` + CDP endpoint in config |
| **Scrapling** | Use Playwright integration with custom CDP endpoint |
| **Stagehand** | Configure `chromeProxy` or custom CDP endpoint |
| **LangChain** | Use `PlaywrightBrowser` loader with CDP browser |
| **Selenium** | Via patching tools — set Chrome binary to cloakbrowser |

### Restarting cloakserve

```bash
# Via manager script
~/Molin-OS/bin/cloakserve-manager.sh restart

# Or via launchctl directly
launchctl unload ~/Library/LaunchAgents/com.molin.cloakserve.plist
launchctl load ~/Library/LaunchAgents/com.molin.cloakserve.plist
```

## Management

The skill ships with three support files:

| File | Path | Purpose |
|------|------|---------|
| Manager script | `scripts/cloakserve-manager.sh` | `start`/`stop`/`restart`/`status`/`logs`/`ps`/`test` |
| Test script | `scripts/cloakserve_test.py` | Verify CDP status and seed connectivity |
| Profile config | `references/profile-config.yaml` | Seed/tz/locale defaults per agent |

## Logs

```bash
tail -f ~/.cloakbrowser/cloakserve.log      # main log
tail -f ~/.cloakbrowser/cloakserve.err.log  # error log
```

## Limitations & Considerations

1. **Binary size**: ~200MB, downloaded on first launch (automatically cached)
2. **Binary path**: `~/.cloakbrowser/chromium-{version}/`
3. **Auto-update**: CloakBrowser checks for binary updates periodically
4. **GPU**: Uses `--ignore-gpu-blocklist` but headless mode doesn't use GPU anyway
5. **Not a CAPTCHA solver**: CloakBrowser prevents CAPTCHAs from appearing; if a site shows one anyway (rare), it still needs solving
6. **Browser Manager** (GUI alternative to Multilogin): available as separate Docker image at `cloakhq/cloakbrowser-manager`
