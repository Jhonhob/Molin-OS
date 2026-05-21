# CloakServe Deployment — Molin-OS

## Service Topology

- **Host**: macOS (darwin-arm64), user `laomo`
- **Port**: 9222
- **Managed by**: launchd (`com.molin.cloakserve`)
- **Binary**: `~/.cloakbrowser/chromium-145.0.7632.109.2/Chromium.app/Contents/MacOS/Chromium`
- **Data dir**: `~/.cloakbrowser/cloakserve/`
- **PID check**: `launchctl list | grep cloakserve`

## Profile Pool

| Agent | Seed | CDP Port Range |
|-------|------|---------------|
| 银月传媒 | `media-yinyue` | 5100+ |
| 梅凝出海 | `global-meining` | 5101+ |
| 元瑶教育 | `edu-yuanyao` | 5102+ |
| 宋玉创业 | `side-songyu` | 5103+ |
| 玄骨中枢 | `core-xuangu` | 5104+ |

## Verify Running

```bash
curl http://localhost:9222/                        # status + active seeds
curl "http://localhost:9222/json/version?fingerprint=media-yinyue"  # test seed launch
```

## Binary Download Issue (China)

Download from `cloakbrowser.dev` is slow (~200KB/s). Use `-C -` (resume) if interrupted:
```bash
curl -L -C - --max-time 600 \
  "https://cloakbrowser.dev/chromium-v{version}/cloakbrowser-{platform}.tar.gz" \
  -o /tmp/cloakbrowser.tar.gz
```

Available platforms: `darwin-arm64`, `darwin-x64`, `linux-x64`, `windows-x64`.

## Per-Profile Connection

All 5 profiles have the `cloakserve` skill under `skills/molin-org/cloakserve/`.
