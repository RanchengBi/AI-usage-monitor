import tempfile
import time
import unittest

from PySide6.QtCore import QCoreApplication
from codex_client import CodexClient

APP = QCoreApplication.instance() or QCoreApplication([])


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.client = CodexClient(self.tmp.name)
        self.states = []
        self.client.status.connect(self.states.append)

    def tearDown(self):
        self.client.close()
        self.tmp.cleanup()

    def test_request_response_ids(self):
        got = []
        self.client.pending[12] = (time.monotonic() + 10, "test", lambda r,e: got.append((r,e)))
        self.client.dispatch({"id": 11, "result": {"wrong": True}})
        self.assertFalse(got)
        self.client.dispatch({"id": 12, "result": {"right": True}})
        self.assertEqual(got, [({"right": True}, None)])
        self.assertFalse(self.client.pending)

    def test_timeout(self):
        got = []
        self.client.pending[3] = (0, "test", lambda r,e: got.append(e))
        self.client.tick()
        self.assertEqual(got, [{"code": "timeout"}])
        self.assertFalse(self.client.pending)

    def test_login_url_validation(self):
        self.client.login_requested = True
        urls = []
        self.client.browser_login.connect(urls.append)
        self.client.login_started({"authUrl": "https://evil.example/", "loginId": "x"}, None)
        self.assertEqual(self.states[-1], "login_failed")
        self.assertFalse(urls)
        self.client.login_started({"authUrl": "https://auth.openai.com/oauth/authorize", "loginId": "x"}, None)
        self.assertEqual(len(urls), 1)

    def test_cancel_before_start_response_does_not_open_browser(self):
        urls = []
        self.client.browser_login.connect(urls.append)
        self.client.login_requested = True
        self.client.cancel_login()
        self.client.login_started({"authUrl": "https://auth.openai.com/oauth/authorize", "loginId": "late"}, None)
        self.assertFalse(urls)

    def test_login_completion_must_match(self):
        calls = []
        self.client.read_account = lambda: calls.append(True)
        self.client.login_id = "current"
        self.client.dispatch({"method": "account/login/completed", "params": {"loginId": "old", "success": True}})
        self.assertFalse(calls)
        self.client.dispatch({"method": "account/login/completed", "params": {"loginId": "current", "success": True}})
        self.assertTrue(calls)

    def test_cancel_ignores_late_login(self):
        calls = []
        self.client.read_account = lambda: calls.append(True)
        self.client.login_id = "old"
        self.client.cancel_login()
        self.client.dispatch({"method": "account/login/completed", "params": {"loginId": "old", "success": True}})
        self.assertFalse(calls)

    def test_limits_notification_and_error(self):
        received = []
        self.client.account = {"type": "chatgpt"}
        self.client.snapshot.connect(received.append)
        self.client.dispatch({"method": "account/rateLimits/updated", "params": {"rateLimits": {"primary": {"usedPercent": 42}}}})
        self.assertEqual(received[0]["windows"][0]["used"], 42)
        self.client.got_limits({}, {"code": 401})
        self.assertEqual(self.states[-1], "restoring")
        self.client.got_limits({}, {"code": 401})
        self.assertEqual(self.states[-1], "offline")
        self.assertEqual(len(received), 1)

    def test_startup_checks_saved_session_before_browser(self):
        calls = []
        self.client.want_login = True
        self.client.send = lambda method, *args: calls.append(method)
        self.client.initialized({}, None)
        self.assertEqual(calls, ['initialized', 'account/read'])
        self.assertNotIn('account/login/start', calls)

    def test_saved_account_reused_without_login(self):
        calls = []
        self.client.want_login = True
        self.client.refresh = lambda: calls.append('refresh')
        self.client.begin_login = lambda: calls.append('login')
        self.client.got_account({'account':{'type':'chatgpt','planType':'pro'}}, None)
        self.assertEqual(calls, ['refresh'])
        self.assertFalse(self.client.want_login)

    def test_missing_account_prompts_only_after_user_request(self):
        calls = []
        self.client.begin_login = lambda: calls.append('login')
        self.client.got_account({'account':None}, None)
        self.assertEqual(calls, [])
        self.client.want_login = True
        self.client.got_account({'account':None}, None)
        self.assertEqual(calls, ['login'])

    def test_expired_token_recovery_is_bounded(self):
        calls = []
        self.client.read_account = lambda refresh_token=False: calls.append(refresh_token)
        self.client.got_limits({}, {'code':401})
        self.client.got_limits({}, {'code':401})
        self.assertEqual(calls, [True])
        self.assertEqual(self.states[-1], 'offline')

    def test_closing_never_logs_out(self):
        calls = []
        self.client.send = lambda method, *args: calls.append(method)
        self.client.close()
        self.assertNotIn('account/logout', calls)


if __name__ == '__main__':
    unittest.main()
