#!/usr/bin/env python3
import objc
import rumps
import AppKit
from Foundation import NSObject

EYE_INTERVAL = 20 * 60      # 20 min between eye rests
EYE_REST_DURATION = 20      # 20 sec stare into distance
BREAK_INTERVAL = 45 * 60    # 45 min between standing breaks
BREAK_DURATION = 5 * 60     # 5 min break

ICON_ACTIVE = "👁"
ICON_PAUSED = "👁"


class _SystemObserver(NSObject):
    def initWithCallback_(self, cb):
        self = objc.super(_SystemObserver, self).init()
        if self is not None:
            self._cb = cb
        return self

    def handleNotification_(self, notification):
        self._cb()

    @objc.python_method
    def register(self):
        nc = AppKit.NSWorkspace.sharedWorkspace().notificationCenter()
        nc.addObserver_selector_name_object_(
            self, b'handleNotification:', AppKit.NSWorkspaceDidWakeNotification, None
        )
        nc.addObserver_selector_name_object_(
            self, b'handleNotification:', 'NSWorkspaceSessionDidBecomeActiveNotification', None
        )


class EyeStressReminderApp(rumps.App):
    def __init__(self):
        super().__init__(ICON_ACTIVE, quit_button=None)
        self._reset_state()
        self.paused = False

        self.status_item = rumps.MenuItem("● Active")
        self.status_item.set_callback(None)

        self.pause_item = rumps.MenuItem("Pause", callback=self.on_pause_toggle)

        self.menu = [
            self.status_item,
            None,
            self.pause_item,
            rumps.MenuItem("Reset timers", callback=self.on_reset),
            None,
            rumps.MenuItem("Quit", callback=lambda _: rumps.quit_application()),
        ]

        self._update_ui()
        rumps.Timer(self.tick, 1).start()

        self._sys_observer = _SystemObserver.alloc().initWithCallback_(self._on_system_wake)
        self._sys_observer.register()

    def _reset_state(self):
        self.eye_countdown = EYE_INTERVAL
        self.break_countdown = BREAK_INTERVAL
        self.eye_resting = False
        self.on_break = False
        self.eye_rest_left = 0
        self.break_left = 0

    def _on_system_wake(self):
        self._reset_state()
        self.paused = False
        self.pause_item.title = "Pause"
        self._update_ui()

    def _update_ui(self):
        if self.paused:
            self.title = "👁"
            self.status_item.title = "⏸ Paused"
        else:
            self.title = "👁"
            self.status_item.title = "● Active"

    def tick(self, _):
        if self.paused:
            return

        if self.eye_resting:
            self.eye_rest_left -= 1
            if self.eye_rest_left <= 0:
                self.eye_resting = False
                self.eye_countdown = EYE_INTERVAL
        else:
            self.eye_countdown -= 1
            if self.eye_countdown <= 0:
                self.eye_resting = True
                self.eye_rest_left = EYE_REST_DURATION
                rumps.notification(
                    "Eye Rest",
                    "Stare 20 feet away for 20 seconds",
                    "Look into the distance to relax your eyes.",
                    sound=True,
                )

        if self.on_break:
            self.break_left -= 1
            if self.break_left <= 0:
                self.on_break = False
                self.break_countdown = BREAK_INTERVAL
        else:
            self.break_countdown -= 1
            if self.break_countdown <= 0:
                self.on_break = True
                self.break_left = BREAK_DURATION
                rumps.notification(
                    "Stand Up & Move",
                    "Take a 5-minute break",
                    "Step away from your screen and stretch.",
                    sound=True,
                )

    def on_pause_toggle(self, _):
        self.paused = not self.paused
        self.pause_item.title = "Resume" if self.paused else "Pause"
        self._update_ui()

    def on_reset(self, _):
        self._reset_state()
        self.paused = False
        self.pause_item.title = "Pause"
        self._update_ui()


if __name__ == "__main__":
    EyeStressReminderApp().run()
