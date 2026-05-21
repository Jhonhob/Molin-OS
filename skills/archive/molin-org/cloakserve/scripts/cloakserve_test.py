#!/usr/bin/env python3
"""
Molin-OS CloakServe Test — check CDP multiplexer status and connectivity.
Usage:
    python3 cloakserve_test.py [seed]

Examples:
    python3 cloakserve_test.py                   # check status only
    python3 cloakserve_test.py media-yinyue       # check + test seed
"""

import json
import sys
import urllib.request as request
import urllib.error as error

CLOAKSERVE_URL = "http://localhost:9222"


def check_status():
    """Check cloakserve status."""
    try:
        req = request.Request(CLOAKSERVE_URL)
        with request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"cloakserve status: {data['status']}")
            print(f"Active processes: {data['active']}")
            if data.get("processes"):
                for name, info in data["processes"].items():
                    print(f"  [{name}] pid={info['pid']} port={info['port']} "
                          f"connections={info['connections']} "
                          f"tz={info.get('timezone', '-')}")
            return True
    except error.URLError as e:
        print(f"cloakserve not reachable: {e.reason}")
        return False
    except Exception as e:
        print(f"cloakserve error: {e}")
        return False


def get_version(seed: str | None = None):
    """Get CDP version info, optionally with a seed."""
    url = f"{CLOAKSERVE_URL}/json/version"
    if seed:
        url += f"?fingerprint={seed}"

    try:
        req = request.Request(url)
        with request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"CDP version: {data.get('Browser', '?')}")
            ws_url = data.get("webSocketDebuggerUrl", "?")
            print(f"WS URL: {ws_url}")
            return data
    except Exception as e:
        print(f"Version check failed: {e}")
        return None


def get_pages(seed: str | None = None):
    """List CDP targets."""
    url = f"{CLOAKSERVE_URL}/json/list"
    if seed:
        url += f"?fingerprint={seed}"

    try:
        req = request.Request(url)
        with request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"Targets: {len(data)}")
            for t in data:
                print(f"  [{t.get('id', '?')[:12]}] {t.get('title', '')} "
                      f"— {t.get('url', '')}")
            return data
    except Exception as e:
        print(f"Page list failed: {e}")
        return None


if __name__ == "__main__":
    seed = sys.argv[1] if len(sys.argv) > 1 else None

    print("=" * 60)
    print("CloakServe — Molin-OS Stealth Browser Pool")
    print("=" * 60)

    if not check_status():
        sys.exit(1)

    if seed:
        print()
        print(f"--- Testing seed: {seed} ---")
        get_version(seed)
        print()
        get_pages(seed)

    print()
    print("✓ CloakServe is running and ready")
    print(f"  Connect: playwright.chromium.connect_over_cdp('{CLOAKSERVE_URL}')")
    if seed:
        print(f"  With seed: ?fingerprint={seed}")
