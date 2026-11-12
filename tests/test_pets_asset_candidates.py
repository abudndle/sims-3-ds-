"""Asset-free FNT/FAT fixture tests for Pets package inventory."""
import struct
import unittest

from tools.pets.asset_candidates import parse_tables, inspect


class NitroFSTests(unittest.TestCase):
    @staticmethod
    def fixture():
        # 3 directory records: root -> DATA -> BACKEND, with 2 package files.
        listing0 = bytes([0x80 | 4]) + b"DATA" + struct.pack("<H", 0xF001) + b"\0"
        listing1 = bytes([0x80 | 7]) + b"BACKEND" + struct.pack("<H", 0xF002) + b"\0"
        files = ["Animations.package", "ObjectInteractions.package"]
        listing2 = b"".join(bytes([len(name)]) + name.encode("ascii") for name in files) + b"\0"
        table = struct.pack("<IHH", 24, 0, 3)
        table += struct.pack("<IHH", 24 + len(listing0), 0, 0xF000)
        table += struct.pack("<IHH", 24 + len(listing0) + len(listing1), 0, 0xF001)
        fnt = table + listing0 + listing1 + listing2
        fat = struct.pack("<IIII", 0x400, 0x480, 0x480, 0x500)
        rom = bytearray(0x600)
        fnt_off = 0x200
        fat_off = (fnt_off + len(fnt) + 3) & ~3
        rom[fnt_off:fnt_off + len(fnt)] = fnt
        rom[fat_off:fat_off + len(fat)] = fat
        for pos, val in ((0x40, fnt_off), (0x44, len(fnt)), (0x48, fat_off), (0x4c, len(fat))):
            struct.pack_into("<I", rom, pos, val)
        return bytes(rom), fnt, fat

    def test_decode_paths_and_metadata(self):
        rom, fnt, fat = self.fixture()
        items = parse_tables(fnt, fat, len(rom))
        self.assertEqual(items["DATA/BACKEND/Animations.package"], {"file_id": 0, "size": 128})
        self.assertEqual(items["DATA/BACKEND/ObjectInteractions.package"]["file_id"], 1)

    def test_read_only_report_flags_unknown_hooks(self):
        rom, _, _ = self.fixture()
        result = inspect(rom, verify_sha=False)
        self.assertEqual(len(result["candidate_packages"]), 2)
        self.assertFalse(result["patch_ready"])
        self.assertFalse(result["pets_model_identified"])
        self.assertFalse(result["candidate_packages"][0]["pet_assets_confirmed"])

    def test_default_rejects_unknown_rom(self):
        with self.assertRaisesRegex(ValueError, "unsupported original"):
            inspect(self.fixture()[0])

    def test_reject_corrupt_fat_bounds(self):
        rom, fnt, fat = self.fixture()
        corrupt = bytearray(fat)
        struct.pack_into("<I", corrupt, 4, len(rom) + 1)
        with self.assertRaisesRegex(ValueError, "file bounds"):
            parse_tables(fnt, bytes(corrupt), len(rom))

    def test_reject_truncated_fnt(self):
        _, fnt, fat = self.fixture()
        with self.assertRaises(ValueError):
            parse_tables(fnt[:23], fat, 0x600)

    def test_reject_invalid_directory_ref(self):
        _, fnt, fat = self.fixture()
        corrupt = bytearray(fnt)
        # root first listing: length 0x84, name DATA at [25:29], child at [29:31]
        struct.pack_into("<H", corrupt, 29, 0xFFFF)
        with self.assertRaisesRegex(ValueError, "subdirectory"):
            parse_tables(bytes(corrupt), fat, 0x600)

    def test_reject_missing_fat_entry(self):
        _, fnt, fat = self.fixture()
        with self.assertRaises(ValueError):
            parse_tables(fnt, fat[:8], 0x600)


if __name__ == "__main__":
    unittest.main()
