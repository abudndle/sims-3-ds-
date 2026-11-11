"""Pure synthetic tests; no original game ROM or game data is distributed."""
import struct
import unittest
from classify_literals import classify_target, classify_literal, enrich
from scan import ARM9_BASE


def synthetic(words):
    rom = bytearray(0x200 + len(words) * 4)
    struct.pack_into("<IIII", rom, 0x20, 0x200, ARM9_BASE, ARM9_BASE, len(words)*4)
    for i, word in enumerate(words):
        struct.pack_into("<I", rom, 0x200+4*i, word)
    return bytes(rom)


def candidate(index):
    return {"address": f"0x{ARM9_BASE + 4*index:08X}",
            "base_register": 0, "source_register": 1}


class TargetTests(unittest.TestCase):
    def test_arm_pointer_inside(self):
        self.assertTrue(classify_target(ARM9_BASE+8, ARM9_BASE, 32)["possible_code_pointer"])

    def test_thumb_pointer_inside(self):
        r = classify_target(ARM9_BASE+9, ARM9_BASE, 32)
        self.assertEqual(r["arm_state_hint"], "Thumb")
        self.assertTrue(r["possible_code_pointer"])

    def test_unaligned_arm_not_code_shaped(self):
        self.assertFalse(classify_target(ARM9_BASE+2, ARM9_BASE, 32)["possible_code_pointer"])

    def test_external_not_code_shaped(self):
        self.assertFalse(classify_target(0x03000000, ARM9_BASE, 32)["possible_code_pointer"])

    def test_end_exclusive(self):
        self.assertFalse(classify_target(ARM9_BASE+32, ARM9_BASE, 32)["inside_loaded_arm9"])

    def test_reject_invalid_pointer_value(self):
        for v in (-1, 2**32, True):
            with self.subTest(v=v), self.assertRaises(ValueError):
                classify_target(v, ARM9_BASE, 32)


class LiteralTests(unittest.TestCase):
    def test_resolve_literal(self):
        # LDR r1,[pc,#0] at word 0 points to word 2; word 1 is STR r1,[r0,#4].
        words = [0xE59F1000, 0xE5801004, ARM9_BASE+1, 0xE1A00000]
        hits = enrich(synthetic(words), [candidate(1)], 4)
        r = hits[0]["recent_source_register_writers"][0]["resolved_literal"]
        self.assertEqual(r["status"], "readable")
        self.assertTrue(r["pointer_shape"]["possible_code_pointer"])
        self.assertEqual(r["literal_address"], f"0x{ARM9_BASE+8:08X}")

    def test_outside_literal_not_dereferenced(self):
        words=[0xE59F1FFF, 0xE5801004]
        hits=enrich(synthetic(words), [candidate(1)], 2)
        r=hits[0]["recent_source_register_writers"][0]["resolved_literal"]
        self.assertEqual(r["status"], "outside_or_unaligned_loaded_arm9")

    def test_unaligned_literal_not_read(self):
        r=classify_literal(synthetic([0, 0]), ARM9_BASE+1)
        self.assertEqual(r["status"], "outside_or_unaligned_loaded_arm9")

    def test_non_literal_writer_is_unchanged(self):
        words=[0xE3A01004, 0xE5801004]
        r=enrich(synthetic(words),[candidate(1)])[0]
        self.assertEqual(r["recent_source_register_writers"][0]["type"],"mov_immediate")
        self.assertNotIn("resolved_literal",r["recent_source_register_writers"][0])

    def test_multiple_candidates_independent(self):
        words=[0xE3A01004,0xE5801004,0xE59F1000,0xE5801004,ARM9_BASE]
        hits=enrich(synthetic(words),[candidate(1),candidate(3)],4)
        self.assertEqual(len(hits),2)
        self.assertIsNone(hits[0]["recent_source_register_writers"][0].get("resolved_literal"))
        self.assertTrue(hits[1]["recent_source_register_writers"][-1]["resolved_literal"]["pointer_shape"]["possible_code_pointer"])


if __name__ == "__main__":
    unittest.main()
