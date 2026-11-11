"""Bind HUD pages, persistent notifications, and game-timed Page-0 job offers.

Source-only transition model. The eventual ROM hook must provide monotonic
original-game ticks and actual message IDs; no gameplay timer is invented.
"""
from dataclasses import dataclass, replace
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parents[1]
for folder in ('hud_page_navigation', 'hud_notifications', 'hud_overlay_controller', 'hud_job_offers'):
    path = str(TOOLS / folder)
    if path not in sys.path:
        sys.path.insert(0, path)

from controller import HudState
from notifications import Notice, NotificationQueue
from job_offers import JobOffer, JobOfferState

JOB_KIND = 'job_opportunity:'


def job_notice(offer: JobOffer) -> Notice:
    return Notice(JOB_KIND + offer.offer_id, offer.title)


@dataclass(frozen=True)
class HudGameSession:
    hud: HudState
    jobs: JobOfferState = JobOfferState()
    game_tick: int = 0

    @classmethod
    def create(cls, panels=(), game_tick=0):
        if type(game_tick) is not int or game_tick < 0:
            raise ValueError('nonnegative game tick required')
        return cls(HudState.create(panels), game_tick=game_tick)

    def advance(self, game_tick: int) -> 'HudGameSession':
        """Prune expired job offers and associated notices without affecting others."""
        if type(game_tick) is not int or game_tick < self.game_tick:
            raise ValueError('game tick must be monotonic')
        jobs = self.jobs.expire(game_tick)
        active_ids = {item.offer_id for item in jobs.offers}
        pending = tuple(item for item in self.hud.notifications.pending
                        if not item.kind.startswith(JOB_KIND)
                        or item.kind[len(JOB_KIND):] in active_ids)
        return replace(self, game_tick=game_tick, jobs=jobs,
                       hud=replace(self.hud, notifications=NotificationQueue(pending)))

    def post_job(self, offer: JobOffer) -> 'HudGameSession':
        """Queue offer notification without switching pages or losing other alerts."""
        session = self.advance(self.game_tick)
        jobs = session.jobs.add(offer, session.game_tick)
        if jobs == session.jobs:
            return session  # already expired
        return replace(session, jobs=jobs, hud=session.hud.post(job_notice(offer)))

    def post_notice(self, notice: Notice) -> 'HudGameSession':
        if notice.kind.startswith(JOB_KIND):
            raise ValueError('job notices must be created with post_job')
        return replace(self, hud=self.hud.post(notice))

    def dismiss(self) -> 'HudGameSession':
        """Clear visible overlay, keep dismissed job offer available until expiry."""
        current = self.hud.visible_notification
        jobs = self.jobs.close() if current is not None and current.kind.startswith(JOB_KIND) else self.jobs
        return replace(self, hud=self.hud.clear(), jobs=jobs)

    def tap(self, x: int, y: int) -> tuple['HudGameSession', str]:
        """Forward a bottom-screen touch; synchronize job state on alert clear.

        The underlying HUD controller defines provisional arrow/clear bounds;
        asset-verified touch rectangles are still needed for the real ROM.
        """
        old_notice = self.hud.visible_notification
        result = self.hud.tap(x, y)
        jobs = self.jobs
        if result.action == 'notification_cleared' and old_notice is not None and old_notice.kind.startswith(JOB_KIND):
            jobs = jobs.close()
        return replace(self, hud=result.state, jobs=jobs), result.action

    def navigate(self, direction: str) -> 'HudGameSession':
        if direction not in ('left', 'right'):
            raise ValueError('direction must be left or right')
        pages = self.hud.pages.previous() if direction == 'left' else self.hud.pages.next()
        return replace(self, hud=replace(self.hud, pages=pages))

    def reopen_job(self, offer_id: str) -> 'HudGameSession':
        """On gameplay HUD Page 0 only, bring live offer details above the HUD."""
        session = self.advance(self.game_tick)
        jobs = session.jobs.reopen_on_page_zero(offer_id, session.hud.pages.index, session.game_tick)
        if jobs.visible is None or jobs.visible.offer_id != offer_id:
            return session
        notice = job_notice(jobs.visible)
        # Do not create duplicate job notification entries or discard other alerts.
        pending = (notice,) + tuple(n for n in session.hud.notifications.pending if n.kind != notice.kind)
        hud = replace(session.hud, notifications=NotificationQueue(pending))
        return replace(session, hud=hud, jobs=jobs)

    def accept_visible_job(self) -> 'HudGameSession':
        """Only accept the currently shown, unexpired Page-0 job opportunity."""
        session = self.advance(self.game_tick)
        visible = session.hud.visible_notification
        if session.hud.pages.index != 0 or visible is None or not visible.kind.startswith(JOB_KIND):
            return session
        offer_id = visible.kind[len(JOB_KIND):]
        jobs = session.jobs.reopen_on_page_zero(offer_id, 0, session.game_tick)
        if jobs.visible is None or jobs.visible.offer_id != offer_id:
            return session
        jobs = jobs.accept(session.game_tick)
        rest = tuple(n for n in session.hud.notifications.pending if n.kind != visible.kind)
        return replace(session, jobs=jobs, hud=replace(session.hud, notifications=NotificationQueue(rest)))
