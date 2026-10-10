"""Local storage and quota adapters. No credential or conversation collection."""
from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import time

VERSION = "2.2.0"


def data_dir() -> Path:
    override = os.environ.get("AI_USAGE_MONITOR_DATA")
    if override:
        return Path(override)
    return Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local/share")) / "AIUsageMonitorV2"


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def number(value, minimum=0, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(value) or value < minimum or (maximum is not None and value > maximum):
        return None
    return value


def window(name, raw, percent_key="usedPercent", reset_key="resetsAt"):
    if not isinstance(raw, dict):
        return None
    return {
        "name": name,
        "used": number(raw.get(percent_key), maximum=100),
        "reset": number(raw.get(reset_key), maximum=253402300799),
        "minutes": number(raw.get("windowDurationMins")),
    }


def codex_snapshot(result, now=None):
    if not isinstance(result, dict):
        raise ValueError("Invalid rate limit response")
    buckets = result.get("rateLimitsByLimitId")
    if not isinstance(buckets, dict) or not buckets:
        legacy = result.get("rateLimits")
        buckets = {(legacy.get("limitId") or "codex"): legacy} if isinstance(legacy, dict) else {}
    rows = []
    for key, bucket in buckets.items():
        if not isinstance(bucket, dict):
            continue
        for slot in ("primary", "secondary"):
            item = window(str(key) + ":" + slot, bucket.get(slot))
            if item:
                rows.append(item)
    return {"provider": "codex", "observed_at": now or time.time(), "windows": rows}


def claude_snapshot(payload, now=None):
    if not isinstance(payload, dict):
        raise ValueError("Invalid status line data")
    limits = payload.get("rate_limits")
    limits = limits if isinstance(limits, dict) else {}
    rows = []
    for name in ("five_hour", "seven_day", "spend_limit"):
        item = window(name, limits.get(name), "used_percentage", "resets_at")
        if item:
            rows.append(item)
    cost = payload.get("cost")
    cost = cost if isinstance(cost, dict) else {}
    # Explicit allowlist: never persist the raw payload, transcript paths or session IDs.
    return {
        "provider": "claude", "observed_at": now or time.time(), "windows": rows,
        "session_estimate_usd": number(cost.get("total_cost_usd")),
    }


def quota_state(row, observed_at, now=None, stale_after=300):
    now = time.time() if now is None else now
    reset = row.get("reset")
    if reset is not None and reset <= now:
        return "expired"
    if now - observed_at > stale_after or observed_at > now + 60:
        return "stale"
    if row.get("used") is None:
        return "unknown"
    return "current"


class QuotaAlerts:
    """One alert per descending threshold, per provider/window/reset cycle."""
    def __init__(self, saved=None):
        self.state = dict(saved) if isinstance(saved, dict) else {}

    def check(self, snapshot, now=None):
        now = time.time() if now is None else now
        observed = number(snapshot.get('observed_at'))
        provider = snapshot.get('provider')
        if observed is None or provider not in ('codex', 'claude'):
            return []
        events = []
        for row in snapshot.get('windows', []):
            used = number(row.get('used'), maximum=100)
            reset = number(row.get('reset'), maximum=253402300799)
            if used is None or quota_state(dict(row, reset=reset), observed, now) != 'current':
                continue
            name = row.get('name')
            if not isinstance(name, str):
                continue
            key = provider + '/' + name
            remaining = 100 - used
            old = self.state.get(key, {})
            if not isinstance(old, dict):
                old = {}
            old_observed = number(old.get('observed'))
            if old_observed is not None and observed < old_observed:
                continue
            previous_reset = number(old.get('reset'))
            # Ignore small timestamp drift; actual new windows re-arm alerts.
            new_cycle = (previous_reset is not None and previous_reset <= now)
            if reset is not None and previous_reset is not None and abs(reset - previous_reset) > 60:
                new_cycle = True
            if reset is None and previous_reset is None and remaining > 50:
                new_cycle = True
            lowest = number(old.get('lowest'), maximum=101)
            lowest = 101 if new_cycle or lowest is None else lowest
            threshold = next((t for t in (10, 20, 50) if remaining <= t), None)
            if threshold is not None and threshold < lowest:
                events.append({'provider':provider, 'row':row, 'remaining':remaining, 'threshold':threshold})
                lowest = threshold
            cycle_reset = reset if new_cycle or previous_reset is None else previous_reset
            self.state[key] = {'reset':cycle_reset, 'lowest':lowest, 'observed':observed}
        # Bound metadata growth when providers rename or retire limit buckets.
        if len(self.state) > 128:
            self.state = {k:v for k,v in self.state.items() if isinstance(v,dict) and
                          number(v.get('observed')) is not None and v['observed'] >= now - 86400*14}
        return events


class History:
    def __init__(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS snapshots (provider TEXT, observed REAL, data TEXT, PRIMARY KEY(provider, observed))")

    def save(self, snapshot):
        self.db.execute("INSERT OR REPLACE INTO snapshots VALUES (?,?,?)", (
            snapshot["provider"], snapshot["observed_at"], json.dumps(snapshot, allow_nan=False)))
        self.db.execute("DELETE FROM snapshots WHERE observed < ?", (time.time() - 90 * 86400,))
        self.db.commit()

    def latest(self, provider):
        row = self.db.execute("SELECT data FROM snapshots WHERE provider=? ORDER BY observed DESC LIMIT 1", (provider,)).fetchone()
        return json.loads(row[0]) if row else None

    def export(self, path):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["provider", "observed_at_utc", "window", "used_percent", "reset_epoch", "session_estimate_usd"])
            for provider, observed, raw in self.db.execute("SELECT * FROM snapshots ORDER BY observed"):
                snap = json.loads(raw)
                for row in snap["windows"] or [{}]:
                    # Text comes from upstream, so neutralize spreadsheet formulas.
                    name = str(row.get("name", ""))
                    if name.startswith(("=", "+", "-", "@")):
                        name = "'" + name
                    writer.writerow([provider, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(observed)), name,
                                     row.get("used"), row.get("reset"), snap.get("session_estimate_usd")])


def find_codex():
    direct = shutil.which("codex.exe") or shutil.which("codex")
    if direct and Path(direct).suffix.lower() not in (".cmd", ".bat"):
        return direct
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    candidates = list((local / "OpenAI/Codex/bin").glob("*/codex.exe"))
    npm = Path(os.environ.get("APPDATA", "")) / "npm/node_modules/@openai"
    candidates += list(npm.glob("codex*/**/codex.exe"))
    return str(max(candidates, key=lambda p: p.stat().st_mtime)) if candidates else ""


def claude_settings_path():
    return Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "settings.json"


class BridgeSettings:
    """Own only statusLine; preserve all other settings and never overwrite later edits."""
    def __init__(self, root=None, settings_path=None):
        self.root = Path(root) if root else data_dir()
        self.ledger = self.root / "claude-bridge.json"
        self.settings_path = Path(settings_path) if settings_path else claude_settings_path()

    def _settings(self, path=None):
        settings = read_json(path or self.settings_path)
        if not isinstance(settings, dict):
            raise ValueError("Claude settings must be a JSON object")
        return settings

    def active(self):
        record = read_json(self.ledger)
        return bool(record and self._settings(Path(record["path"])).get("statusLine") == record["installed"])

    def enable(self, command, replace=False):
        settings = self._settings()
        installed = {"type": "command", "command": command, "padding": 0}
        old_record = read_json(self.ledger)
        if old_record:
            if Path(old_record["path"]) != self.settings_path:
                raise ValueError("Restore the previous bridge before changing the Claude settings location")
            if settings.get("statusLine") == old_record["installed"]:
                record = old_record
                record["installed"] = installed
            else:
                if not replace:
                    raise FileExistsError("statusLine changed")
                record = {"path": str(self.settings_path), "had_previous": "statusLine" in settings,
                          "previous": settings.get("statusLine"), "installed": installed}
        else:
            if "statusLine" in settings and not replace:
                raise FileExistsError("statusLine already configured")
            record = {"path": str(self.settings_path), "had_previous": "statusLine" in settings,
                      "previous": settings.get("statusLine"), "installed": installed}
        # Write recovery information first. A failed settings write remains recoverable.
        atomic_json(self.ledger, record)
        settings["statusLine"] = installed
        atomic_json(self.settings_path, settings)

    def disable(self):
        record = read_json(self.ledger)
        if not record:
            return True
        target = Path(record["path"])
        settings = self._settings(target)
        if settings.get("statusLine") != record["installed"]:
            # Another application/user changed it. Keep their setting and our backup.
            return False
        if record["had_previous"]:
            settings["statusLine"] = record["previous"]
        else:
            settings.pop("statusLine", None)
        atomic_json(target, settings)
        self.ledger.unlink()
        return True
