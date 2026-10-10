import json
from pathlib import Path
import tempfile
import time
import unittest

from core import (BridgeSettings, History, atomic_json, claude_snapshot, codex_snapshot,
                  number, quota_state, read_json)
from i18n import TEXT, tr


class QuotaTests(unittest.TestCase):
    def test_codex_legacy(self):
        snap = codex_snapshot({"rateLimits": {"primary": {"usedPercent": 0, "resetsAt": 999, "windowDurationMins": 300}}}, 100)
        self.assertEqual(snap["windows"][0]["used"], 0)
        self.assertEqual(snap["windows"][0]["minutes"], 300)

    def test_multiple_buckets_do_not_double_count_legacy(self):
        snap = codex_snapshot({"rateLimits": {"primary": {"usedPercent": 80}}, "rateLimitsByLimitId": {
            "codex": {"primary": {"usedPercent": 30}, "secondary": {"usedPercent": 45}},
            "other": {"primary": {"usedPercent": 20}}}})
        self.assertEqual([w["used"] for w in snap["windows"]], [30, 45, 20])

    def test_missing_is_not_zero(self):
        self.assertEqual(codex_snapshot({})["windows"], [])
        self.assertIsNone(codex_snapshot({"rateLimits": {"primary": {}}})["windows"][0]["used"])
        self.assertEqual(claude_snapshot({"rate_limits": None})["windows"], [])

    def test_invalid_numbers(self):
        for value in (True, False, "10", float("nan"), float("inf"), -1, 101):
            self.assertIsNone(number(value, maximum=100))

    def test_claude_allowlist(self):
        snap = claude_snapshot({"session_id": "SECRET", "transcript_path": "PRIVATE", "cwd": "HIDDEN",
            "rate_limits": {"five_hour": {"used_percentage": 12, "resets_at": 900}},
            "cost": {"total_cost_usd": 0.12}, "access_token": "TOKEN"}, 100)
        self.assertEqual(snap["windows"][0]["used"], 12)
        self.assertEqual(snap["session_estimate_usd"], 0.12)
        for private in ("SECRET", "PRIVATE", "HIDDEN", "TOKEN"):
            self.assertNotIn(private, json.dumps(snap))

    def test_stale_and_expired(self):
        self.assertEqual(quota_state({"used": 10, "reset": 99}, 90, now=100), "expired")
        self.assertEqual(quota_state({"used": 10, "reset": 9999}, 100, now=500), "stale")
        self.assertEqual(quota_state({"used": None}, 100, now=101), "unknown")
        self.assertEqual(quota_state({"used": 0}, 100, now=101), "current")
        self.assertEqual(quota_state({"used": 1}, 500, now=100), "stale")

    def test_translations(self):
        for key, values in TEXT.items():
            self.assertEqual(len(values), 2)
            import string
            fields = lambda text: {f for _, f, _, _ in string.Formatter().parse(text) if f}
            self.assertEqual(fields(values[0]), fields(values[1]), key)
            self.assertTrue(all(values), key)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.path = self.root / "claude/settings.json"
        self.bridge = BridgeSettings(self.root / "monitor", self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_enable_restore_preserves_unrelated_fields(self):
        original = {"statusLine": {"type": "command", "command": "old"}, "theme": "dark", "permissions": {"allow": []}}
        atomic_json(self.path, original)
        with self.assertRaises(FileExistsError):
            self.bridge.enable("monitor")
        self.bridge.enable("monitor", replace=True)
        self.assertTrue(self.bridge.active())
        updated = read_json(self.path)
        updated["theme"] = "light"
        atomic_json(self.path, updated)
        self.assertTrue(self.bridge.disable())
        original["theme"] = "light"
        self.assertEqual(read_json(self.path), original)

    def test_repeated_enable_keeps_original_backup(self):
        atomic_json(self.path, {"statusLine": {"command": "old"}})
        self.bridge.enable("one", replace=True)
        self.bridge.enable("two")
        self.bridge.disable()
        self.assertEqual(read_json(self.path)["statusLine"], {"command": "old"})

    def test_external_change_not_overwritten(self):
        self.bridge.enable("one")
        atomic_json(self.path, {"statusLine": {"command": "new external"}})
        self.assertFalse(self.bridge.disable())
        self.assertTrue(self.bridge.ledger.exists())
        self.assertEqual(read_json(self.path)["statusLine"]["command"], "new external")

    def test_first_install_restore_removes_only_status_line(self):
        self.bridge.enable("one")
        self.bridge.disable()
        self.assertEqual(read_json(self.path), {})

    def test_invalid_json_remains_untouched(self):
        self.path.parent.mkdir()
        self.path.write_text("{bad", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.bridge.enable("one")
        self.assertEqual(self.path.read_text(), "{bad")

    def test_history_roundtrip_and_csv_formula_safety(self):
        db = History(self.root / "history.db")
        try:
            snap = {"provider": "codex", "observed_at": time.time(), "windows": [
                {"name": "=FORMULA()", "used": 0, "reset": None}]}
            db.save(snap)
            db.save(snap)
            self.assertEqual(db.latest("codex"), snap)
            out = self.root / "export.csv"
            db.export(out)
            self.assertIn("'=FORMULA()", out.read_text(encoding="utf-8-sig"))
            self.assertEqual(db.db.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0], 1)
        finally:
            db.db.close()


if __name__ == '__main__':
    unittest.main()
