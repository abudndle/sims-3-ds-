"""Synthetic ARM9 tests; no game assets required."""
import struct
import unittest
import explain
from scan import ARM9_BASE


def fake_rom(words):
    rom = bytearray(0x200 + 4 * len(words))
    struct.pack_into("<IIII", rom, 0x20, 0x200, ARM9_BASE, ARM9_BASE, len(words)*4)
    for index, word in enumerate(words):
        struct.pack_into("<I", rom, 0x200+4*index, word)
    return bytes(rom)


def one_candidate(index, source=1, base=0):
    return {"address": f"0x{ARM9_BASE+index*4:08X}",
            "source_register": source, "base_register": base}


class DecodeTests(unittest.TestCase):
    def test_mov_immediate(self):
        self.assertEqual(explain.arm_mov_immediate(0xE3A010D8),
                         {"register": 1, "value": 216})

    def test_rotated_immediate(self):
        self.assertEqual(explain.arm_mov_immediate(0xE3A014FF),
                         {"register": 1, "value": 0xFF000000})

    def test_conditional_mov(self):
        self.assertEqual(explain.arm_mov_immediate(0x03A01004),
                         {"register": 1, "value": 4})

    def test_non_mov_is_rejected(self):
        self.assertIsNone(explain.arm_mov_immediate(0xE5901004))

    def test_literal_pc(self):
        self.assertEqual(explain.arm_ldr_literal(0xE59F1008, ARM9_BASE),
                         {"register": 1, "literal_address": ARM9_BASE+16})

    def test_non_literal_is_rejected(self):
        self.assertIsNone(explain.arm_ldr_literal(0xE5901008, ARM9_BASE))


class WindowTests(unittest.TestCase):
    def test_recent_immediate_provenance(self):
        rom=fake_rom([0xE3A010D8,0xE1A00000,0xE5801004])
        record=explain.provenance_hints(rom,[one_candidate(2)])[0]
        self.assertEqual(record["last_candidate_writer"]["type"],"mov_immediate")

    def test_last_candidate_wins(self):
        rom=fake_rom([0xE3A010D8,0xE3A01091,0xE5801004])
        record=explain.provenance_hints(rom,[one_candidate(2)])[0]
        self.assertEqual(record["last_candidate_writer"]["detail"]["value"],0x91)

    def test_unrelated_source_register_ignored(self):
        rom=fake_rom([0xE3A02004,0xE5801004])
        self.assertIsNone(explain.provenance_hints(rom,[one_candidate(1)])[0]["last_candidate_writer"])

    def test_lookback_boundary(self):
        rom=fake_rom([0xE3A010D8,0xE1A00000,0xE5801004])
        self.assertIsNone(explain.provenance_hints(rom,[one_candidate(2)],1)[0]["last_candidate_writer"])

    def test_corrupt_underlying_store_is_rejected(self):
        rom=fake_rom([0xE5901004])
        with self.assertRaisesRegex(ValueError, "does not match"):
            explain.provenance_hints(rom,[one_candidate(0)])

    def test_outside_arm9_rejected(self):
        rom=fake_rom([0xE5801004])
        with self.assertRaisesRegex(ValueError, "outside"):
            explain.provenance_hints(rom,[one_candidate(2)])

    def test_invalid_window(self):
        for window in (0,33,True):
            with self.subTest(window=window),self.assertRaises(ValueError):
                explain.provenance_hints(fake_rom([0xE5801004]),[],window)


if __name__ == "__main__":
    unittest.main()
