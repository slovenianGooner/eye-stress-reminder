#!/usr/bin/env python3
import rumps
import AppKit

EYE_INTERVAL = 20 * 60      # 20 min between eye rests
EYE_REST_DURATION = 20      # 20 sec stare into distance
BREAK_INTERVAL = 45 * 60    # 45 min between standing breaks
BREAK_DURATION = 5 * 60     # 5 min break


class EyeStressReminderApp(rumps.App):
    def __init__(self):
        super().__init__("", quit_button=None)
        self._reset_state()

        self.eye_item = rumps.MenuItem("👁  Eye rest in  20:00")
        self.break_item = rumps.MenuItem("🚶 Break in  45:00")

        self.menu = [
            self.eye_item,
            self.break_item,
            None,
            rumps.MenuItem("Reset timers", callback=self.on_reset),
            None,
            rumps.MenuItem("Quit", callback=lambda _: rumps.quit_application()),
        ]

        # Plain-text initial label; colored version set on first timer tick after run()
        self.title = "👁 20:00   🚶 45:00"
        rumps.Timer(self.tick, 1).start()

    def _reset_state(self):
        self.eye_countdown = EYE_INTERVAL
        self.break_countdown = BREAK_INTERVAL
        self.eye_resting = False
        self.on_break = False
        self.eye_rest_left = 0
        self.break_left = 0

    def _fmt(self, secs):
        secs = max(0, int(secs))
        return f"{secs // 60:02d}:{secs % 60:02d}"

    def _set_bar(self, text, red=False):
        color = AppKit.NSColor.redColor() if red else AppKit.NSColor.labelColor()
        try:
            font = AppKit.NSFont.monospacedDigitSystemFontOfSize_weight_(13, 0.0)
        except Exception:
            font = AppKit.NSFont.menuBarFontOfSize_(0)
        attrs = {
            AppKit.NSForegroundColorAttributeName: color,
            AppKit.NSFontAttributeName: font,
        }
        attributed = AppKit.NSAttributedString.alloc().initWithString_attributes_(text, attrs)
        self._nsapp.nsstatusitem.setAttributedTitle_(attributed)

    def tick(self, _):
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

        self._update_ui()

    def _update_ui(self):
        action = self.eye_resting or self.on_break

        if self.eye_resting:
            eye_bar = f"👁 {self._fmt(self.eye_rest_left)}"
            self.eye_item.title = f"👁  Look 20 ft away  —  {self._fmt(self.eye_rest_left)} left"
        else:
            eye_bar = f"👁 {self._fmt(self.eye_countdown)}"
            self.eye_item.title = f"👁  Eye rest in  {self._fmt(self.eye_countdown)}"

        if self.on_break:
            break_bar = f"🚶 {self._fmt(self.break_left)}"
            self.break_item.title = f"🚶 Stand up & move!  —  {self._fmt(self.break_left)} left"
        else:
            break_bar = f"🚶 {self._fmt(self.break_countdown)}"
            self.break_item.title = f"🚶 Break in  {self._fmt(self.break_countdown)}"

        self._set_bar(f"{eye_bar}   {break_bar}", red=action)

    def on_reset(self, _):
        self._reset_state()
        self._update_ui()


if __name__ == "__main__":
    EyeStressReminderApp().run()
