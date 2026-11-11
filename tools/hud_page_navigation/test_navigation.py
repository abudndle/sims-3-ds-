import unittest

from navigation import (
    ORIGINAL_3D_HUD, ArrowRegions, PageState, create_hud_pages, navigate_tap
)


class LayoutNavigationTests(unittest.TestCase):
    def setUp(self):
        self.state = create_hud_pages(["sim_overview", "needs", "inventory"])

    def test_page_zero_is_original_bottom_hud(self):
        self.assertEqual(self.state.current, ORIGINAL_3D_HUD)

    def test_original_top_hud_pages_follow(self):
        self.assertEqual(self.state.pages[1:], ("sim_overview", "needs", "inventory"))

    def test_right_arrow_moves_to_first_info_page(self):
        self.assertEqual(navigate_tap(self.state, 240, 12).current, "sim_overview")

    def test_left_arrow_moves_to_last_page(self):
        self.assertEqual(navigate_tap(self.state, 12, 12).current, "inventory")

    def test_navigation_wraps(self):
        self.assertEqual(self.state.next().next().next().next(), self.state)
        self.assertEqual(self.state.previous().next(), self.state)

    def test_single_page_has_no_active_arrows(self):
        one = create_hud_pages()
        self.assertFalse(one.has_navigation)
        self.assertEqual(navigate_tap(one, 240, 12), one)

    def test_nonarrow_touch_unchanged(self):
        self.assertEqual(navigate_tap(self.state, 100, 100), self.state)

    def test_out_of_bounds_unchanged(self):
        for x, y in [(-1, 0), (256, 0), (0, 192)]:
            with self.subTest(x=x, y=y):
                self.assertEqual(navigate_tap(self.state, x, y), self.state)

    def test_screen_boundary_hit_regions(self):
        arrows = ArrowRegions()
        self.assertEqual(arrows.hit(0, 0), "previous")
        self.assertEqual(arrows.hit(255, 23), "next")
        self.assertIsNone(arrows.hit(24, 0))
        self.assertIsNone(arrows.hit(232, 24))

    def test_reject_overlapping_regions(self):
        with self.assertRaises(ValueError):
            ArrowRegions((0, 0, 50, 20), (30, 0, 60, 20))

    def test_reject_wrong_page_zero(self):
        with self.assertRaises(ValueError):
            PageState(("needs", "sim_overview"))

    def test_reject_duplicate_panels(self):
        with self.assertRaises(ValueError):
            create_hud_pages(["needs", "needs"])

    def test_reset_returns_to_first_page(self):
        self.assertEqual(self.state.next().next().reset().current, ORIGINAL_3D_HUD)

    def test_preserve_page_when_inventory_changes(self):
        on_needs = self.state.next().next()
        updated = on_needs.with_original_information_panels(["needs", "skills"])
        self.assertEqual(updated.current, "needs")
        self.assertEqual(updated.index, 1)

    def test_missing_page_falls_back_to_first(self):
        updated = self.state.next().with_original_information_panels(["wishes"])
        self.assertEqual(updated.current, ORIGINAL_3D_HUD)


if __name__ == "__main__":
    unittest.main()
