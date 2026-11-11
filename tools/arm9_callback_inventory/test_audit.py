import os
import struct
import unittest
from pathlib import Path
import audit

class Helpers(unittest.TestCase):
    def test_positive_literal(self):
        self.assertEqual(audit.literal_target(0xE59F4060, 0x020D7604), 0x020D766C)
    def test_negative_literal(self):
        self.assertEqual(audit.literal_target(0xE51F1004, 0x1000), 0x1004)
    def test_bad_literal(self):
        with self.assertRaises(ValueError):
            audit.literal_target(0, 0)
    def test_bad_word(self):
        with self.assertRaises(ValueError):
            audit.word(b"\0" * 3, 0)
    def test_reference_scan_tiny(self):
        data = struct.pack("<III", 0xE59F0000, 0, audit.STATE_BLOCK)
        self.assertEqual(audit.scan_references(data, 0x1000), {0x1000: 0x1008})
    def test_reference_scan_nonload(self):
        data = struct.pack("<III", 0xE1A00000, 0, audit.STATE_BLOCK)
        self.assertEqual(audit.scan_references(data, 0x1000), {})

class OriginalROM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.getenv("SIMS3_DS_ROM")
        if not path:
            raise unittest.SkipTest("Set SIMS3_DS_ROM for original-ROM assertions")
        cls.rom = Path(path).read_bytes()
    def test_complete_inventory(self):
        result = audit.inspect(self.rom)
        self.assertEqual(result["reference_count"], 9)
        self.assertEqual(result["callback_field_address"], "0x224fce8")
    def test_hash_guard(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            audit.inspect(self.rom[:-1])
    def changed(self, address):
        raw = bytearray(self.rom)
        off = struct.unpack_from("<I", raw, 0x20)[0]
        base = struct.unpack_from("<I", raw, 0x28)[0]
        raw[off + address - base] ^= 1
        return raw
    def test_modified_callback_clear(self):
        with self.assertRaisesRegex(ValueError, "anchor mismatch"):
            audit.inspect(self.changed(0x020D7628), False)
    def test_modified_input_callback(self):
        with self.assertRaisesRegex(ValueError, "anchor mismatch"):
            audit.inspect(self.changed(0x020D757C), False)
    def test_modified_literal(self):
        with self.assertRaisesRegex(ValueError, "anchor mismatch"):
            audit.inspect(self.changed(0x020D766C), False)
    def test_modified_reference_inventory(self):
        with self.assertRaisesRegex(ValueError, "reference inventory"):
            audit.inspect(self.changed(0x020D788C), False)

if __name__ == "__main__":
    unittest.main()
