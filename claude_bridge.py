"""Small console helper for Claude Code's documented statusLine contract."""
import json
import sys
from core import atomic_json, claude_snapshot, data_dir


def main():
    try:
        raw = sys.stdin.buffer.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("Payload too large")
        snapshot = claude_snapshot(json.loads(raw.decode("utf-8-sig")))
        atomic_json(data_dir() / "claude-latest.json", snapshot)
        parts = []
        for item in snapshot["windows"]:
            if item["used"] is not None:
                label = {"five_hour": "5h", "seven_day": "7d", "spend_limit": "spend"}[item["name"]]
                parts.append(f"{label} {item['used']:g}%")
        print(" | ".join(parts) if parts else "AI Usage Monitor: waiting for quota data")
        return 0
    except (OSError, ValueError, TypeError, KeyError):
        # Never echo raw stdin or errors containing account/conversation data.
        print("AI Usage Monitor: quota data unavailable")
        return 1


if __name__ == "__main__":
    sys.exit(main())
