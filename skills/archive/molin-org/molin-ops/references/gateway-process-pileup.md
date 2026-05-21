# Gateway Process Pile-up Debug Log

## Reproduction (2026-05-17)

6 gateway processes accumulated since 12:56, running until 23:00 (~10 hours). All had `--replace` but couldn't kill each other.

```
laomo  50589  ... 12:56下午  7:01.20  hermes gateway run --replace
laomo  50634  ... 12:56下午  2:31.40  hermes gateway run --replace
laomo  50613  ... 12:56下午  3:36.93  hermes gateway run --replace
laomo  50668  ... 12:57下午  2:09.90  hermes gateway run --replace
laomo  50648  ... 12:56下午  1:25.16  hermes gateway run --replace
laomo  50630  ... 12:56下午  1:23.08  hermes gateway run --replace
```

## Impact

- Web UI (port 3000) returned HTTP 200 but SSE streaming failed
- Gateway API (port 8642) health check returned `{"status":"ok"}` from at least one instance
- Bridge IPC socket `/tmp/hermes-agent-bridge.sock` existed but connected to wrong gateway
- Agent tasks showed "SSE client disconnected; interrupted agent task" repeatedly in gateway.log (18 disconnects on 2026-05-17 alone)
- error.log showed `ClientConnectionResetError: Cannot write to closing transport` — the bridge/sse writer was sending to a closing transport

## Cleanup Sequence

1. `kill` all gateway PIDs (some survived — SIGTERM was caught by --replace logic?)
2. `kill -9` survivors
3. `rm -f /tmp/hermes-agent-bridge.sock`
4. `hermes gateway run --replace` (background)
5. Wait 5s → kill web UI node process
6. Wait 8s → verify health + socket + UI HTTP
7. Login with token from `~/.hermes-web-ui/.token`

## Log Evidence

gateway.log showed the pile-up origin:
```
12:56:48  1st gateway start
12:56:49  Cron ticker started
12:56:54  kanban dispatcher started
```
Same timestamp repeated 6 times. All from `hermes gateway run --replace` calls, none successfully replacing prior instances.

## Key Metrics

| Metric | Value |
|--------|-------|
| Max PIDs accumulated | 6 |
| Runtime before detection | ~10 hours |
| SSE client disconnects logged | 18 events |
| error.log entries on kill | ~30 `ClientConnectionResetError` |
