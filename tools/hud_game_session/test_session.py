import unittest
from session import HudGameSession
from job_offers import JobOffer
from notifications import Notice


class HUDGameSessionTests(unittest.TestCase):
    def setUp(self):
        self.s = HudGameSession.create(('sim_info', 'needs'), game_tick=20)
        self.offer = JobOffer('career42', 'New career', expires_at=100)
        self.skill = Notice('skill_gain', 'Cooking level 2')

    def test_starts_on_original_hud(self):
        self.assertEqual(self.s.hud.pages.index, 0)

    def test_no_notification_page(self):
        self.assertEqual(self.s.hud.pages.pages, ('original_3d_control_hud', 'sim_info', 'needs'))

    def test_new_offer_overlays_page_zero(self):
        posted = self.s.post_job(self.offer)
        self.assertEqual(posted.hud.visible_notification.kind, 'job_opportunity:career42')
        self.assertEqual(posted.hud.pages.index, 0)

    def test_dismiss_hides_notice_but_keeps_job(self):
        state = self.s.post_job(self.offer).dismiss()
        self.assertIsNone(state.hud.visible_notification)
        self.assertEqual(len(state.jobs.offers), 1)

    def test_reopen_on_page_zero_before_expiry(self):
        state = self.s.post_job(self.offer).dismiss().advance(99).reopen_job('career42')
        self.assertEqual(state.hud.visible_notification.kind, 'job_opportunity:career42')

    def test_no_reopen_on_other_hud_page(self):
        state = self.s.post_job(self.offer).dismiss().navigate('right').reopen_job('career42')
        self.assertIsNone(state.hud.visible_notification)

    def test_can_reopen_after_returning_to_page_zero(self):
        state = self.s.post_job(self.offer).dismiss().navigate('right').navigate('left').reopen_job('career42')
        self.assertEqual(state.hud.visible_notification.kind, 'job_opportunity:career42')

    def test_expiry_erases_offer_and_its_overlay(self):
        state = self.s.post_job(self.offer).advance(100)
        self.assertEqual(state.jobs.offers, ())
        self.assertIsNone(state.hud.visible_notification)

    def test_expired_job_cannot_reopen(self):
        state = self.s.post_job(self.offer).dismiss().advance(100).reopen_job('career42')
        self.assertIsNone(state.hud.visible_notification)

    def test_unrelated_notifications_survive_job_expiry(self):
        state = self.s.post_job(self.offer).post_notice(self.skill).advance(100)
        self.assertEqual(state.hud.visible_notification, self.skill)

    def test_job_expiry_removes_queued_not_visible_notice(self):
        state = self.s.post_notice(self.skill).post_job(self.offer).advance(100)
        self.assertEqual(state.hud.notifications.pending, (self.skill,))

    def test_other_alerts_are_fifo(self):
        state = self.s.post_notice(self.skill).post_job(self.offer).dismiss()
        self.assertEqual(state.hud.visible_notification.kind, 'job_opportunity:career42')

    def test_reopen_does_not_duplicate_notice(self):
        state = self.s.post_job(self.offer).reopen_job('career42').reopen_job('career42')
        self.assertEqual(len(state.hud.notifications.pending), 1)

    def test_reopen_preserves_unrelated_alerts(self):
        state = self.s.post_job(self.offer).dismiss().post_notice(self.skill).reopen_job('career42')
        self.assertEqual(len(state.hud.notifications.pending), 2)
        self.assertEqual(state.hud.notifications.pending[1], self.skill)

    def test_job_can_be_accepted_before_expiry(self):
        state = self.s.post_job(self.offer).accept_visible_job()
        self.assertEqual(state.jobs.offers, ())
        self.assertIsNone(state.hud.visible_notification)

    def test_cannot_accept_on_other_page(self):
        state = self.s.post_job(self.offer).navigate('right').accept_visible_job()
        self.assertEqual(len(state.jobs.offers), 1)

    def test_expired_offer_not_accepted(self):
        state = self.s.post_job(self.offer).advance(101).accept_visible_job()
        self.assertEqual(state.jobs.offers, ())
        self.assertIsNone(state.hud.visible_notification)

    def test_not_allowed_to_rewind_clock(self):
        with self.assertRaises(ValueError):
            self.s.advance(19)

    def test_expired_offer_post_does_not_show(self):
        state = self.s.post_job(JobOffer('old', 'Old offer', expires_at=20))
        self.assertIsNone(state.hud.visible_notification)

    def test_nonjob_notice_does_not_change_page(self):
        state = self.s.navigate('right').post_notice(self.skill)
        self.assertEqual(state.hud.pages.index, 1)

    def test_invalid_job_notice_bypass_prevented(self):
        with self.assertRaises(ValueError):
            self.s.post_notice(Notice('job_opportunity:fake', 'Bypass'))

    def test_pending_notice_keeps_job_visible_when_first_is_dismissed(self):
        state = self.s.post_notice(self.skill).post_job(self.offer).dismiss()
        self.assertEqual(state.hud.visible_notification.kind, 'job_opportunity:career42')

    def test_multi_job_expiry_keeps_other(self):
        later = JobOffer('career99', 'Other job', expires_at=200)
        state = self.s.post_job(self.offer).post_job(later).advance(100)
        self.assertEqual(tuple(o.offer_id for o in state.jobs.offers), ('career99',))

    def test_touch_dismiss_job_can_reopen(self):
        state, action = self.s.post_job(self.offer).tap(120, 160)
        self.assertEqual(action, 'notification_cleared')
        self.assertIsNone(state.hud.visible_notification)
        self.assertIsNone(state.jobs.visible)
        self.assertEqual(state.reopen_job('career42').hud.visible_notification.kind, 'job_opportunity:career42')

    def test_touch_arrow_keeps_job_overlay(self):
        state, action = self.s.post_job(self.offer).tap(240, 12)
        self.assertEqual(action, 'page_next')
        self.assertEqual(state.hud.pages.index, 1)
        self.assertEqual(state.hud.visible_notification.kind, 'job_opportunity:career42')

    def test_touch_dismiss_skill_does_not_close_job(self):
        state, action = self.s.post_notice(self.skill).post_job(self.offer).tap(120, 160)
        self.assertEqual(action, 'notification_cleared')
        self.assertEqual(len(state.jobs.offers), 1)
        self.assertEqual(state.hud.visible_notification.kind, 'job_opportunity:career42')

    def test_immutable_transitions(self):
        self.s.post_job(self.offer)
        self.assertFalse(self.s.jobs.offers)


if __name__ == '__main__':
    unittest.main()
