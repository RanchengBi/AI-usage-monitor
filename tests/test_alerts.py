import json
import unittest
from core import QuotaAlerts


def sample(remaining, reset=2000, name='codex:primary', provider='codex', observed=1000):
    return {'provider':provider, 'observed_at':observed, 'windows':[
        {'name':name, 'minutes':300, 'used':None if remaining is None else 100-remaining, 'reset':reset}]}


class AlertTests(unittest.TestCase):
    def test_each_threshold_and_no_repeat(self):
        alerts = QuotaAlerts()
        for remaining, expected in [(51,[]),(50,[50]),(49,[]),(20,[20]),(15,[]),(10,[10]),(0,[])]:
            self.assertEqual([e['threshold'] for e in alerts.check(sample(remaining),1000)], expected)

    def test_skipped_thresholds_only_emit_most_urgent(self):
        alerts = QuotaAlerts()
        self.assertEqual([e['threshold'] for e in alerts.check(sample(8),1000)], [10])
        self.assertEqual(alerts.check(sample(8),1000), [])

    def test_restart_preserves_deduplication(self):
        alerts = QuotaAlerts()
        alerts.check(sample(19),1000)
        restored = QuotaAlerts(json.loads(json.dumps(alerts.state)))
        self.assertEqual(restored.check(sample(19),1000), [])
        self.assertEqual(restored.check(sample(10),1000)[0]['threshold'],10)

    def test_five_hour_weekly_and_providers_independent(self):
        alerts = QuotaAlerts()
        for provider in ('codex','claude'):
            for name in ('five_hour','seven_day'):
                self.assertEqual(len(alerts.check(sample(20,name=name,provider=provider),1000)),1)
                self.assertEqual(alerts.check(sample(20,name=name,provider=provider),1000),[])

    def test_new_reset_cycle_rearms(self):
        alerts = QuotaAlerts()
        alerts.check(sample(10),1000)
        self.assertEqual(alerts.check(sample(20,reset=4000,observed=2001),2001)[0]['threshold'],20)

    def test_small_reset_drift_does_not_repeat(self):
        alerts = QuotaAlerts()
        alerts.check(sample(10),1000)
        self.assertEqual(alerts.check(sample(10,reset=2001),1000),[])

    def test_missing_reset_recovers_above_fifty(self):
        alerts = QuotaAlerts()
        alerts.check(sample(10,reset=None),1000)
        alerts.check(sample(90,reset=None),1000)
        self.assertEqual(alerts.check(sample(50,reset=None),1000)[0]['threshold'],50)

    def test_same_cycle_fluctuation_does_not_repeat(self):
        alerts = QuotaAlerts()
        alerts.check(sample(20),1000)
        alerts.check(sample(60),1000)
        self.assertEqual(alerts.check(sample(20),1000),[])

    def test_stale_expired_missing_future_invalid_ignored(self):
        for snap in (sample(10,observed=600),sample(10,reset=999),sample(None),
                     sample(10,observed=1100),sample(-5),sample(110)):
            alerts = QuotaAlerts()
            self.assertEqual(alerts.check(snap,1000),[])
            self.assertEqual(alerts.state,{})

    def test_older_response_cannot_rearm(self):
        alerts = QuotaAlerts()
        alerts.check(sample(10,reset=4000,observed=1100),1100)
        self.assertEqual(alerts.check(sample(20,reset=2000,observed=1000),1100),[])

    def test_multiple_windows_in_one_response(self):
        snap = sample(20)
        snap['windows'] += sample(50,name='codex:secondary')['windows']
        self.assertEqual(len(QuotaAlerts().check(snap,1000)),2)


if __name__ == '__main__':
    unittest.main()
