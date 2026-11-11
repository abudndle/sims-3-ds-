import sys
import unittest
from pathlib import Path

# CI clones the public repository and imports the actual modules, not stubs.
TOOLS = Path(__file__).resolve().parents[1]
for module_dir in (TOOLS / "hud_page_navigation", TOOLS / "hud_notifications"):
    sys.path.insert(0, str(module_dir))
from controller import HudState
from notifications import Notice


class HudOverlayIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.state = HudState.create(["sim_info", "needs", "skills"])
        self.job = Notice("job_opportunity", "New job opportunity")
        self.skill = Notice("skill_gain", "Skill level gained")

    def test_default_page_is_original_gameplay_hud(self):
        self.assertEqual(self.state.pages.current, "original_3d_control_hud")

    def test_notifications_are_not_pages(self):
        self.assertEqual(self.state.pages.pages, ("original_3d_control_hud", "sim_info", "needs", "skills"))

    def test_alert_overlays_page_zero(self):
        s = self.state.post(self.job)
        self.assertEqual(s.visible_notification, self.job)
        self.assertEqual(s.pages.current, "original_3d_control_hud")

    def test_alert_persists_when_right_arrow_switches_page(self):
        s = self.state.post(self.job).tap(240, 12).state
        self.assertEqual(s.pages.current, "sim_info")
        self.assertEqual(s.visible_notification, self.job)

    def test_alert_persists_across_all_pages(self):
        s = self.state.post(self.job)
        for _ in range(7):
            s = s.tap(240, 12).state
            self.assertEqual(s.visible_notification, self.job)

    def test_arrow_navigation_does_not_clear_alert(self):
        result = self.state.post(self.job).tap(10, 10)
        self.assertEqual(result.action, "page_previous")
        self.assertEqual(result.state.notifications.pending, (self.job,))

    def test_explicit_clear_keeps_page(self):
        s = self.state.post(self.job).tap(240, 12).state
        result = s.tap(120, 160)
        self.assertEqual(result.action, "notification_cleared")
        self.assertEqual(result.state.pages.current, "sim_info")
        self.assertIsNone(result.state.visible_notification)

    def test_multiple_notifications_fifo(self):
        s = self.state.post(self.job).post(self.skill)
        self.assertEqual(s.tap(120, 160).state.visible_notification, self.skill)
        self.assertIsNone(s.tap(120, 160).state.tap(120, 160).state.visible_notification)

    def test_alert_blocks_underlying_hud_tap(self):
        result = self.state.post(self.job).tap(100, 80)
        self.assertEqual(result.action, "notification_blocked_underlay")
        self.assertEqual(result.state.pages.index, 0)

    def test_without_alert_hud_receives_touch(self):
        self.assertEqual(self.state.tap(100, 80).action, "hud_passthrough")

    def test_out_of_bounds_does_not_mutate_state(self):
        for x, y in [(-1, 12), (256, 12), (12, 192), (True, 10)]:
            with self.subTest(x=x, y=y):
                result = self.state.post(self.job).tap(x, y)
                self.assertEqual(result.action, "invalid")
                self.assertEqual(result.state.visible_notification, self.job)

    def test_tap_does_not_mutate_previous_immutable_state(self):
        original = self.state.post(self.job)
        changed = original.tap(120, 160).state
        self.assertEqual(original.visible_notification, self.job)
        self.assertIsNone(changed.visible_notification)

    def test_single_page_still_handles_clear(self):
        s = HudState.create().post(self.job)
        self.assertEqual(s.tap(240, 12).action, "notification_blocked_underlay")
        self.assertEqual(s.tap(120, 160).action, "notification_cleared")

    def test_clearing_empty_alert_passthrough(self):
        self.assertEqual(self.state.tap(120, 160).action, "hud_passthrough")

    def test_page_reset_does_not_clear_queue(self):
        s = self.state.post(self.job).tap(240, 12).state
        from dataclasses import replace
        reset = replace(s, pages=s.pages.reset())
        self.assertEqual(reset.pages.index, 0)
        self.assertEqual(reset.visible_notification, self.job)


if __name__ == '__main__':
    unittest.main()
