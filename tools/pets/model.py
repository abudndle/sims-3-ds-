"""Asset-free, deterministic pet gameplay prototype for the Sims 3 DS mod.

This is a reference gameplay model, NOT a ROM patch. No retail structures are
assumed here; adapters must be verified against the user-owned ROM separately.
"""
from dataclasses import dataclass, field
from typing import Dict, List

KINDS = frozenset({"cat", "dog"})
ACTIONS = frozenset({"feed", "play", "groom", "rest", "walk"})
MAX_PETS = 3


class PetError(ValueError):
    """Invalid pet creation or interaction."""


def clamp(value: int) -> int:
    return max(0, min(100, value))


@dataclass
class Pet:
    pet_id: int
    name: str
    species: str
    hunger: int = 80
    energy: int = 80
    hygiene: int = 80
    fun: int = 80
    bond: int = 0

    def __post_init__(self) -> None:
        if self.pet_id < 0:
            raise PetError("pet_id must be nonnegative")
        if not self.name.strip() or len(self.name) > 16:
            raise PetError("pet name must contain 1-16 characters")
        if self.species not in KINDS:
            raise PetError("only cats and dogs are supported")
        for stat in ("hunger", "energy", "hygiene", "fun", "bond"):
            value = getattr(self, stat)
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 100:
                raise PetError(f"{stat} must be an integer from 0 to 100")

    def interact(self, action: str) -> None:
        if action not in ACTIONS:
            raise PetError(f"unknown action: {action}")
        if action == "walk" and self.species != "dog":
            raise PetError("walking is dog-only")
        if action == "feed":
            self.hunger = clamp(self.hunger + 30)
            self.bond = clamp(self.bond + 3)
        elif action == "play":
            if self.energy < 10:
                raise PetError("pet is too tired to play")
            self.fun = clamp(self.fun + 25)
            self.energy = clamp(self.energy - 10)
            self.hunger = clamp(self.hunger - 8)
            self.bond = clamp(self.bond + 8)
        elif action == "groom":
            self.hygiene = clamp(self.hygiene + 35)
            self.bond = clamp(self.bond + 4)
        elif action == "rest":
            self.energy = clamp(self.energy + 30)
        elif action == "walk":
            if self.energy < 10:
                raise PetError("pet is too tired to walk")
            self.fun = clamp(self.fun + 18)
            self.energy = clamp(self.energy - 10)
            self.hygiene = clamp(self.hygiene - 6)
            self.bond = clamp(self.bond + 6)

    def tick(self, minutes: int) -> None:
        """Advance needs in 10-minute game-time steps, without randomness."""
        if not isinstance(minutes, int) or isinstance(minutes, bool) or minutes < 0:
            raise PetError("minutes must be nonnegative integer")
        steps = minutes // 10
        self.hunger = clamp(self.hunger - 2 * steps)
        self.energy = clamp(self.energy - steps)
        self.hygiene = clamp(self.hygiene - steps)
        self.fun = clamp(self.fun - steps)

    def to_dict(self) -> Dict[str, object]:
        return {key: getattr(self, key) for key in
                ("pet_id", "name", "species", "hunger", "energy", "hygiene", "fun", "bond")}


@dataclass
class HouseholdPets:
    pets: List[Pet] = field(default_factory=list)

    def adopt(self, pet: Pet) -> None:
        if len(self.pets) >= MAX_PETS:
            raise PetError("household pet limit reached")
        if any(existing.pet_id == pet.pet_id for existing in self.pets):
            raise PetError("duplicate pet_id")
        self.pets.append(pet)

    def get(self, pet_id: int) -> Pet:
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet
        raise PetError("pet not found")

    def tick(self, minutes: int) -> None:
        if not isinstance(minutes, int) or isinstance(minutes, bool) or minutes < 0:
            raise PetError("minutes must be nonnegative integer")
        for pet in self.pets:
            pet.tick(minutes)

    def to_dict(self) -> Dict[str, object]:
        return {"version": 1, "pets": [pet.to_dict() for pet in self.pets]}

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "HouseholdPets":
        if not isinstance(payload, dict) or payload.get("version") != 1:
            raise PetError("unsupported pet save version")
        records = payload.get("pets")
        if not isinstance(records, list):
            raise PetError("pets must be a list")
        household = cls()
        for record in records:
            if not isinstance(record, dict):
                raise PetError("invalid pet record")
            required = {"pet_id", "name", "species", "hunger", "energy", "hygiene", "fun", "bond"}
            if set(record) != required:
                raise PetError("unexpected/missing pet data")
            household.adopt(Pet(**record))
        return household
