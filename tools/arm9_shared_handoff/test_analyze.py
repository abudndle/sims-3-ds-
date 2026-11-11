"""Regression tests for the ARM7-to-ARM9 shared halfword handoff."""
import os
import struct
import unittest
from pathlib import Path

import analyze


class DecoderTests(unittest.TestCase):
    def test_literal_positive(self):
        self.assertEqual(analyze.arm_literal_address(0xE59F1004, 0x1000), 0x100C)

    def test_literal_negative(self):
        self.assertEqual(analyze.arm_literal_address(0xE51F1004, 0x1000), 0x1004)

    def test_reject_bad_opcode(self):
        with self.assertRaises(ValueError):
            analyze.arm_literal_address(0, 0x1000)

    def test_read_bounds(self):
        with self.assertRaises(ValueError):
            analyze.read32(b"\0\0", 0)


class ROMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.environ.get("SIMS3_DS_ROM")
        if not path:
            raise unittest.SkipTest("SIMS3_DS_ROM is not set; original ROM is not in public CI")
        cls.rom = Path(path).read_bytes()

    def test_valid_handoff(self):
        result = analyze.inspect(self.rom)
        self.assertEqual(result["shared_memory_address"], "0x02ffff94")

    def test_wrong_hash(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            analyze.inspect(self.rom[:-1])

    def _modified(self, header_offset, load_address):
        changed = bytearray(self.rom)
        off = struct.unpack_from("<I", changed, header_offset)[0]
        base = struct.unpack_from("<I", changed, header_offset + 8)[0]
        changed[off + load_address - base] ^= 1
        return changed

    def test_reject_arm9_bad_instruction(self):
        with self.assertRaisesRegex(ValueError, "ARM9"):
            analyze.inspect(self._modified(0x20, 0x020D7DB0), verify_hash=False)

    def test_reject_arm7_bad_store(self):
        with self.assertRaisesRegex(ValueError, "ARM7"):
            analyze.inspect(self._modified(0x30, 0x0238E478), verify_hash=False)

    def test_reject_arm9_bad_literal(self):
        with self.assertRaisesRegex(ValueError, "shared-memory"):
            analyze.inspect(self._modified(0x20, 0x020D7DE4), verify_hash=False)


if __name__ == "__main__":
    unittest.main()
