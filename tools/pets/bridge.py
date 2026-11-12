"""Strict host-event contract for the standalone Pets prototype.

No DS memory hooks, retail input interception, HUD rendering, or ROM patching.
An eventual verified native adapter must translate approved *lot-mode* events
to these messages. Reject malformed/unexpected messages before any mutation.
"""
from .model import ACTIONS, KINDS, PetError
from .session import MODES, PetsSession

EVENT_KEYS = {
    "enter_mode": frozenset({"type", "mode"}),
    "adopt": frozenset({"type", "pet_id", "name", "species"}),
    "select": frozenset({"type", "pet_id"}),
    "interact": frozenset({"type", "action"}),
    "advance_time": frozenset({"type", "minutes"}),
    "snapshot": frozenset({"type"}),
}


def _id(value):
    if type(value) is not int or not 0 <= value <= 65535:
        raise PetError("pet_id must be an integer between 0 and 65535")
    return value


def _minutes(value):
    if type(value) is not int or not 0 <= value <= 1440:
        raise PetError("minutes must be an integer between 0 and 1440")
    return value


def _validate(event):
    if not isinstance(event, dict):
        raise PetError("event must be an object")
    kind = event.get("type")
    if type(kind) is not str or kind not in EVENT_KEYS:
        raise PetError("unknown pet event")
    if event.keys() != EVENT_KEYS[kind]:
        raise PetError("missing or unexpected event fields")
    if kind == "enter_mode":
        if type(event["mode"]) is not str or event["mode"] not in MODES:
            raise PetError("invalid host mode")
    elif kind == "adopt":
        _id(event["pet_id"])
        if (type(event["name"]) is not str or
                not 1 <= len(event["name"]) <= 16 or
                not event["name"].strip()):
            raise PetError("invalid pet name")
        if type(event["species"]) is not str or event["species"] not in KINDS:
            raise PetError("invalid pet species")
    elif kind == "select":
        _id(event["pet_id"])
    elif kind == "interact":
        if type(event["action"]) is not str or event["action"] not in ACTIONS:
            raise PetError("invalid pet interaction")
    elif kind == "advance_time":
        _minutes(event["minutes"])
    return kind


def dispatch(session, event):
    """Validate one host message and return an immutable-data snapshot.

    This function does NOT capture or reroute original NDS touchscreen events.
    A rejected event leaves the session unchanged. Successful commands return
    a plain dict, never references to mutable live pet objects.
    """
    if not isinstance(session, PetsSession):
        raise PetError("expected PetsSession")
    kind = _validate(event)
    if kind == "enter_mode":
        session.enter_mode(event["mode"])
    elif kind == "adopt":
        session.adopt(event["pet_id"], event["name"], event["species"])
    elif kind == "select":
        session.select(event["pet_id"])
    elif kind == "interact":
        session.interact(event["action"])
    elif kind == "advance_time":
        session.advance_time(event["minutes"])
    return session.snapshot()
