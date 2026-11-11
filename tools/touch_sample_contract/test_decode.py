import unittest
from dataclasses import replace
from decode import TouchSample, pack, unpack, requires_recheck


class TouchSampleContractTests(unittest.TestCase):
    def test_zero_is_pen_up(self):
        self.assertEqual(unpack(0), TouchSample(0, 0, False, 0, 0))

    def test_all_bits_round_trip(self):
        self.assertEqual(pack(unpack(0xFFFFFFFF)), 0xFFFFFFFF)

    def test_axis_boundaries(self):
        sample = TouchSample(4095, 0, True, 0, 0)
        self.assertEqual(pack(sample), 0x01000FFF)
        self.assertEqual(unpack(pack(sample)), sample)

    def test_y_shift(self):
        self.assertEqual(pack(TouchSample(0, 4095, False, 0, 0)), 0x00FFF000)

    def test_status_meaning(self):
        for status, expected in [(0,(False,False)), (1,(True,False)),
                                 (2,(False,True)), (3,(True,True))]:
            with self.subTest(status=status):
                sample=unpack(0x01000000 | (status << 25))
                self.assertEqual((sample.x_fallback, sample.y_fallback), expected)

    def test_preserve_opaque_bits(self):
        self.assertEqual(unpack(0xF8000000).opaque_high, 31)
        self.assertEqual(pack(unpack(0xF8000000)), 0xF8000000)

    def test_status_three_is_ambiguous(self):
        self.assertTrue(requires_recheck(unpack(0x07000000)))

    def test_pen_up_is_not_valid_press_even_with_coordinates(self):
        self.assertTrue(requires_recheck(unpack(0x000ABC12)))

    def test_status_one_can_be_processed_but_is_fallback(self):
        sample=unpack(0x03000120)
        self.assertFalse(requires_recheck(sample))
        self.assertTrue(sample.x_fallback)

    def test_reject_bad_word(self):
        for word in (-1, 2**32, True, 1.0):
            with self.subTest(word=word), self.assertRaises(ValueError):
                unpack(word)

    def test_reject_invalid_fields(self):
        valid=TouchSample(0,0,False,0,0)
        for changed in (replace(valid, raw_x=4096), replace(valid, raw_y=-1),
                        replace(valid, sample_status=4), replace(valid, opaque_high=32),
                        replace(valid, pen_down=1), replace(valid, raw_x=True)):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                pack(changed)

    def test_full_sample_space_invariants(self):
        for x in (0,1,8,2048,4095):
            for y in (0,7,2048,4095):
                for status in range(4):
                    for pen in (False,True):
                        sample=TouchSample(x,y,pen,status,23)
                        self.assertEqual(unpack(pack(sample)),sample)


if __name__ == '__main__':
    unittest.main()
