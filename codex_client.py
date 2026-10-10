"""Nonblocking, read-only Codex App Server integration over stdio."""
import json
from pathlib import Path
import time
from urllib.parse import urlparse

from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, QTimer, Signal
from core import VERSION, codex_snapshot, find_codex


class CodexClient(QObject):
    status = Signal(str)
    snapshot = Signal(dict)
    browser_login = Signal(str)
    account_changed = Signal(str)

    def __init__(self, root, executable="", parent=None):
        super().__init__(parent)
        self.root = Path(root)
        self.executable = executable
        self.process = None
        self.sequence = 0
        self.pending = {}
        self.buffer = bytearray()
        self.ready = False
        self.login_id = None
        self.login_deadline = None
        self.login_requested = False
        self.want_login = False
        self.account = None
        self.closing = False
        self.auth_recovery_attempted = False
        self.reauth_required = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def start(self, login=False):
        self.want_login = self.want_login or login
        if self.process and self.process.state() != QProcess.NotRunning:
            if self.ready and login:
                if self.reauth_required:
                    self.begin_login()
                elif self.account:
                    self.want_login = False
                    self.refresh()
                else:
                    self.read_account()
            return
        if not self.executable or not Path(self.executable).is_file():
            self.executable = find_codex()
        if not self.executable or not Path(self.executable).is_file():
            self.status.emit("missing_codex")
            self.want_login = False
            return
        self.closing = False
        self.timer.start(1000)
        self.auth_recovery_attempted = False
        self.ready = False
        self.pending.clear()
        self.buffer.clear()
        home = self.root / "codex-home"
        home.mkdir(parents=True, exist_ok=True)
        p = QProcess(self)
        self.process = p
        env = QProcessEnvironment.systemEnvironment()
        # An independent official CLI profile: no copying of another app's tokens.
        env.insert("CODEX_HOME", str(home))
        for variable in ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL"):
            env.remove(variable)
        p.setProcessEnvironment(env)
        p.setWorkingDirectory(str(self.root))
        p.setProgram(self.executable)
        p.setArguments(["app-server"])
        p.started.connect(self.initialize)
        p.readyReadStandardOutput.connect(self.read_output)
        p.readyReadStandardError.connect(lambda: p.readAllStandardError())
        p.errorOccurred.connect(self.process_error)
        p.finished.connect(self.process_finished)
        self.status.emit("restoring")
        p.start()

    def process_error(self, _error):
        self.ready = False
        if not self.closing:
            self.status.emit("offline")

    def process_finished(self, *_args):
        self.ready = False
        self.pending.clear()
        self.login_id = None
        self.login_deadline = None
        if not self.closing:
            self.status.emit("offline")

    def send(self, method, params=None, callback=None):
        if not self.process or self.process.state() != QProcess.Running:
            return
        message = {"method": method}
        if params is not None:
            message["params"] = params
        if callback is not None:
            self.sequence += 1
            message["id"] = self.sequence
            self.pending[self.sequence] = (time.monotonic() + 30, method, callback)
        self.process.write((json.dumps(message) + "\n").encode("utf-8"))

    def initialize(self):
        self.send("initialize", {"clientInfo": {"name": "ai_usage_monitor", "title": "AI Usage Monitor", "version": VERSION}}, self.initialized)

    def initialized(self, result, error):
        if error:
            self.status.emit("offline")
            if self.process:
                self.process.kill()
            return
        self.send("initialized")
        self.ready = True
        # Check the official client's persisted session before opening a browser,
        # including when the user clicks sign-in during startup.
        self.read_account()

    def read_account(self, refresh_token=False):
        if not any(m == "account/read" for _, m, _ in self.pending.values()):
            self.send("account/read", {"refreshToken": refresh_token}, self.got_account)

    def got_account(self, result, error):
        if error:
            if self.auth_recovery_attempted and any(x in str(error).lower() for x in ('401','unauthorized','token','authentication')):
                self.reauth_required = True
                self.account = None
                self.account_changed.emit("")
            self.status.emit("offline")
            return
        account = result.get("account") if isinstance(result, dict) else None
        self.account = account
        if not account:
            self.status.emit("not_connected")
            self.account_changed.emit("")
            if self.want_login:
                self.begin_login()
        elif account.get("type") == "apiKey":
            self.status.emit("api_key")
        else:
            self.want_login = False
            self.account_changed.emit(str(account.get("planType") or ""))
            self.refresh()

    def begin_login(self):
        self.want_login = False
        if self.login_deadline or any(m == "account/login/start" for _, m, _ in self.pending.values()):
            return
        self.status.emit("signing_in")
        self.login_requested = True
        self.send("account/login/start", {"type": "chatgpt"}, self.login_started)

    def login_started(self, result, error):
        if not self.login_requested:
            if isinstance(result, dict) and result.get("loginId"):
                self.send("account/login/cancel", {"loginId": result["loginId"]}, lambda *_: None)
            return
        if error or not isinstance(result, dict):
            self.status.emit("login_failed")
            return
        url = result.get("authUrl", "")
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in ("auth.openai.com", "chatgpt.com", "auth0.openai.com"):
            self.status.emit("login_failed")
            return
        self.login_id = result.get("loginId")
        self.login_deadline = time.monotonic() + 300
        self.browser_login.emit(url)

    def cancel_login(self):
        if self.login_id:
            self.send("account/login/cancel", {"loginId": self.login_id}, lambda *_: None)
        self.login_id = None
        self.login_deadline = None
        self.want_login = False
        self.login_requested = False
        self.status.emit("not_connected")

    def logout(self):
        self.cancel_login()
        if self.ready:
            self.send("account/logout", {}, self.logged_out)

    def logged_out(self, result, error):
        if error:
            self.status.emit("offline")
        else:
            self.account = None
            self.account_changed.emit("")
            self.status.emit("not_connected")

    def refresh(self):
        if self.reauth_required:
            self.status.emit("offline")
            return
        if not self.ready:
            self.start()
        elif not self.login_deadline and not any(m == "account/rateLimits/read" for _, m, _ in self.pending.values()):
            if not self.account:
                if not any(m == "account/read" for _, m, _ in self.pending.values()):
                    self.read_account()
            else:
                self.send("account/rateLimits/read", {}, self.got_limits)

    def got_limits(self, result, error):
        if error:
            # Ask the official client to renew an expired session once. Never
            # open a login page automatically or read/handle credentials ourselves.
            message = str(error).lower()
            if not self.auth_recovery_attempted and any(x in message for x in
                    ("401", "unauthorized", "token expired", "token_expired", "authentication")):
                self.auth_recovery_attempted = True
                self.status.emit("restoring")
                self.read_account(refresh_token=True)
                return
            if self.auth_recovery_attempted and any(x in message for x in ("401", "unauthorized", "token expired", "token_expired", "authentication")):
                self.reauth_required = True
                self.account = None
                self.account_changed.emit("")
            self.status.emit("offline")
            return
        try:
            snap = codex_snapshot(result)
        except (ValueError, TypeError):
            self.status.emit("offline")
            return
        self.status.emit("connected")
        self.snapshot.emit(snap)

    def read_output(self):
        self.buffer.extend(bytes(self.process.readAllStandardOutput()))
        if len(self.buffer) > 2 * 1024 * 1024:
            self.buffer.clear()
            self.status.emit("offline")
            return
        while b"\n" in self.buffer:
            raw, _, rest = self.buffer.partition(b"\n")
            self.buffer = bytearray(rest)
            try:
                message = json.loads(raw)
                if isinstance(message, dict):
                    self.dispatch(message)
            except (ValueError, TypeError, KeyError):
                self.status.emit("offline")

    def dispatch(self, message):
        if "id" in message and ("result" in message or "error" in message):
            entry = self.pending.pop(message["id"], None)
            if entry:
                entry[2](message.get("result", {}), message.get("error"))
            return
        method = message.get("method")
        params = message.get("params") or {}
        if method == "account/login/completed":
            if not self.login_id or params.get("loginId") != self.login_id:
                return
            self.login_id = None
            self.login_deadline = None
            self.login_requested = False
            if params.get("success"):
                self.reauth_required = False
                self.auth_recovery_attempted = False
                self.read_account()
            else:
                self.status.emit("login_failed")
        elif method == "account/rateLimits/updated" and self.account:
            self.got_limits(params, None)
        elif method == "account/updated" and not self.login_deadline:
            self.read_account()

    def tick(self):
        now = time.monotonic()
        for request_id, (deadline, method, callback) in list(self.pending.items()):
            if deadline < now:
                self.pending.pop(request_id, None)
                callback({}, {"code": "timeout"})
        if self.login_deadline and self.login_deadline < now:
            self.cancel_login()
            self.status.emit("login_failed")

    def close(self):
        self.closing = True
        self.timer.stop()
        if self.process:
            self.process.kill()
            self.process.waitForFinished(2000)
