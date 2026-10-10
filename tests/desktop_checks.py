"""Run separately: python tests/desktop_checks.py (requires a GUI platform)."""
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QPoint, QRect, QSize
from PySide6.QtWidgets import QApplication, QMainWindow
from desktop import DesktopController, FloatingWindow, clamp_position, select_screen
from i18n import tr

APP = QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)


class Monitor:
    def __init__(self, name, rect):
        self._name, self._rect = name, rect
    def name(self):
        return self._name
    def geometry(self):
        return QRect(self._rect)
    def availableGeometry(self):
        return QRect(self._rect)


class DesktopTests(unittest.TestCase):
    def setUp(self):
        self.floating = FloatingWindow(lambda k: tr('en', k), {'x':-99999,'y':99999})

    def tearDown(self):
        self.floating.hide()
        self.floating.deleteLater()
        APP.processEvents()

    def test_offscreen_position_recovered(self):
        self.assertTrue(self.floating.area().contains(self.floating.geometry()))

    def test_negative_coordinate_screen(self):
        point = clamp_position(QPoint(-9999,9999), QSize(320,208), QRect(-1920,0,1920,1080))
        self.assertEqual(point, QPoint(-1920,872))

    def test_left_and_right_docking_and_expansion(self):
        for edge in ('left','right'):
            self.floating.edge = edge
            self.floating.collapse()
            self.assertTrue(self.floating.collapsed)
            self.assertEqual(self.floating.width(),20)
            self.assertTrue(self.floating.area().contains(self.floating.geometry()))
            self.floating.expand()
            self.assertEqual(self.floating.width(),320)
            self.assertTrue(self.floating.area().contains(self.floating.geometry()))

    def test_drag_undocks_and_remembers(self):
        saved = []
        self.floating.position_saved.connect(saved.append)
        self.floating.edge = 'right'
        self.floating.begin_drag(self.floating.pos()+QPoint(10,10))
        self.assertIsNone(self.floating.edge)
        self.floating.drag_to(self.floating.area().center())
        self.floating.finish_drag()
        self.assertTrue(saved)
        self.assertTrue(self.floating.area().contains(self.floating.geometry()))

    def test_expired_and_stale_quota_not_shown_as_fresh(self):
        now = time.time()
        sample = {'observed_at':now-900,'windows':[{'name':'week','used':30,'reset':now+900}]}
        self.floating.update_usage({'codex':sample,'claude':None},
                                   {'codex':'connected','claude':'waiting'},lambda row:row['name'])
        self.assertIn('Stale',self.floating.labels['codex'].text())
        sample['windows'][0]['reset'] = now-1
        self.floating.update_usage({'codex':sample,'claude':None},
                                   {'codex':'connected','claude':'waiting'},lambda row:row['name'])
        self.assertNotIn('70%',self.floating.labels['codex'].text())

    def test_preferences_and_tray_fallback(self):
        window = QMainWindow()
        window.refresh = lambda: None
        settings, saves = {}, []
        controller = DesktopController(window,lambda k:tr('en',k),settings,lambda:saves.append(True),smoke=True)
        self.assertFalse(controller.can_tray())
        controller.set_floating(True)
        self.assertTrue(controller.floating.isVisible())
        controller.set_floating(False)
        self.assertFalse(settings['floating_enabled'])
        controller.set_tray_mode(False)
        self.assertFalse(settings['close_to_tray'])
        self.assertTrue(saves)
        controller.shutdown()
        controller.floating.deleteLater()
        window.deleteLater()

    def test_quota_notification_delivery_toggle_and_restart(self):
        window = QMainWindow()
        window.refresh = lambda: None
        settings, saves = {}, []
        controller = DesktopController(window,lambda k,**kw:tr('en',k,**kw),settings,lambda:saves.append(True),smoke=True)
        try:
            controller.alerts_suppressed = False
            controller.tray = Mock()
            controller.tray.isVisible.return_value = True
            snap = {'provider':'codex','observed_at':time.time(),'windows':[
                {'name':'primary','minutes':300,'used':80,'reset':time.time()+900},
                {'name':'secondary','minutes':10080,'used':50,'reset':time.time()+9000}]}
            with patch('desktop.QSystemTrayIcon.supportsMessages',return_value=True):
                controller.check_quota(snap,lambda row:'5 hours' if row['minutes']==300 else '7 days')
                self.assertEqual(controller.tray.showMessage.call_count,1)
                body = controller.tray.showMessage.call_args.args[1]
                self.assertIn('5 hours: 20% remaining',body)
                self.assertIn('7 days: 50% remaining',body)
                controller.check_quota(snap,lambda row:row['name'])
                self.assertEqual(controller.tray.showMessage.call_count,1)
                controller.alert_action.setChecked(False)
                snap['windows'][0]['used'] = 90
                controller.check_quota(snap,lambda row:row['name'])
                self.assertEqual(controller.tray.showMessage.call_count,1)
                controller.alert_action.setChecked(True)
                controller.check_quota(snap,lambda row:row['name'])
                self.assertEqual(controller.tray.showMessage.call_count,2)
                self.assertTrue(settings['quota_alert_state'])
                self.assertTrue(saves)
        finally:
            controller.shutdown()
            controller.floating.deleteLater()
            window.deleteLater()

    def test_demo_and_smoke_do_not_send_quota_notifications(self):
        window = QMainWindow()
        window.refresh = lambda: None
        controller = DesktopController(window,lambda k:tr('en',k),{},lambda:None,smoke=True)
        try:
            controller.tray = Mock()
            controller.check_quota({'provider':'codex'},lambda row:row['name'])
            controller.tray.showMessage.assert_not_called()
            self.assertEqual(controller.alerts.state,{})
        finally:
            controller.shutdown()
            controller.floating.deleteLater()
            window.deleteLater()

    def test_left_monitor_right_seam_repeated_expansion(self):
        left = Monitor('left', QRect(0,0,1920,1080))
        right = Monitor('right', QRect(1920,0,2560,1440))
        with patch('desktop.QGuiApplication.screens', return_value=[left,right]):
            self.floating.edge = None
            self.floating.move(1600,160)
            self.floating.area()
            self.floating.edge = 'right'
            for _ in range(20):
                self.floating.collapse()
                self.assertEqual(self.floating.x(),1900)
                self.floating.expand()
                self.assertEqual(self.floating.x(),1600)
                self.assertEqual(self.floating.area(),left.availableGeometry())

    def test_negative_monitor_and_inner_left_edge(self):
        left = Monitor('left', QRect(-1920,-120,1920,1080))
        right = Monitor('right', QRect(0,0,2560,1440))
        with patch('desktop.QGuiApplication.screens', return_value=[left,right]):
            for screen, edge in [(left,'right'), (right,'left')]:
                self.floating._anchor_screen = screen
                self.floating.edge = edge
                self.floating.move(screen.geometry().left()+20,200)
                self.floating.ensure_visible()
                before = self.floating.pos()
                for _ in range(5):
                    self.floating.collapse()
                    self.floating.expand()
                self.assertEqual(self.floating.pos(),before)

    def test_restore_keeps_selected_monitor(self):
        left = Monitor('left', QRect(0,0,1920,1080))
        right = Monitor('right', QRect(1920,0,1920,1080))
        with patch('desktop.QGuiApplication.screens', return_value=[left,right]):
            self.floating._anchor_screen = left
            self.floating.edge = 'right'
            self.floating.move(1600,200)
            self.floating.collapse()
            saved = []
            self.floating.position_saved.connect(saved.append)
            self.floating.remember()
            restored = FloatingWindow(lambda k:tr('en',k), saved[-1])
            try:
                restored.collapse()
                restored.expand()
                self.assertEqual(restored.x(),1600)
                self.assertEqual(restored.area(),left.geometry())
            finally:
                restored.deleteLater()

    def test_legacy_position_without_screen_metadata(self):
        left = Monitor('left', QRect(0,0,1920,1080))
        right = Monitor('right', QRect(1920,0,1920,1080))
        with patch('desktop.QGuiApplication.screens', return_value=[left,right]):
            restored = FloatingWindow(lambda k:tr('en',k), {'x':1600,'y':200,'edge':'right'})
            try:
                restored.collapse()
                restored.expand()
                self.assertEqual(restored.x(),1600)
                self.assertEqual(restored.area(),left.geometry())
            finally:
                restored.deleteLater()

    def test_removed_monitor_recovers_on_remaining_monitor(self):
        old = Monitor('removed',QRect(0,0,1920,1080))
        remaining = Monitor('remaining',QRect(1920,0,2560,1440))
        self.floating._anchor_screen = old
        self.floating.edge = 'right'
        self.floating.move(1600,900)
        with patch('desktop.QGuiApplication.screens', return_value=[remaining]):
            self.floating.collapse()
            self.floating.expand()
            self.assertTrue(remaining.geometry().contains(self.floating.geometry()))

    def test_drag_can_explicitly_move_to_other_monitor(self):
        left = Monitor('left',QRect(0,0,1920,1080))
        right = Monitor('right',QRect(1920,0,2560,1440))
        with patch('desktop.QGuiApplication.screens', return_value=[left,right]):
            self.floating._anchor_screen = left
            self.floating.edge = 'right'
            self.floating.begin_drag(self.floating.pos()+QPoint(10,10))
            self.floating.drag_to(QPoint(2600,200))
            self.floating.finish_drag()
            self.assertEqual(self.floating.area(),right.geometry())


if __name__ == '__main__':
    unittest.main()
