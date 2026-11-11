"""Non-rendering FIFO notification state for the bottom-screen HUD.

Original artwork, timing, sounds, actions and modal semantics are integrated
only after the game behavior is audited; this module never displays an image.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Notice:
    kind: str
    text: str

    def __post_init__(self):
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ValueError("notice kind required")
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("notice text required")


@dataclass(frozen=True)
class NotificationQueue:
    pending: tuple[Notice, ...] = ()

    @property
    def current(self) -> Optional[Notice]:
        return self.pending[0] if self.pending else None

    def enqueue(self, notice: Notice) -> "NotificationQueue":
        if not isinstance(notice, Notice):
            raise TypeError("expected Notice")
        return NotificationQueue(self.pending + (notice,))

    def dismiss(self) -> "NotificationQueue":
        return NotificationQueue(self.pending[1:]) if self.pending else self

    def has_alert(self) -> bool:
        return bool(self.pending)
