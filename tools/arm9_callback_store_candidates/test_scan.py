import struct
import unittest
import scan


def fake_rom(words):
    base = scan.ARM9_BASE
    header = bytearray(0x200)
    struct.pack_into("<IIII", header, 0x20, 0x200, base, base, len(words) * 4)
    return bytes(header) + struct.pack("<" + "I" * len(words), *words)


class CandidateDecoderTests(unittest.TestCase):
    def test_unconditional_str(self):
        self.assertEqual(scan.store_word_immediate(0xE5801004),
                         {"condition": 14, "base_register": 0, "source_register": 1})

    def test_conditional_str(self):
        self.assertEqual(scan.store_word_immediate(0x05821004),
                         {"condition": 0, "base_register": 2, "source_register": 1})

    def test_reject_load(self):
        self.assertIsNone(scan.store_word_immediate(0xE5901004))

    def test_reject_strb(self):
        self.assertIsNone(scan.store_word_immediate(0xE5C01004))

    def test_reject_postindexed(self):
        self.assertIsNone(scan.store_word_immediate(0xE4801004))

    def test_reject_negative_offset(self):
        self.assertIsNone(scan.store_word_immediate(0xE5001004))

    def test_reject_register_offset(self):
        self.assertIsNone(scan.store_word_immediate(0xE7801001))

    def test_reject_wrong_offset(self):
        self.assertIsNone(scan.store_word_immediate(0xE5801008))

    def test_reject_pc_base(self):
        self.assertIsNone(scan.store_word_immediate(0xE58F1004))

    def test_reject_bad_values(self):
        for value in (-1, 2**32, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                scan.store_word_immediate(value)

    def test_hit_with_synthetic_rom(self):
        report = scan.scan(fake_rom([0xE5801004, 0xE5901004, 0x05821004]),
                           require_exact_sha=False)
        self.assertEqual(report["hit_count"], 2)
        self.assertEqual([item["address"] for item in report["instruction_shaped_hits"]],
                         ["0x02004000", "0x02004008"])

    def test_window_excludes_hits(self):
        report = scan.scan(fake_rom([0xE5801004, 0xE5901004]),
                           require_exact_sha=False,
                           start=scan.ARM9_BASE + 4, end=scan.ARM9_BASE + 8)
        self.assertEqual(report["hit_count"], 0)

    def test_wrong_hash_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            scan.scan(fake_rom([0xE5801004]))

    def test_bad_window(self):
        rom = fake_rom([0xE5801004, 0xE5801004])
        for params in ({"start": scan.ARM9_BASE + 1},
                       {"end": scan.ARM9_BASE + 20},
                       {"start": scan.ARM9_BASE + 8, "end": scan.ARM9_BASE + 4}):
            with self.subTest(params=params), self.assertRaises(ValueError):
                scan.scan(rom, False, **params)


if __name__ == "__main__":
    unittest.main()
