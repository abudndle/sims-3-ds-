"""Page-0 job opportunities: reopenable until game-supplied expiration tick.

Source-only state model; no original assets or ROM patch.
"""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class JobOffer:
    offer_id: str
    title: str
    expires_at: int
    closed: bool = False
    accepted: bool = False
    def __post_init__(self):
        if not isinstance(self.offer_id,str) or not self.offer_id.strip():
            raise ValueError('offer ID required')
        if not isinstance(self.title,str) or not self.title.strip():
            raise ValueError('job title required')
        if type(self.expires_at) is not int or self.expires_at<0:
            raise ValueError('game-provided nonnegative expiration tick required')
    def available(self,now:int)->bool:
        if type(now) is not int or now<0:
            raise ValueError('nonnegative game tick required')
        return now<self.expires_at and not self.accepted

@dataclass(frozen=True)
class JobOfferState:
    offers: tuple[JobOffer,...]=()
    active_id: str|None=None
    def add(self,offer:JobOffer,now:int)->"JobOfferState":
        if not isinstance(offer,JobOffer):
            raise TypeError('expected JobOffer')
        current=self.expire(now)
        if not offer.available(now):
            return current
        if any(item.offer_id==offer.offer_id for item in current.offers):
            raise ValueError('duplicate offer')
        return JobOfferState(current.offers+(offer,),current.active_id or offer.offer_id)
    def expire(self,now:int)->"JobOfferState":
        available=tuple(item for item in self.offers if item.available(now))
        active=self.active_id if any(item.offer_id==self.active_id for item in available) else None
        return JobOfferState(available,active)
    def close(self)->"JobOfferState":
        return replace(self,active_id=None)
    def reopen_on_page_zero(self,offer_id:str,page_index:int,now:int)->"JobOfferState":
        current=self.expire(now)
        if page_index!=0:
            return current
        if not any(item.offer_id==offer_id for item in current.offers):
            return current
        return replace(current,active_id=offer_id)
    @property
    def visible(self)->JobOffer|None:
        return next((item for item in self.offers if item.offer_id==self.active_id),None)
    def accept(self,now:int)->"JobOfferState":
        current=self.expire(now)
        if current.visible is None:
            return current
        return JobOfferState(tuple(item for item in current.offers if item.offer_id!=current.active_id),None)
