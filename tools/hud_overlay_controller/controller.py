"""Pure state transition model for persistent notifications above Sims 3 DS HUD pages.

The top-screen 3D scene is deliberately not modeled/modified here. This code
has no game-asset dependency and does not hook into the original ROM.
"""
from dataclasses import dataclass, replace
from navigation import PageState, ArrowRegions, create_hud_pages
from notifications import Notice, NotificationQueue


@dataclass(frozen=True)
class TapResult:
    state: "HudState"
    action: str


@dataclass(frozen=True)
class HudState:
    pages: PageState
    notifications: NotificationQueue = NotificationQueue()

    @classmethod
    def create(cls, info_panels=()):
        return cls(create_hud_pages(info_panels))

    @property
    def visible_notification(self):
        """The current notice is rendered over whatever HUD page is selected."""
        return self.notifications.current

    def post(self, notice: Notice):
        """Keep both the selected page and any previously queued alerts."""
        return replace(self, notifications=self.notifications.enqueue(notice))

    def clear(self):
        """Explicit acknowledgement; never change the underlying HUD page."""
        return replace(self, notifications=self.notifications.dismiss())

    def tap(self, x, y, *, arrow_regions=ArrowRegions(), clear_region=(96, 144, 160, 184)):
        """Route a NEW touch-down. Arrows outrank overlays; clear is next.

        All other touches are absorbed by an active notification. The clear
        rectangle is illustrative, not an extracted original-game asset target.
        Only a renderer with a verified clear button may use these coordinates.
        """
        if type(x) is not int or type(y) is not int or not (0 <= x < 256 and 0 <= y < 192):
            return TapResult(self, "invalid")
        arrow = arrow_regions.hit(x, y)
        if arrow and self.pages.has_navigation:
            next_page = self.pages.previous() if arrow == "previous" else self.pages.next()
            return TapResult(replace(self, pages=next_page), "page_" + arrow)
        if self.visible_notification is not None:
            x0, y0, x1, y1 = clear_region
            if x0 <= x < x1 and y0 <= y < y1:
                return TapResult(self.clear(), "notification_cleared")
            return TapResult(self, "notification_blocked_underlay")
        return TapResult(self, "hud_passthrough")
