"""Synthetic fixture tests: no retail ROM or game assets required."""
import struct
import unittest

from tools.arm9_event_boundary.analyze import ANCHORS
from tools.pets.native_readiness import inspect


class NativeReadinessTests(unittest.TestCase):
    @staticmethod
    def fixture():
        # Fake ARM9 containing ONLY the known static audit anchors. This is not
        # game code, and must never be treated as a patchable retail ROM.
        base, off = 0x02004000, 0x200
        size = 0xD4000
        rom = bytearray(off + size + 0x300)
        for header_offset, value in ((0x20, off), (0x28, base), (0x2c, size),
                                     (0x30, off + size), (0x3c, 0x40),
                                     (0x40, off + size + 0x40), (0x44, 0x20),
                                     (0x48, off + size + 0x60), (0x4c, 0x10),
                                     (0x50, off + size + 0x80), (0x54, 0x40),
                                     (0x58, 0), (0x5c, 0)):
            struct.pack_into("<I", rom, header_offset, value)
        for address, opcode in ANCHORS.items():
            struct.pack_into("<I", rom, off + address - base, opcode)
        # For literal_address() the 0x020D74EC LDR points to 0x020D75FC,
        # which the anchor set already preserves.
        return bytes(rom)

    def test_static_inventory_never_claims_a_patch(self):
        result = inspect(self.fixture(), verify_sha=False)
        self.assertEqual(result["arm9_overlay_records"], 2)
        self.assertEqual(result["nitrofs_fat_records"], 2)
        self.assertFalse(result["known_original_revision"])
        self.assertFalse(result["patch_ready"])
        self.assertFalse(result["pets_actor_hook_verified"])

    def test_retail_sha_required_by_default(self):
        with self.assertRaisesRegex(ValueError, "unsupported game ROM"):
            inspect(self.fixture())

    def test_reject_bad_overlay_table_length(self):
        data = bytearray(self.fixture())
        struct.pack_into("<I", data, 0x54, 33)
        with self.assertRaisesRegex(ValueError, "divisible by 32"):
            inspect(bytes(data), verify_sha=False)

    def test_reject_out_of_bounds_table(self):
        data = bytearray(self.fixture())
        struct.pack_into("<I", data, 0x48, len(data) - 4)
        with self.assertRaisesRegex(ValueError, "NitroFS FAT"):
            inspect(bytes(data), verify_sha=False)

    def test_reject_modified_touch_anchor(self):
        data = bytearray(self.fixture())
        struct.pack_into("<I", data, 0x200 + 0x020D757C - 0x02004000, 0)
        with self.assertRaisesRegex(ValueError, "anchor mismatch"):
            inspect(bytes(data), verify_sha=False)

    def test_reject_truncated_header(self):
        with self.assertRaisesRegex(ValueError, "truncated"):
            inspect(b"short", verify_sha=False)


if __name__ == "__main__":
    unittest.main()
