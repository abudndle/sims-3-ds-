"""Safe host-facing prototype boundary, with no retail-game memory access.

The host must explicitly report its game mode. Pet actions are accepted only
inside a live lot; original map, Build/Buy, and social menu routing is untouched.
"""
from dataclasses import dataclass, field
from typing import Optional

from .model import HouseholdPets, Pet, PetError

LOT = "lot"
MAP = "map"
BUILD = "build"
BUY = "buy"
SOCIAL = "social"
PAUSED = "paused"
MODES = frozenset({LOT, MAP, BUILD, BUY, SOCIAL, PAUSED})


@dataclass
class PetsSession:
    household: HouseholdPets = field(default_factory=HouseholdPets)
    mode: str = MAP
    selected_pet_id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.mode not in MODES:
            raise PetError("invalid host game mode")
        if self.selected_pet_id is not None:
            self.household.get(self.selected_pet_id)

    def enter_mode(self, mode: str) -> None:
        if mode not in MODES:
            raise PetError("invalid host game mode")
        self.mode = mode
        if mode != LOT:
            self.selected_pet_id = None

    def _require_lot(self) -> None:
        if self.mode != LOT:
            raise PetError("pet actions are only available during lot gameplay")

    def adopt(self, pet_id: int, name: str, species: str) -> None:
        self._require_lot()
        self.household.adopt(Pet(pet_id, name, species))

    def select(self, pet_id: int) -> None:
        self._require_lot()
        self.household.get(pet_id)
        self.selected_pet_id = pet_id

    def interact(self, action: str) -> dict:
        self._require_lot()
        if self.selected_pet_id is None:
            raise PetError("select a pet first")
        pet = self.household.get(self.selected_pet_id)
        pet.interact(action)
        # Return only a data snapshot; no HUD drawing or game-memory writing.
        return pet.to_dict()

    def advance_time(self, minutes: int) -> None:
        # Advance only during active lot gameplay; no decay while in menus/map.
        if not isinstance(minutes, int) or isinstance(minutes, bool) or minutes < 0:
            raise PetError("minutes must be a nonnegative integer")
        if self.mode == LOT:
            self.household.tick(minutes)

    def snapshot(self) -> dict:
        return {
            "mode": self.mode,
            "selected_pet_id": self.selected_pet_id,
            "household": self.household.to_dict(),
        }
