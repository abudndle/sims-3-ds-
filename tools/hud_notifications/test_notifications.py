import unittest
from notifications import Notice, NotificationQueue


class BottomHudNotificationsTests(unittest.TestCase):
    def setUp(self):
        self.job = Notice("job_opportunity", "A new job is available")
        self.skill = Notice("skill_gain", "Skill increased")

    def test_initially_no_notice(self):
        self.assertIsNone(NotificationQueue().current)

    def test_job_alert_displayable(self):
        self.assertEqual(NotificationQueue().enqueue(self.job).current, self.job)

    def test_skill_gain_displayable(self):
        self.assertEqual(NotificationQueue().enqueue(self.skill).current, self.skill)

    def test_fifo_prevents_alert_loss(self):
        queue = NotificationQueue().enqueue(self.job).enqueue(self.skill)
        self.assertEqual(queue.current, self.job)
        self.assertEqual(queue.dismiss().current, self.skill)

    def test_dismiss_empty_is_safe(self):
        queue = NotificationQueue()
        self.assertEqual(queue.dismiss(), queue)

    def test_queued_notices_persist_across_unrelated_page_navigation(self):
        queue = NotificationQueue().enqueue(self.job)
        selected_hud_index = 3
        self.assertEqual(queue.current, self.job)
        self.assertEqual(selected_hud_index, 3)

    def test_reject_empty_notice(self):
        with self.assertRaises(ValueError):
            Notice("skill_gain", "")

    def test_reject_wrong_type(self):
        with self.assertRaises(TypeError):
            NotificationQueue().enqueue("text")

    def test_dismiss_does_not_mutate_previous_state(self):
        original = NotificationQueue().enqueue(self.job).enqueue(self.skill)
        subsequent = original.dismiss()
        self.assertEqual(original.current, self.job)
        self.assertEqual(subsequent.current, self.skill)


if __name__ == "__main__":
    unittest.main()
