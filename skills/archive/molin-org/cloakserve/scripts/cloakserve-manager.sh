#!/usr/bin/env bash
# Molin-OS CloakServe Manager — start/stop/restart/status
# Usage: cloakserve-manager.sh {start|stop|restart|status|logs|ps|test [seed]}

CLOAKSERVE_PORT=9222
CLOAKSERVE_BIN="$HOME/Molin-OS/bin/cloakserve"
CLOAKSERVE_PLIST="$HOME/Library/LaunchAgents/com.molin.cloakserve.plist"
CLOAKSERVE_LOG="$HOME/.cloakbrowser/cloakserve.log"
CLOAKSERVE_ERR="$HOME/.cloakbrowser/cloakserve.err.log"

case "${1:-status}" in
  start)
    launchctl load "$CLOAKSERVE_PLIST" 2>&1
    sleep 2
    curl -s http://localhost:$CLOAKSERVE_PORT/ >/dev/null 2>&1 \
      && echo "✓ cloakserve running on port $CLOAKSERVE_PORT" \
      || echo "✗ not ready — check logs"
    ;;
  stop)
    launchctl unload "$CLOAKSERVE_PLIST" 2>&1
    echo "✓ stopped"
    ;;
  restart)
    $0 stop; sleep 1; $0 start
    ;;
  status)
    launchctl list | grep -q com.molin.cloakserve && echo "launchd: ✓" || echo "launchd: ✗"
    curl -s http://localhost:$CLOAKSERVE_PORT/ 2>/dev/null | python3 -m json.tool 2>/dev/null \
      || echo "HTTP: not reachable"
    echo "Binary:"; python3 -m cloakbrowser info 2>/dev/null | head -2
    ;;
  logs)
    tail -f "$CLOAKSERVE_LOG"
    ;;
  ps)
    echo "Active seeds:"; curl -s http://localhost:$CLOAKSERVE_PORT/ 2>/dev/null | python3 -m json.tool
    echo "Chrome:"; ps aux | grep -i chromium | grep -v grep
    ;;
  install-binary)
    python3 -m cloakbrowser install
    python3 -m cloakbrowser info
    ;;
  docker-manager)
    docker run -d --name cloakbrowser-manager -p 8080:8080 -v cloakprofiles:/data \
      cloakhq/cloakbrowser-manager 2>/dev/null \
      && echo "✓ Manager at http://localhost:8080" \
      || docker start cloakbrowser-manager 2>/dev/null \
      || echo "Install Docker first"
    ;;
  test)
    python3 "$HOME/Molin-OS/bin/cloakserve_test.py" "${2:-}"
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|logs|ps|install-binary|docker-manager|test [seed]}"
    exit 1
    ;;
esac
