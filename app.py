from __future__ import annotations

import argparse
import base64
import hashlib
from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys
import time

from core import (BridgeSettings, History, VERSION, atomic_json, data_dir, find_codex,
                  quota_state, read_json)
from i18n import tr


def bridge_command():
    if getattr(sys, "frozen", False):
        exe = Path(sys.executable).with_name("UsageBridge.exe")
        if not exe.is_file():
            raise FileNotFoundError("UsageBridge.exe")
        args = [str(exe)]
    else:
        args = [sys.executable, str(Path(__file__).with_name("claude_bridge.py"))]
    # The same command works under Git Bash and PowerShell. All variable paths
    # are single-quoted PowerShell literals inside a UTF-16 encoded command.
    quoted = " ".join("'" + arg.replace("'", "''") + "'" for arg in args)
    script = ("$OutputEncoding = New-Object System.Text.UTF8Encoding($false); "
              "[Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false); "
              "$payload = [Console]::In.ReadToEnd(); $payload | & " + quoted + "; exit $LASTEXITCODE")
    encoded = base64.b64encode(script.encode("utf-16le")).decode("ascii")
    return "powershell.exe -NoProfile -NonInteractive -EncodedCommand " + encoded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=["zh", "en"])
    parser.add_argument("--set-language", choices=["zh", "en"])
    parser.add_argument("--disconnect-claude", action="store_true")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")
    parser.add_argument("--snapshot")
    opts = parser.parse_args()
    root = data_dir()
    root.mkdir(parents=True, exist_ok=True)
    if opts.set_language:
        settings = read_json(root / "settings.json")
        settings["language"] = opts.set_language
        atomic_json(root / "settings.json", settings)
        return 0
    if opts.disconnect_claude:
        try:
            BridgeSettings(root).disable()
            return 0
        except (OSError, ValueError, KeyError):
            return 1

    from PySide6.QtCore import QEvent, QLibraryInfo, QLockFile, QLocale, Qt, QTimer, QTranslator, QUrl
    from PySide6.QtNetwork import QLocalServer, QLocalSocket
    from PySide6.QtGui import QColor, QDesktopServices, QFont, QFontDatabase, QIcon, QPainter, QPixmap
    from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
        QDoubleSpinBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
        QMainWindow, QMessageBox, QProgressBar, QPushButton, QScrollArea,
        QSizePolicy, QVBoxLayout, QWidget)
    from codex_client import CodexClient
    from desktop import DesktopController

    app = QApplication(sys.argv[:1])
    app.setApplicationName("AI Usage Monitor")
    app.setApplicationVersion(VERSION)
    # Explicitly load OS fonts so offscreen rendering also has CJK glyphs.
    if app.platformName() == "offscreen":
        for name in ("segoeui.ttf", "msyh.ttc"):
            font_path = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / name
            if font_path.exists():
                QFontDatabase.addApplicationFont(str(font_path))
    families = QFontDatabase.families()
    app.setFont(QFont("Microsoft YaHei" if "Microsoft YaHei" in families else "Segoe UI", 10))
    mutex = None
    if os.name == "nt" and not opts.smoke_test:
        import ctypes
        ctypes.windll.kernel32.CreateMutexW.restype = ctypes.c_void_p
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "AIUsageMonitorV2")
    lock = QLockFile(str(root / "app.lock"))
    server_name = "AIUsageMonitor-" + hashlib.sha256(str(root.resolve()).casefold().encode()).hexdigest()[:24]
    if not lock.tryLock(100):
        socket = QLocalSocket()
        socket.connectToServer(server_name)
        if socket.waitForConnected(800):
            socket.write(b"show")
            socket.waitForBytesWritten(500)
            socket.disconnectFromServer()
            return 0
        QMessageBox.information(None, "AI Usage Monitor", "程序已在运行。\nThe app is already running.")
        return 0
    icon_path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "assets" / "app.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    app.setStyleSheet('''
        QMainWindow, QScrollArea, QWidget#page { background: #F2F5F7; }
        QWidget { color: #172B3A; font-family: "Segoe UI", "Microsoft YaHei UI"; font-size: 14px; }
        QFrame#card { background: #FFFFFF; border: 1px solid #DFE6EA; border-radius: 16px; }
        QLabel { background: transparent; border: none; }
        QLabel#title { font-size: 30px; font-weight: 700; }
        QLabel#provider { font-size: 21px; font-weight: 650; }
        QLabel#muted { color: #637985; }
        QLabel#pill { color: #087D71; background: #E7F5EF; border-radius: 9px; padding: 6px 12px; }
        QLabel#section { font-size: 17px; font-weight: 600; }
        QPushButton { background: white; border: 1px solid #CEDAE0; border-radius: 8px; padding: 9px 15px; }
        QPushButton:hover { background: #EDF5F5; border-color: #6CAFA5; }
        QPushButton:disabled { color: #9AAAB3; background: #F2F5F7; }
        QPushButton#primary { color: white; background: #087D71; border: none; font-weight: 600; }
        QPushButton#primary:hover { background: #09695F; }
        QComboBox, QDoubleSpinBox { background: white; border: 1px solid #CEDAE0; border-radius: 7px; padding: 7px; }
        QComboBox::drop-down { width: 22px; border: 0; }
        QProgressBar { height: 8px; max-height: 8px; border: 0; border-radius: 4px; background: #E9EFF1; }
        QProgressBar::chunk { background: #149B88; border-radius: 4px; }
        QScrollArea { border: none; }
        QDialog { background: #F7F9FA; }
        QToolTip { color: #172B3A; background: white; border: 1px solid #CCD8DD; padding: 4px; }
    ''')

    class Window(QMainWindow):
        def __init__(self):
            super().__init__()
            self.root = root
            try:
                self.settings = read_json(root / "settings.json")
                if not isinstance(self.settings, dict):
                    raise ValueError()
            except (OSError, ValueError):
                self.settings = {}
            default_language = "zh" if QLocale.system().name().startswith("zh") else "en"
            self.lang = opts.lang or self.settings.get("language", default_language)
            if self.lang not in ("zh", "en"):
                self.lang = default_language
            self.translator = QTranslator(self)
            self.set_qt_language()
            self.bridge = BridgeSettings(root)
            self.history = History(root / "history.sqlite3")
            self.snapshots = {p: self.history.latest(p) for p in ("codex", "claude")}
            self.states = {"codex": "not_connected", "claude": "not_connected"}
            self.plan = ""
            self.claude_mtime = None
            self.client = CodexClient(root, self.settings.get("codex_executable") or find_codex(), self)
            self.client.status.connect(self.codex_status)
            self.client.account_changed.connect(self.account_changed)
            self.client.snapshot.connect(self.receive)
            self.client.browser_login.connect(lambda url: QDesktopServices.openUrl(QUrl(url)))
            self.resize(1120, 930)
            self.setMinimumSize(820, 660)
            self.cards = {}
            self.cleaned_up = False
            if opts.demo:
                now = time.time()
                self.states = {"codex": "connected", "claude": "received"}
                self.snapshots = {
                    "codex": {"provider": "codex", "observed_at": now, "windows": [
                        {"name": "codex:primary", "minutes": 300, "used": 36, "reset": now + 6840},
                        {"name": "codex:secondary", "minutes": 10080, "used": 61, "reset": now + 228000}]},
                    "claude": {"provider": "claude", "observed_at": now - 42, "session_estimate_usd": 0.83, "windows": [
                        {"name": "five_hour", "minutes": None, "used": 24, "reset": now + 11200},
                        {"name": "seven_day", "minutes": None, "used": 48, "reset": now + 331200}]}}
            self.build()
            self.desktop = DesktopController(self, self.t, self.settings, self.persist_desktop,
                                             demo=opts.demo, smoke=opts.smoke_test)
            app.setQuitOnLastWindowClosed(False)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.local_tick)
            self.timer.start(5000)
            self.poll = QTimer(self)
            self.poll.timeout.connect(self.client.refresh)
            if not (opts.demo or opts.smoke_test):
                self.poll.start(60000)
                QTimer.singleShot(100, self.client.start)
            self.local_tick()

        def persist_desktop(self):
            try:
                self.save_settings()
            except OSError:
                self.show_error("file_error")

        def t(self, key, **kwargs):
            return tr(self.lang, key, **kwargs)

        def label(self, text, kind="", wrap=False):
            w = QLabel(text)
            w.setTextFormat(Qt.PlainText)
            w.setWordWrap(wrap)
            if kind:
                w.setObjectName(kind)
            return w

        def button(self, key, fn, primary=False):
            w = QPushButton(self.t(key))
            if primary:
                w.setObjectName("primary")
            w.clicked.connect(fn)
            return w

        def build(self):
            self.setWindowTitle(self.t("title") + " · " + VERSION)
            old = self.takeCentralWidget()
            if old:
                old.hide()
                old.deleteLater()
            page = QWidget()
            page.setObjectName("page")
            layout = QVBoxLayout(page)
            layout.setContentsMargins(30, 26, 30, 24)
            layout.setSpacing(18)
            head = QHBoxLayout()
            titles = QVBoxLayout()
            titles.addWidget(self.label(self.t("title") + "  /  02", "title"))
            titles.addWidget(self.label(self.t("subtitle"), "muted"))
            head.addLayout(titles)
            head.addStretch()
            languages = QComboBox()
            languages.addItem("简体中文", "zh")
            languages.addItem("English", "en")
            languages.setAccessibleName(self.t("language"))
            languages.setCurrentIndex(0 if self.lang == "zh" else 1)
            languages.currentIndexChanged.connect(lambda _: self.switch_language(languages.currentData()))
            head.addWidget(languages)
            layout.addLayout(head)
            if opts.demo:
                layout.addWidget(self.label(self.t("demo"), "pill"))
            toolbar = QHBoxLayout()
            toolbar.addWidget(self.label(self.t("overview"), "section"))
            toolbar.addStretch()
            toolbar.addWidget(self.button("floating", lambda: self.desktop.toggle_floating()))
            toolbar.addWidget(self.button("export", self.export))
            toolbar.addWidget(self.button("refresh", self.refresh, True))
            layout.addLayout(toolbar)
            for provider in ("codex", "claude"):
                frame = QFrame()
                frame.setObjectName("card")
                card = QVBoxLayout(frame)
                card.setContentsMargins(22, 19, 22, 20)
                card.setSpacing(12)
                top = QHBoxLayout()
                top.addWidget(self.label("Codex" if provider == "codex" else "Claude Code", "provider"))
                top.addStretch()
                status = self.label("", "pill")
                status.setMaximumWidth(430)
                status.setWordWrap(True)
                top.addWidget(status)
                card.addLayout(top)
                card.addWidget(self.label(self.t(provider + "_hint"), "muted", True))
                if provider == "codex":
                    card.addWidget(self.label(self.t("session_hint"), "muted", True))
                content = QWidget()
                content_layout = QVBoxLayout(content)
                content_layout.setContentsMargins(0, 4, 0, 4)
                content_layout.setSpacing(12)
                card.addWidget(content)
                bottom = QHBoxLayout()
                updated = self.label("", "muted")
                bottom.addWidget(updated)
                bottom.addStretch()
                if provider == "codex":
                    cancel = self.button("cancel_login", self.client.cancel_login)
                    bottom.addWidget(cancel)
                    logout = self.button("disconnect", self.client.logout)
                    bottom.addWidget(logout)
                    login = self.button("connect", self.login, True)
                    bottom.addWidget(login)
                else:
                    bottom.addWidget(self.button("claude_login", self.claude_guide))
                    toggle = self.button("enable", self.toggle_bridge, True)
                    bottom.addWidget(toggle)
                card.addLayout(bottom)
                self.cards[provider] = {"status": status, "content": content_layout, "updated": updated}
                if provider == "codex":
                    self.cards[provider].update(login=login, logout=logout, cancel=cancel)
                else:
                    self.cards[provider]["toggle"] = toggle
                layout.addWidget(frame)
            fees_frame = QFrame()
            fees_frame.setObjectName("card")
            fees = QVBoxLayout(fees_frame)
            fees.setContentsMargins(22, 17, 22, 17)
            fee_head = QHBoxLayout()
            fee_head.addWidget(self.label(self.t("fees"), "section"))
            fee_head.addStretch()
            fee_head.addWidget(self.button("edit_fees", self.edit_fees))
            fees.addLayout(fee_head)
            self.fee_label = self.label("")
            fees.addWidget(self.fee_label)
            fees.addWidget(self.label(self.t("fee_hint"), "muted", True))
            layout.addWidget(fees_frame)
            settings_row = QHBoxLayout()
            settings_row.addWidget(self.button("choose_codex", self.choose_codex))
            settings_row.addWidget(self.button("codex_docs", lambda: QDesktopServices.openUrl(QUrl("https://developers.openai.com/codex/cli/"))))
            settings_row.addStretch()
            layout.addLayout(settings_row)
            desktop_row = QHBoxLayout()
            tray_mode = QCheckBox(self.t("tray_mode"))
            tray_mode.setChecked(self.settings.get("close_to_tray", True))
            tray_mode.toggled.connect(lambda enabled: self.desktop.tray_action.setChecked(enabled))
            self.tray_checkbox = tray_mode
            desktop_row.addWidget(tray_mode)
            desktop_row.addStretch()
            desktop_row.addWidget(self.button("exit_app", lambda: self.desktop.quit()))
            layout.addLayout(desktop_row)
            self.alerts_checkbox = QCheckBox(self.t('quota_alerts'))
            self.alerts_checkbox.setChecked(self.settings.get('quota_alerts_enabled', True))
            self.alerts_checkbox.toggled.connect(lambda enabled: self.desktop.alert_action.setChecked(enabled))
            layout.addWidget(self.alerts_checkbox)
            layout.addWidget(self.label(self.t('quota_alert_hint'), 'muted', True))
            layout.addWidget(self.label(self.t("footer"), "muted", True))
            layout.addStretch()
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(page)
            self.setCentralWidget(scroll)
            self.render()

        def save_settings(self):
            atomic_json(root / "settings.json", self.settings)

        def switch_language(self, language):
            self.settings["language"] = language
            try:
                self.save_settings()
            except OSError:
                self.show_error("file_error")
                return
            # Apply on the next launch so Qt starts with one consistent native
            # translation/font context. The installer uses the same preference.
            if not opts.smoke_test and language != self.lang:
                QMessageBox.information(self, tr(language, "title"), tr(language, "language_saved"))

        def set_qt_language(self):
            app.removeTranslator(self.translator)
            if self.lang == "zh":
                bundled = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "assets" / "qtbase_zh_CN.qm"
                fallback = Path(QLibraryInfo.path(QLibraryInfo.TranslationsPath)) / "qtbase_zh_CN.qm"
                if self.translator.load(str(bundled if bundled.exists() else fallback)):
                    app.installTranslator(self.translator)

        def show_error(self, key):
            QMessageBox.warning(self, self.t("error"), self.t(key))

        def codex_status(self, key):
            self.states["codex"] = key
            self.render()

        def account_changed(self, plan):
            self.plan = plan
            self.render()

        def receive(self, snapshot):
            self.snapshots[snapshot["provider"]] = snapshot
            if hasattr(self, 'desktop'):
                self.desktop.check_quota(snapshot, self.window_name)
            try:
                self.history.save(snapshot)
            except (OSError, sqlite3.Error):
                # The UI remains usable if a database is locked; surface it once.
                if not getattr(self, "storage_error_shown", False):
                    self.storage_error_shown = True
                    self.show_error("file_error")
            self.render()

        def local_tick(self):
            if opts.demo:
                self.render()
                return
            try:
                active = self.bridge.active()
                self.states["claude"] = "waiting" if active else "not_connected"
                file = root / "claude-latest.json"
                if active and file.exists():
                    modified = file.stat().st_mtime_ns
                    if modified != self.claude_mtime:
                        snap = read_json(file)
                        if (snap.get("provider") != "claude" or not isinstance(snap.get("windows"), list)
                                or not isinstance(snap.get("observed_at"), (int, float))):
                            raise ValueError()
                        self.receive(snap)
                        self.claude_mtime = modified
                    self.states["claude"] = "received"
            except (OSError, ValueError, KeyError, TypeError):
                self.states["claude"] = "bridge_error"
            self.render()

        def window_name(self, row):
            name = row["name"]
            if name in ("five_hour", "seven_day", "spend_limit"):
                return self.t(name)
            bucket, _, slot = name.rpartition(":")
            minutes = row.get("minutes")
            if minutes:
                if minutes % 1440 == 0:
                    label = self.t("days", n=f"{minutes / 1440:g}")
                elif minutes % 60 == 0:
                    label = self.t("hours", n=f"{minutes / 60:g}")
                else:
                    label = self.t("minutes", n=f"{minutes:g}")
            else:
                label = self.t(slot) if slot in ("primary", "secondary") else name
            return label if bucket in ("", "codex") else bucket + " · " + label

        def render(self):
            for provider, card in self.cards.items():
                key = self.states[provider]
                card["status"].setText(self.t(key))
                content = card["content"]
                while content.count():
                    item = content.takeAt(0)
                    if item.widget():
                        item.widget().hide()
                        item.widget().deleteLater()
                snap = self.snapshots[provider]
                observed = snap["observed_at"] if snap else None
                if observed:
                    card["updated"].setText(self.t("updated", time=datetime.fromtimestamp(observed).astimezone().strftime("%m-%d %H:%M:%S %z")))
                else:
                    card["updated"].setText(self.t("never"))
                if not snap or not snap["windows"]:
                    empty = self.label(self.t("no_data") + "\n" + self.t("no_data_hint"), "muted", True)
                    empty.setMinimumHeight(58)
                    content.addWidget(empty)
                else:
                    for row in snap["windows"]:
                        line = QWidget()
                        grid = QGridLayout(line)
                        grid.setContentsMargins(0, 0, 0, 0)
                        grid.setHorizontalSpacing(18)
                        grid.setColumnStretch(0, 2)
                        grid.setColumnStretch(1, 2)
                        grid.setColumnStretch(2, 3)
                        state = quota_state(row, observed)
                        if state == "current" and key not in ("connected", "received"):
                            state = "stale"
                        used = row.get("used")
                        label = self.window_name(row)
                        if state == "stale":
                            label += " · " + self.t("stale")
                        grid.addWidget(self.label(label), 0, 0)
                        valid = used is not None and state != "expired"
                        percent = f"{used:g}%" if valid else "—"
                        grid.addWidget(self.label(self.t("used") + "  " + percent), 0, 1)
                        remaining = f"{100-used:g}%" if valid else "—"
                        grid.addWidget(self.label(self.t("remaining") + "  " + remaining, "muted"), 0, 2)
                        progress = QProgressBar()
                        progress.setRange(0, 1000)
                        progress.setValue(round(used * 10) if valid else 0)
                        progress.setTextVisible(False)
                        progress.setAccessibleName(self.t("used") + " " + percent)
                        if state != "current":
                            progress.setStyleSheet("QProgressBar::chunk { background: #A9B8C0; }")
                        elif used is not None and used >= 85:
                            progress.setStyleSheet("QProgressBar::chunk { background: #D89737; }")
                        grid.addWidget(progress, 1, 0, 1, 2)
                        if state == "expired":
                            reset = self.t("expired")
                        elif row.get("reset") is None:
                            reset = self.t("reset") + ": " + self.t("unknown")
                        else:
                            minutes = max(0, int((row["reset"] - time.time()) / 60))
                            stamp = datetime.fromtimestamp(row["reset"]).astimezone().strftime("%m-%d %H:%M %z")
                            reset = self.t("reset") + ": " + stamp + " · " + self.t("countdown", h=minutes // 60, m=minutes % 60)
                        grid.addWidget(self.label(reset, "muted", True), 1, 2)
                        content.addWidget(line)
                if provider == "claude" and snap and snap.get("session_estimate_usd") is not None:
                    content.addWidget(self.label(self.t("estimate", amount=f"{snap['session_estimate_usd']:.2f}"), "muted", True))
                if provider == "codex":
                    card["cancel"].setVisible(key == "signing_in")
                    card["login"].setVisible(key not in ("connected", "signing_in", "restoring", "connecting") and not self.client.account)
                    card["logout"].setVisible(bool(self.client.account))
                    card["login"].setEnabled(not opts.demo)
                else:
                    card["toggle"].setText(self.t("disable" if key in ("waiting", "received") else "enable"))
                    card["toggle"].setEnabled(not opts.demo)
            fees = self.settings.get("fees", {})
            parts = []
            for provider, title in (("codex", "Codex"), ("claude", "Claude Code")):
                fee = fees.get(provider)
                parts.append(title + "   " + (f"{fee['amount']:.2f} {fee['currency']}" if fee else "—"))
            if hasattr(self, "fee_label"):
                self.fee_label.setText("          /          ".join(parts))
            if hasattr(self, "desktop"):
                self.desktop.floating.update_usage(self.snapshots, self.states, self.window_name)

        def login(self):
            self.client.start(login=True)

        def refresh(self):
            if not opts.demo:
                self.client.refresh()
            self.local_tick()

        def choose_codex(self):
            file, _ = QFileDialog.getOpenFileName(self, self.t("choose_codex"), "", "Codex (codex.exe)")
            if not file:
                return
            self.client.close()
            self.client.timer.start()
            self.client.executable = file
            self.settings["codex_executable"] = file
            try:
                self.save_settings()
            except OSError:
                self.show_error("file_error")
            self.client.start()

        def claude_guide(self):
            box = QMessageBox(self)
            box.setWindowTitle(self.t("setup_title"))
            box.setText(self.t("setup_body"))
            docs = box.addButton(self.t("open_docs"), QMessageBox.ActionRole)
            box.addButton(QMessageBox.Close)
            box.exec()
            if box.clickedButton() == docs:
                QDesktopServices.openUrl(QUrl("https://code.claude.com/docs/en/quickstart"))

        def toggle_bridge(self):
            try:
                if self.bridge.active():
                    if not self.bridge.disable():
                        QMessageBox.information(self, self.t("title"), self.t("changed"))
                else:
                    try:
                        self.bridge.enable(bridge_command())
                    except FileExistsError:
                        box = QMessageBox(self)
                        box.setWindowTitle(self.t("replace_title"))
                        box.setText(self.t("replace_body"))
                        accept = box.addButton(self.t("enable"), QMessageBox.AcceptRole)
                        box.addButton(self.t("cancel"), QMessageBox.RejectRole)
                        box.exec()
                        if box.clickedButton() != accept:
                            return
                        self.bridge.enable(bridge_command(), replace=True)
                    self.claude_guide()
                self.local_tick()
            except (OSError, ValueError, KeyError):
                self.show_error("bridge_error")

        def edit_fees(self):
            dialog = QDialog(self)
            dialog.setWindowTitle(self.t("fees"))
            layout = QVBoxLayout(dialog)
            layout.addWidget(self.label(self.t("fee_hint"), "muted", True))
            grid = QGridLayout()
            values = {}
            for i, (provider, title) in enumerate((("codex", "Codex"), ("claude", "Claude Code"))):
                fee = self.settings.get("fees", {}).get(provider, {})
                grid.addWidget(self.label(title), i, 0)
                amount = QDoubleSpinBox()
                amount.setRange(-1, 1000000)
                amount.setDecimals(2)
                amount.setSpecialValueText(self.t("unknown"))
                amount.setValue(fee.get("amount", -1))
                amount.setAccessibleName(self.t("amount"))
                currency = QComboBox()
                currency.addItems(["USD", "GBP", "EUR", "CNY", "HKD", "JPY", "CAD", "AUD"])
                currency.setCurrentText(fee.get("currency", "USD"))
                currency.setAccessibleName(self.t("currency"))
                grid.addWidget(amount, i, 1)
                grid.addWidget(currency, i, 2)
                values[provider] = (amount, currency)
            layout.addLayout(grid)
            buttons = QDialogButtonBox()
            buttons.addButton(self.t("save"), QDialogButtonBox.AcceptRole)
            buttons.addButton(self.t("cancel"), QDialogButtonBox.RejectRole)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            if dialog.exec() == QDialog.Accepted:
                self.settings["fees"] = {p: {"amount": a.value(), "currency": c.currentText()}
                                         for p, (a, c) in values.items() if a.value() >= 0}
                try:
                    self.save_settings()
                except OSError:
                    self.show_error("file_error")
                self.render()

        def export(self):
            file, _ = QFileDialog.getSaveFileName(self, self.t("export"), "AIUsageHistory.csv", "CSV (*.csv)")
            if file:
                try:
                    self.history.export(file)
                    QMessageBox.information(self, self.t("title"), self.t("exported"))
                except OSError:
                    self.show_error("file_error")

        def changeEvent(self, event):
            super().changeEvent(event)
            if event.type() == QEvent.WindowStateChange and self.isMinimized() and hasattr(self, "desktop"):
                QTimer.singleShot(0, lambda: self.desktop.hide_main() if self.isMinimized() else None)

        def cleanup(self):
            if self.cleaned_up:
                return
            self.cleaned_up = True
            self.timer.stop()
            self.poll.stop()
            self.desktop.shutdown()
            self.client.close()
            self.history.db.close()

        def closeEvent(self, event):
            if self.desktop.hide_main():
                event.ignore()
                return
            self.cleanup()
            event.accept()
            app.quit()

    window = Window()
    app.aboutToQuit.connect(window.cleanup)
    server = QLocalServer()
    server.setSocketOptions(QLocalServer.UserAccessOption)
    QLocalServer.removeServer(server_name)
    server.listen(server_name)
    def incoming():
        while server.hasPendingConnections():
            connection = server.nextPendingConnection()
            window.desktop.show_main()
            connection.disconnectFromServer()
            connection.deleteLater()
    server.newConnection.connect(incoming)
    window.show()
    if opts.smoke_test:
        def finish_smoke():
            # Exercise the actual main-window lifecycle with a simulated tray
            # availability fallback; no real account calls are made in this mode.
            desktop = window.desktop
            can_tray = desktop.can_tray
            native_tray = desktop.tray.isSystemTrayAvailable()
            if native_tray:
                desktop.smoke = False
                desktop.tray.show()
                assert desktop.can_tray()
            else:
                desktop.can_tray = lambda: True
            desktop.notified = True
            window.showMinimized()
            app.processEvents()
            app.processEvents()
            assert not window.isVisible() and not window.cleaned_up
            desktop.show_main()
            window.close()
            assert not window.isVisible() and not window.cleaned_up
            desktop.show_main()
            assert window.isVisible()
            desktop.can_tray = can_tray
            desktop.smoke = True
            desktop.set_floating(True)
            floating = desktop.floating
            floating.update_usage(window.snapshots, window.states, window.window_name)
            floating.dock_nearest()
            assert floating.collapsed and floating.width() == 20
            floating.expand()
            assert not floating.collapsed and floating.width() == 320
            floating.ensure_visible()
            assert floating.area().contains(floating.geometry())
            if opts.snapshot:
                from PySide6.QtTest import QTest
                QTest.qWait(150)
                # Layered translucent windows cannot be captured by Win32 BitBlt.
                preview = floating.grab()
                preview.save(str(Path(opts.snapshot).with_name(Path(opts.snapshot).stem + '_floating.png')))
                desktop.menu.popup(window.pos())
                QTest.qWait(500)
                menu_preview = desktop.menu.grab()
                menu_preview.save(str(Path(opts.snapshot).with_name(Path(opts.snapshot).stem + '_menu.png')))
                desktop.menu.hide()
            desktop.set_floating(False)
            assert not floating.isVisible()
            # Restore the default preference for this isolated test profile.
            window.settings['floating_enabled'] = True
            # Exercise both translations, then restore the requested language.
            original = window.lang
            alternate = "en" if original == "zh" else "zh"
            window.switch_language(alternate)
            assert read_json(root / "settings.json")["language"] == alternate
            def capture():
                if opts.snapshot:
                    if app.platformName() == "windows":
                        # Capture this app's native client window. QWidget.grab
                        # can clip cached glyphs after a language change on Qt 6.10.
                        window.screen().grabWindow(window.winId()).save(opts.snapshot)
                    else:
                        window.grab().save(opts.snapshot)
                atomic_json(root / "smoke-result.json", {"ok": True, "language": window.lang, "version": VERSION,
                                                         "providers": sorted(window.cards), "demo": opts.demo, "language_preference_test": True,
                                                         "tray_close_restore_test": True, "floating_dock_test": True})
                window.close()
                app.quit()
            def restore_language():
                window.switch_language(original)
                QTimer.singleShot(250, capture)
            # Verify preference persistence independently from the initial UI language.
            QTimer.singleShot(250, restore_language)
        QTimer.singleShot(800, finish_smoke)
    result = app.exec()
    server.close()
    lock.unlock()
    if mutex:
        ctypes.windll.kernel32.CloseHandle(ctypes.c_void_p(mutex))
    return result


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback
        try:
            folder = data_dir()
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "startup-error.log").write_text(traceback.format_exc(), encoding="utf-8")
        except OSError:
            pass
        if "--smoke-test" not in sys.argv and os.name == "nt":
            import ctypes
            ctypes.windll.user32.MessageBoxW(None,
                "程序无法启动。错误详情保存在数据目录的 startup-error.log。\n"
                "Unable to start. See startup-error.log in the app data folder.", "AI Usage Monitor", 16)
        sys.exit(1)
