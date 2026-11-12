"""Public, no-ROM gameplay tests for the standalone Pets prototype."""
import unittest

from tools.pets import HouseholdPets, Pet, PetError


class PetGameplayTests(unittest.TestCase):
    def test_adoption_and_save_roundtrip(self):
        household = HouseholdPets()
        household.adopt(Pet(1, "Mochi", "cat"))
        household.adopt(Pet(2, "Scout", "dog"))
        saved = household.to_dict()
        self.assertEqual(HouseholdPets.from_dict(saved).to_dict(), saved)

    def test_limited_household_and_unique_ids(self):
        household = HouseholdPets()
        for index in range(3):
            household.adopt(Pet(index, f"Pet{index}", "cat"))
        with self.assertRaises(PetError):
            household.adopt(Pet(4, "Fourth", "dog"))
        with self.assertRaises(PetError):
            HouseholdPets([Pet(1, "One", "cat")]).adopt(Pet(1, "Two", "dog"))

    def test_dog_walk_changes_stats(self):
        dog = Pet(1, "Scout", "dog", energy=20, fun=50)
        dog.interact("walk")
        self.assertEqual((dog.energy, dog.fun, dog.bond), (10, 68, 6))

    def test_cat_cannot_walk_without_mutation(self):
        cat = Pet(1, "Mochi", "cat")
        before = cat.to_dict()
        with self.assertRaises(PetError):
            cat.interact("walk")
        self.assertEqual(cat.to_dict(), before)

    def test_tired_pet_cannot_play_without_mutation(self):
        pet = Pet(1, "Tired", "dog", energy=9)
        before = pet.to_dict()
        with self.assertRaises(PetError):
            pet.interact("play")
        self.assertEqual(pet.to_dict(), before)

    def test_decay_and_clamping(self):
        pet = Pet(1, "Mochi", "cat", hunger=1, energy=2)
        pet.tick(40)
        self.assertEqual((pet.hunger, pet.energy), (0, 0))
        pet.interact("feed")
        self.assertEqual(pet.hunger, 30)
        pet.tick(0)
        self.assertEqual(pet.hunger, 30)

    def test_bad_inputs_and_save_version(self):
        with self.assertRaises(PetError):
            Pet(1, "", "cat")
        with self.assertRaises(PetError):
            Pet(1, "Alien", "horse")
        with self.assertRaises(PetError):
            Pet(1, "Nope", "dog", fun=101)
        with self.assertRaises(PetError):
            Pet(1, "Nope", "dog").tick(-10)
        with self.assertRaises(PetError):
            HouseholdPets.from_dict({"version": 9, "pets": []})


if __name__ == "__main__":
    unittest.main()
