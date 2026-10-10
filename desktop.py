"""Tray and edge-docking UI. Stores geometry/preferences, never account data."""
from PySide6.QtCore import QObject, QPoint, QRect, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPen
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel, QMenu,
                              QPushButton, QSystemTrayIcon, QVBoxLayout, QWidget)
from core import QuotaAlerts, quota_state


def clamp_position(point, size, area):
    return QPoint(max(area.left(), min(point.x(), area.right() - size.width() + 1)),
                  max(area.top(), min(point.y(), area.bottom() - size.height() + 1)))


def select_screen(screens, rect, preferred=None):
    """Keep a dock on its screen; otherwise use the largest visible overlap.

    Never select a screen using the center of a just-resized edge tab: that
    center can cross into a neighboring monitor before the window is repositioned.
    """
    if preferred in screens:
        return preferred
    def overlap(screen):
        intersection = screen.availableGeometry().intersected(rect)
        return intersection.width() * intersection.height() if not intersection.isEmpty() else 0
    return max(screens, key=overlap)


class DragHeader(QLabel):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.window().begin_drag(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.window().drag_to(event.globalPosition().toPoint())
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.window().finish_drag()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        self.window().open_main.emit()


class FloatingWindow(QWidget):
    open_main = Signal()
    hide_requested = Signal()
    position_saved = Signal(dict)

    def __init__(self, t, saved=None, demo=False):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.t = t
        self.edge = None
        self.collapsed = False
        self.drag_origin = None
        self._anchor_screen = None
        self.setObjectName('floating')
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(t('mini_title'))
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setStyleSheet('QWidget#floating QWidget {background:transparent; color:#D4DBDF;} '
                           'QWidget#floating QPushButton {background:transparent; color:#9EABB2; '
                           'border:none; padding:3px 7px; border-radius:9px;} '
                           'QWidget#floating QPushButton:hover {background:#3E484F; color:#EEF2F4;} '
                           'QWidget#floating QLabel {font-size:12px; border:none;}')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        self.panel = QWidget()
        body = QVBoxLayout(self.panel)
        body.setContentsMargins(0, 0, 0, 0)
        header = QHBoxLayout()
        self.handle = DragHeader(t('mini_title') + (' · ' + t('mini_demo') if demo else ''))
        self.handle.setCursor(Qt.SizeAllCursor)
        self.handle.setToolTip(t('float_hint'))
        self.handle.setStyleSheet('color:#9BA9B1; font-size:11px;')
        header.addWidget(self.handle, 1)
        for text, key, callback in [('↗', 'show_main', self.open_main.emit),
                                    ('‹', 'collapse', self.dock_nearest),
                                    ('×', 'hide_float', self.hide_requested.emit)]:
            button = QPushButton(text)
            button.setToolTip(t(key))
            button.setAccessibleName(t(key))
            button.clicked.connect(callback)
            header.addWidget(button)
        body.addLayout(header)
        self.labels = {}
        for provider, title in [('codex', 'Codex'), ('claude', 'Claude Code')]:
            title_label = QLabel(title)
            title_label.setStyleSheet('font-weight:600;color:#9CBDB7;')
            body.addWidget(title_label)
            label = QLabel(t('mini_empty'))
            label.setWordWrap(True)
            label.setTextFormat(Qt.PlainText)
            self.labels[provider] = label
            body.addWidget(label)
        layout.addWidget(self.panel)
        self.tab = QLabel('')
        self.tab.setAlignment(Qt.AlignCenter)
        self.tab.setToolTip(t('float_hint'))
        self.tab.hide()
        layout.addWidget(self.tab)
        self.fold_timer = QTimer(self)
        self.fold_timer.setSingleShot(True)
        self.fold_timer.timeout.connect(self.collapse)
        self.setFixedSize(320, 208)
        area = QGuiApplication.primaryScreen().availableGeometry()
        saved = saved if isinstance(saved, dict) else {}
        x, y = saved.get('x'), saved.get('y')
        point = QPoint(x, y) if type(x) is int and type(y) is int else QPoint(area.right()-340, area.top()+90)
        self.move(point)
        self.edge = saved.get('edge') if saved.get('edge') in ('left', 'right') else None
        screens = QGuiApplication.screens()
        matches = [screen for screen in screens if screen.name() == saved.get('screen')]
        # Geometry disambiguates identical monitor names; no hardware serial is stored.
        preferred = next((screen for screen in matches if
            list(screen.geometry().getRect()) == saved.get('screen_geometry')), None)
        if preferred is None and len(matches) == 1:
            preferred = matches[0]
        self._anchor_screen = select_screen(screens, self.geometry(), preferred if self.edge else None)
        self.ensure_visible()
        self.setWindowOpacity(0.97)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(200, 214, 222, 32), 1))
        painter.setBrush(QColor(40, 47, 53, 238) if self.collapsed else QColor(33, 40, 46, 248))
        rect = QRectF(self.rect()).adjusted(.5, .5, -.5, -.5)
        radius = 10 if self.collapsed else 18
        painter.drawRoundedRect(rect, radius, radius)
        if self.collapsed:
            # A quiet grip instead of the old bright white AI badge.
            painter.setPen(QPen(QColor(167, 189, 188, 180), 2, Qt.SolidLine, Qt.RoundCap))
            x, y = self.width()/2, self.height()/2
            painter.drawLine(QPoint(round(x), round(y-9)), QPoint(round(x), round(y+9)))

    def area(self):
        self._anchor_screen = select_screen(QGuiApplication.screens(), self.geometry(),
                                           self._anchor_screen if self.edge else None)
        return self._anchor_screen.availableGeometry()

    def ensure_visible(self, *_):
        area = self.area()
        position = clamp_position(self.pos(), self.size(), area)
        if self.edge:
            position.setX(area.left() if self.edge == 'left' else area.right()-self.width()+1)
        self.move(position)

    def remember(self):
        # Save expanded geometry, even when only the tab is visible.
        x = self.x()
        if self.edge == 'right':
            x = self.area().right() - 320 + 1
        self.area()
        self.position_saved.emit({'x':x, 'y':self.y(), 'edge':self.edge,
                                  'screen':self._anchor_screen.name(),
                                  'screen_geometry':list(self._anchor_screen.geometry().getRect())})

    def begin_drag(self, point):
        self.fold_timer.stop()
        self.expand()
        self.edge = None
        self.drag_origin = point - self.pos()

    def drag_to(self, point):
        if self.drag_origin is not None:
            self.move(point - self.drag_origin)

    def finish_drag(self):
        if self.drag_origin is None:
            return
        self.drag_origin = None
        area = self.area()
        if self.x() <= area.left()+24:
            self.edge = 'left'
        elif self.x()+self.width() >= area.right()-24:
            self.edge = 'right'
        self.ensure_visible()
        self.remember()
        if self.edge:
            self.fold_timer.start(800)

    def dock_nearest(self):
        self.edge = 'left' if self.geometry().center().x() < self.area().center().x() else 'right'
        self.ensure_visible()
        self.collapse()
        self.remember()

    def collapse(self):
        if not self.edge or self.drag_origin is not None:
            return
        # Capture the dock's screen BEFORE changing width (especially at a seam).
        self.area()
        self.collapsed = True
        self.panel.hide()
        self.tab.show()
        self.layout().setContentsMargins(2, 8, 2, 8)
        self.setFixedSize(20, 68)
        self.ensure_visible()
        self.setWindowOpacity(0.78)
        self.update()

    def expand(self):
        if not self.collapsed:
            return
        # Lock to the original screen before expansion can cross its boundary.
        self.area()
        self.collapsed = False
        self.tab.hide()
        self.panel.show()
        self.layout().setContentsMargins(16, 12, 16, 12)
        self.setFixedSize(320, 208)
        self.ensure_visible()
        self.setWindowOpacity(0.97)
        self.update()

    def enterEvent(self, event):
        self.fold_timer.stop()
        self.expand()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.edge and self.drag_origin is None:
            self.fold_timer.start(800)
        super().leaveEvent(event)

    def closeEvent(self, event):
        event.ignore()
        self.hide_requested.emit()

    def update_usage(self, snapshots, states, window_name):
        for provider, label in self.labels.items():
            snap = snapshots.get(provider)
            if not snap or not snap.get('windows'):
                label.setText(self.t(states[provider]) if states[provider] not in ('connected', 'received') else self.t('mini_empty'))
                continue
            parts = []
            for row in snap['windows']:
                state = quota_state(row, snap['observed_at'])
                if state == 'current' and states[provider] not in ('connected', 'received'):
                    state = 'stale'
                value = '—' if row.get('used') is None or state == 'expired' else f"{100-row['used']:g}%"
                suffix = ' · ' + self.t(state) if state in ('stale', 'expired') else ''
                parts.append(window_name(row)+' '+self.t('remaining')+' '+value+suffix)
            # Full quota list remains available without silently hiding freshness.
            text = '\n'.join(parts)
            label.setToolTip(text)
            label.setText('\n'.join(parts[:2]) + (' …' if len(parts)>2 else ''))


class DesktopController(QObject):
    def __init__(self, window, t, settings, persist, demo=False, smoke=False):
        super().__init__(window)
        self.window, self.t, self.settings, self.persist = window, t, settings, persist
        self.smoke = smoke
        self.quitting = False
        self.notified = False
        self.alerts_suppressed = demo or smoke
        self.alerts = QuotaAlerts(settings.get('quota_alert_state'))
        self.floating = FloatingWindow(t, settings.get('floating_position'), demo)
        self.floating.open_main.connect(self.show_main)
        self.floating.hide_requested.connect(lambda: self.set_floating(False))
        self.floating.position_saved.connect(self.save_position)
        self.tray = QSystemTrayIcon(QApplication.windowIcon(), self)
        self.tray.setToolTip(t('title'))
        self.menu = QMenu()
        # Global QWidget text colors otherwise leak into the native dark menu.
        self.menu.setStyleSheet('''
            QMenu { background:#252D33; color:#EFF3F5; border:1px solid #56616A;
                    padding:6px 0; font-size:14px; }
            QMenu::item { padding:8px 24px 8px 30px; background:transparent; color:#EFF3F5; }
            QMenu::item:selected { background:#3E5359; color:#FFFFFF; }
            QMenu::item:disabled { color:#99A5AD; }
            QMenu::separator { height:1px; background:#4C5860; margin:5px 12px; }
            QMenu::indicator { width:12px; height:12px; margin-left:9px;
                               border:1px solid #8D9DA5; border-radius:3px; }
            QMenu::indicator:checked { background:#70CBB8; border-color:#70CBB8; }
            QMenu::indicator:unchecked { background:transparent; }
        ''')
        self.menu.addAction(t('show_main'), self.show_main)
        self.float_action = self.menu.addAction(t('floating'))
        self.float_action.setCheckable(True)
        self.float_action.setChecked(settings.get('floating_enabled', True))
        self.float_action.toggled.connect(self.set_floating)
        self.tray_action = self.menu.addAction(t('tray_mode'))
        self.tray_action.setCheckable(True)
        self.tray_action.setChecked(settings.get('close_to_tray', True))
        self.tray_action.toggled.connect(self.set_tray_mode)
        self.alert_action = self.menu.addAction(t('quota_alerts'))
        self.alert_action.setCheckable(True)
        self.alert_action.setChecked(settings.get('quota_alerts_enabled', True))
        self.alert_action.toggled.connect(self.set_alerts_enabled)
        self.menu.addAction(t('refresh'), window.refresh)
        self.menu.addSeparator()
        self.menu.addAction(t('exit_app'), self.quit)
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.activated)
        self.tray.messageClicked.connect(self.show_main)
        self.floating.setContextMenuPolicy(Qt.CustomContextMenu)
        self.floating.customContextMenuRequested.connect(lambda point: self.menu.exec(self.floating.mapToGlobal(point)))
        if not smoke and QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()
        if settings.get('floating_enabled', True) and not smoke:
            self.floating.show()
            if self.floating.edge:
                self.floating.collapse()
        QApplication.instance().screenRemoved.connect(self.floating.ensure_visible)
        QApplication.instance().screenAdded.connect(self.watch_screen)
        for screen in QApplication.screens():
            self.watch_screen(screen)

    def watch_screen(self, screen):
        screen.availableGeometryChanged.connect(self.floating.ensure_visible)
        screen.geometryChanged.connect(self.floating.ensure_visible)
        self.floating.ensure_visible()

    def set_alerts_enabled(self, enabled):
        self.settings['quota_alerts_enabled'] = bool(enabled)
        if hasattr(self.window, 'alerts_checkbox'):
            self.window.alerts_checkbox.setChecked(bool(enabled))
        self.persist()

    def check_quota(self, snapshot, window_name):
        if (self.alerts_suppressed or not self.settings.get('quota_alerts_enabled', True)
                or not self.tray.isVisible() or not QSystemTrayIcon.supportsMessages()):
            return
        events = self.alerts.check(snapshot)
        if events:
            lines = [self.t('quota_alert_line', provider='Codex' if e['provider']=='codex' else 'Claude Code',
                            window=window_name(e['row']), remaining=f"{e['remaining']:g}") for e in events]
            self.tray.showMessage(self.t('quota_alert_title'), '\n'.join(lines), QSystemTrayIcon.Warning, 10000)
        # Persist deduplication across restarts, without account identifiers.
        if self.settings.get('quota_alert_state') != self.alerts.state:
            self.settings['quota_alert_state'] = {k:dict(v) for k,v in self.alerts.state.items()}
            self.persist()

    def save_position(self, position):
        self.settings['floating_position'] = position
        self.persist()

    def set_floating(self, enabled):
        enabled = bool(enabled)
        self.settings['floating_enabled'] = enabled
        self.float_action.blockSignals(True)
        self.float_action.setChecked(enabled)
        self.float_action.blockSignals(False)
        self.floating.setVisible(enabled)
        if enabled:
            self.floating.ensure_visible()
        self.persist()

    def toggle_floating(self):
        self.set_floating(not self.floating.isVisible())

    def set_tray_mode(self, enabled):
        self.settings['close_to_tray'] = bool(enabled)
        if hasattr(self.window, 'tray_checkbox'):
            self.window.tray_checkbox.setChecked(bool(enabled))
        self.persist()

    def can_tray(self):
        return (not self.smoke and not self.quitting and self.settings.get('close_to_tray', True)
                and QSystemTrayIcon.isSystemTrayAvailable() and self.tray.isVisible())

    def hide_main(self):
        if not self.can_tray():
            return False
        self.window.hide()
        if not self.notified:
            self.tray.showMessage(self.t('title'), self.t('tray_hint'), QSystemTrayIcon.Information, 3500)
            self.notified = True
        return True

    def show_main(self):
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()

    def activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_main()

    def quit(self):
        self.quitting = True
        self.window.close()
        QApplication.instance().quit()

    def shutdown(self):
        self.quitting = True
        self.floating.fold_timer.stop()
        self.floating.hide()
        self.tray.hide()
