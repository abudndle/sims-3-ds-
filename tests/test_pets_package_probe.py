"""Synthetic-ROM regression tests for read-only package-signature evidence."""
import struct
import unittest

from tools.pets.package_probe import inspect
from tests.test_pets_asset_candidates import NitroFSTests


class PackageProbeTests(unittest.TestCase):
    def fixture(self, magic=b"DBPF"):
        rom = bytearray(NitroFSTests.fixture()[0])
        rom[0x400:0x404] = magic
        rom[0x480:0x484] = b"ABCD"
        return bytes(rom)

    def test_reports_known_signature_only_as_candidate(self):
        result = inspect(self.fixture(), verify_sha=False)
        self.assertEqual(result["packages_examined"], 2)
        package = next(p for p in result["packages"] if p["path"].endswith("Animations.package"))
        self.assertEqual(package["header_signature_hex"], "44425046")
        self.assertIn("UNVERIFIED", package["signature_classification"])
        self.assertFalse(package["resource_index_verified"])
        self.assertFalse(result["patch_ready"])

    def test_unknown_signature_not_misidentified(self):
        result = inspect(self.fixture(b"XYZ!"), verify_sha=False)
        package = next(p for p in result["packages"] if p["path"].endswith("Animations.package"))
        self.assertIn("unknown", package["signature_classification"])

    def test_default_revision_check(self):
        with self.assertRaisesRegex(ValueError, "unsupported original"):
            inspect(self.fixture())

    def test_modified_fat_bounds_rejected(self):
        rom = bytearray(self.fixture())
        fat_start = struct.unpack_from("<I", rom, 0x48)[0]
        struct.pack_into("<I", rom, fat_start + 4, len(rom) + 1)
        with self.assertRaisesRegex(ValueError, "file bounds"):
            inspect(bytes(rom), verify_sha=False)

    def test_truncated_rom_rejected(self):
        with self.assertRaisesRegex(ValueError, "truncated"):
            inspect(b"test", verify_sha=False)


if __name__ == "__main__":
    unittest.main()
