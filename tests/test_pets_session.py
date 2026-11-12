import unittest

from tools.pets.model import PetError
from tools.pets.session import PetsSession, LOT, MAP, BUILD, BUY, SOCIAL, PAUSED


class PetsSessionTests(unittest.TestCase):
    def test_map_blocks_adoption_and_interaction(self):
        session = PetsSession()
        with self.assertRaises(PetError):
            session.adopt(1, "Mochi", "cat")
        session.enter_mode(LOT)
        session.adopt(1, "Mochi", "cat")
        session.select(1)
        session.enter_mode(MAP)
        with self.assertRaises(PetError):
            session.interact("feed")
        self.assertIsNone(session.selected_pet_id)

    def test_every_non_lot_mode_blocks_actions(self):
        session = PetsSession(mode=LOT)
        session.adopt(1, "Scout", "dog")
        session.select(1)
        for mode in (MAP, BUILD, BUY, SOCIAL, PAUSED):
            session.enter_mode(mode)
            before = session.snapshot()
            with self.assertRaises(PetError):
                session.interact("play")
            self.assertEqual(session.snapshot(), before)

    def test_lot_return_requires_reselecting(self):
        session = PetsSession(mode=LOT)
        session.adopt(1, "Scout", "dog")
        session.select(1)
        session.enter_mode(BUY)
        session.enter_mode(LOT)
        with self.assertRaises(PetError):
            session.interact("feed")
        session.select(1)
        self.assertEqual(session.interact("feed")["hunger"], 100)

    def test_time_only_advances_in_lot(self):
        session = PetsSession(mode=LOT)
        session.adopt(1, "Scout", "dog")
        session.enter_mode(BUILD)
        session.advance_time(20)
        self.assertEqual(session.household.get(1).hunger, 80)
        session.enter_mode(LOT)
        session.advance_time(20)
        self.assertEqual(session.household.get(1).hunger, 76)

    def test_invalid_mode_and_pet_selection(self):
        session = PetsSession(mode=LOT)
        with self.assertRaises(PetError):
            session.enter_mode("loading")
        self.assertEqual(session.mode, LOT)
        with self.assertRaises(PetError):
            session.select(7)
        with self.assertRaises(PetError):
            session.advance_time(-1)
        with self.assertRaises(PetError):
            session.advance_time(True)


if __name__ == "__main__":
    unittest.main()
