"""Dependency-free HUD page selection logic for the Sims 3 DS dual-screen rework.

This is a portable reference/state model, not yet hooked into the game ROM.
Page 0 is the original lower-screen 3D-control HUD; page 1 is notifications.
"""
from dataclasses import dataclass
from typing import Sequence

ORIGINAL_3D_HUD = "original_3d_control_hud"
NOTIFICATIONS_HUD = "notifications"


@dataclass(frozen=True)
class PageState:
    pages: tuple[str, ...]
    index: int = 0

    def __post_init__(self):
        if len(self.pages) < 2 or self.pages[:2] != (ORIGINAL_3D_HUD, NOTIFICATIONS_HUD):
            raise ValueError("pages zero and one must be gameplay controls and notifications")
        if any(not isinstance(p, str) or not p.strip() for p in self.pages):
            raise ValueError("pages must have nonblank identifiers")
        if len(self.pages) != len(set(self.pages)):
            raise ValueError("page identifiers must be unique")
        if not 0 <= self.index < len(self.pages):
            raise ValueError("page index outside range")

    @property
    def current(self) -> str:
        return self.pages[self.index]

    @property
    def has_navigation(self) -> bool:
        return len(self.pages) > 1

    def next(self) -> "PageState":
        return PageState(self.pages, (self.index + 1) % len(self.pages))

    def previous(self) -> "PageState":
        return PageState(self.pages, (self.index - 1) % len(self.pages))

    def reset(self) -> "PageState":
        return PageState(self.pages, 0)

    def with_original_information_panels(self, panels: Sequence[str]) -> "PageState":
        """Reconcile inventory while retaining current page when it still exists."""
        pages = (ORIGINAL_3D_HUD, NOTIFICATIONS_HUD, *tuple(panels))
        if not pages or len(pages) != len(set(pages)):
            raise ValueError("invalid page inventory")
        selected = self.current if self.current in pages else ORIGINAL_3D_HUD
        return PageState(pages, pages.index(selected))


def create_hud_pages(information_panels: Sequence[str] = ()) -> PageState:
    """Load actual top-screen panel inventory only after asset audit."""
    return PageState((ORIGINAL_3D_HUD, NOTIFICATIONS_HUD, *tuple(information_panels)))


@dataclass(frozen=True)
class ArrowRegions:
    """Exclusive-edge rectangles in original DS touch coordinates (256x192)."""
    left: tuple[int, int, int, int] = (0, 0, 24, 24)
    right: tuple[int, int, int, int] = (232, 0, 256, 24)

    def __post_init__(self):
        for region in (self.left, self.right):
            x0, y0, x1, y1 = region
            if not (0 <= x0 < x1 <= 256 and 0 <= y0 < y1 <= 192):
                raise ValueError("invalid arrow bounds")
        if self._overlap(self.left, self.right):
            raise ValueError("arrow regions may not overlap")

    @staticmethod
    def _overlap(a, b):
        return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

    @staticmethod
    def _contains(region, x, y):
        return region[0] <= x < region[2] and region[1] <= y < region[3]

    def hit(self, x: int, y: int) -> str | None:
        if not isinstance(x, int) or not isinstance(y, int):
            return None
        if not (0 <= x < 256 and 0 <= y < 192):
            return None
        if self._contains(self.left, x, y):
            return "previous"
        if self._contains(self.right, x, y):
            return "next"
        return None


def navigate_tap(state: PageState, x: int, y: int, regions=ArrowRegions()) -> PageState:
    """React to a new touch-down on a navigation arrow; nonarrow touches pass through."""
    if not state.has_navigation:
        return state
    action = regions.hit(x, y)
    return state.previous() if action == "previous" else (
        state.next() if action == "next" else state
    )
