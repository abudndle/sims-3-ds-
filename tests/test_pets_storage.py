"""No-ROM tests for isolated Pets persistence."""
import json
from pathlib import Path
import tempfile
import unittest

from tools.pets.model import HouseholdPets, Pet, PetError
from tools.pets.storage import decode, encode, load_sidecar, save_sidecar


class SidecarTests(unittest.TestCase):
    def setUp(self):
        self.household = HouseholdPets([Pet(1, "Mochi", "cat"), Pet(2, "Scout", "dog")])

    def test_round_trip(self):
        self.assertEqual(decode(encode(self.household)).to_dict(), self.household.to_dict())

    def test_corrupt_checksum_rejected(self):
        data = json.loads(encode(self.household))
        data["pets"]["pets"][0]["name"] = "Tampered"
        with self.assertRaises(PetError):
            decode(json.dumps(data).encode())

    def test_malformed_and_unsupported_versions(self):
        with self.assertRaises(PetError):
            decode(b"not json")
        data = json.loads(encode(self.household))
        data["format_version"] = 99
        with self.assertRaises(PetError):
            decode(json.dumps(data).encode())

    def test_save_load_and_replacement(self):
        with tempfile.TemporaryDirectory() as location:
            path = Path(location) / "family.pets.json"
            save_sidecar(path, self.household)
            self.assertEqual(load_sidecar(path).to_dict(), self.household.to_dict())
            self.household.get(1).interact("feed")
            save_sidecar(path, self.household)
            self.assertEqual(load_sidecar(path).to_dict(), self.household.to_dict())
            self.assertEqual(list(Path(location).glob("*.tmp")), [])

    def test_original_save_not_modified(self):
        with tempfile.TemporaryDirectory() as location:
            retail_save = Path(location) / "game.sav"
            retail_save.write_bytes(b"ORIGINAL RETAIL SAVE")
            with self.assertRaises(PetError):
                save_sidecar(retail_save, self.household)
            save_sidecar(Path(location) / "game.pets.json", self.household)
            self.assertEqual(retail_save.read_bytes(), b"ORIGINAL RETAIL SAVE")

    def test_reject_sidecar_symlink(self):
        with tempfile.TemporaryDirectory() as location:
            target = Path(location) / "target.bin"
            target.write_bytes(b"original")
            alias = Path(location) / "alias.pets.json"
            alias.symlink_to(target)
            with self.assertRaises(PetError):
                save_sidecar(alias, self.household)
            with self.assertRaises(PetError):
                load_sidecar(alias)
            self.assertEqual(target.read_bytes(), b"original")

    def test_oversized_rejected(self):
        with self.assertRaises(PetError):
            decode(b"x" * 65537)


if __name__ == "__main__":
    unittest.main()
