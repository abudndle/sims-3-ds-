"""Regression tests for a future native-host adapter boundary (no ROM)."""
import copy
import unittest

from tools.pets.bridge import dispatch
from tools.pets.model import PetError
from tools.pets.session import PetsSession


class PetsBridgeTests(unittest.TestCase):
    def setUp(self):
        self.session = PetsSession()

    def send(self, **values):
        return dispatch(self.session, values)

    def test_full_lot_sequence_and_snapshot(self):
        self.send(type="enter_mode", mode="lot")
        self.send(type="adopt", pet_id=5, name="Scout", species="dog")
        self.send(type="select", pet_id=5)
        result = self.send(type="interact", action="feed")
        self.assertEqual(result["household"]["pets"][0]["hunger"], 100)
        result["household"]["pets"][0]["hunger"] = 0
        self.assertEqual(self.session.household.get(5).hunger, 100)

    def test_unexpected_fields_rejected_before_mutation(self):
        self.send(type="enter_mode", mode="lot")
        before = copy.deepcopy(self.session.snapshot())
        with self.assertRaises(PetError):
            self.send(type="adopt", pet_id=1, name="Cat", species="cat", script="write ROM")
        self.assertEqual(self.session.snapshot(), before)

    def test_unknown_and_invalid_values_rejected(self):
        values = [
            None, [], {"type": "execute", "command": "anything"},
            {"type": "select", "pet_id": True},
            {"type": "select", "pet_id": -1},
            {"type": "adopt", "pet_id": 1, "name": "Cat", "species": "bird"},
            {"type": "interact", "action": "teleport"},
            {"type": "advance_time", "minutes": True},
            {"type": "advance_time", "minutes": 1441},
            {"type": "enter_mode", "mode": "unknown"},
            {"type": "snapshot", "hidden": 1},
        ]
        before = copy.deepcopy(self.session.snapshot())
        for value in values:
            with self.subTest(value=value), self.assertRaises(PetError):
                dispatch(self.session, value)
            self.assertEqual(self.session.snapshot(), before)

    def test_mode_transitions_block_pet_actions(self):
        self.send(type="enter_mode", mode="lot")
        self.send(type="adopt", pet_id=1, name="Mochi", species="cat")
        self.send(type="select", pet_id=1)
        for mode in ("map", "buy", "build", "social", "paused"):
            self.send(type="enter_mode", mode=mode)
            before = copy.deepcopy(self.session.snapshot())
            with self.assertRaises(PetError):
                self.send(type="interact", action="feed")
            self.assertEqual(self.session.snapshot(), before)

    def test_no_time_decay_outside_lot(self):
        self.send(type="enter_mode", mode="lot")
        self.send(type="adopt", pet_id=2, name="Scout", species="dog")
        self.send(type="enter_mode", mode="buy")
        self.send(type="advance_time", minutes=100)
        self.assertEqual(self.session.household.get(2).hunger, 80)
        self.send(type="enter_mode", mode="lot")
        self.send(type="advance_time", minutes=10)
        self.assertEqual(self.session.household.get(2).hunger, 78)

    def test_failed_interaction_is_atomic(self):
        self.send(type="enter_mode", mode="lot")
        self.send(type="adopt", pet_id=2, name="Mochi", species="cat")
        self.send(type="select", pet_id=2)
        before = copy.deepcopy(self.session.snapshot())
        with self.assertRaises(PetError):
            self.send(type="interact", action="walk")
        self.assertEqual(self.session.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
