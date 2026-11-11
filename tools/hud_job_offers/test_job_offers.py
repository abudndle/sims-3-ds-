import unittest
from job_offers import JobOffer,JobOfferState

class PageZeroJobOffersTests(unittest.TestCase):
    def setUp(self):
        self.offer=JobOffer('career-1','Artist',expires_at=100)
        self.state=JobOfferState().add(self.offer,now=10)
    def test_new_offer_visible_on_page_zero_overlay(self):self.assertEqual(self.state.visible,self.offer)
    def test_clear_hides_but_keeps_reopen_option(self):
        closed=self.state.close()
        self.assertIsNone(closed.visible)
        self.assertEqual(closed.offers,(self.offer,))
    def test_reopen_from_page_zero_before_expiry(self):
        self.assertEqual(self.state.close().reopen_on_page_zero('career-1',0,99).visible,self.offer)
    def test_no_reopen_on_other_page(self):
        self.assertIsNone(self.state.close().reopen_on_page_zero('career-1',1,99).visible)
    def test_at_expiry_offer_unavailable(self):
        expired=self.state.close().reopen_on_page_zero('career-1',0,100)
        self.assertIsNone(expired.visible)
        self.assertFalse(expired.offers)
    def test_expiry_removes_open_overlay(self):self.assertIsNone(self.state.expire(100).visible)
    def test_no_accept_after_expiry(self):self.assertFalse(self.state.accept(101).offers)
    def test_accept_removes_offer(self):self.assertFalse(self.state.accept(99).offers)
    def test_decline_to_invent_timer(self):
        with self.assertRaises(ValueError):JobOffer('career-2','Chef',-1)
    def test_two_offers_reopen_individually(self):
        newer=JobOffer('career-2','Chef',200)
        state=self.state.add(newer,10).close().reopen_on_page_zero('career-2',0,110)
        self.assertEqual(state.visible,newer)
        self.assertEqual(len(state.offers),1)
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):self.state.add(self.offer,20)
    def test_invalid_clock(self):
        with self.assertRaises(ValueError):self.state.expire(-1)
    def test_missing_id_cannot_reopen(self):
        self.assertIsNone(self.state.close().reopen_on_page_zero('missing',0,50).visible)
    def test_state_is_immutable(self):
        self.state.close()
        self.assertEqual(self.state.visible,self.offer)

if __name__=='__main__':unittest.main()
