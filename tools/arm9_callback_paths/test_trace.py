import os
import struct
import unittest
from pathlib import Path
import trace

class PureTests(unittest.TestCase):
    def test_direct_ldr(self):
        self.assertEqual(trace.decode_ldr_literal(0xE59F0054, 0x020D7830), 0x020D788C)

    def test_backward_ldr(self):
        self.assertEqual(trace.decode_ldr_literal(0xE51F0004, 0x1000), 0x1004)

    def test_reject_non_ldr(self):
        with self.assertRaises(ValueError):
            trace.decode_ldr_literal(0, 0)

    def test_blx_r3(self):
        self.assertEqual(trace.decode_blx_register(0xE12FFF33), 3)

    def test_reject_bx_r3(self):
        with self.assertRaises(ValueError):
            trace.decode_blx_register(0xE12FFF13)

    def test_short_data(self):
        with self.assertRaises(ValueError):
            trace.read32(b'\0\0', 0)

class ROMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.getenv('SIMS3_DS_ROM')
        if not path:
            raise unittest.SkipTest('SIMS3_DS_ROM not set; no originals in public CI')
        cls.rom = Path(path).read_bytes()

    def test_original(self):
        result = trace.inspect(self.rom)
        self.assertEqual(len(result['callback_invocation_paths']), 3)
        self.assertEqual(result['new_third_path']['call'], '0x020d7858')

    def test_hash_guard(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            trace.inspect(self.rom[:-1])

    def mutate(self, address):
        raw = bytearray(self.rom)
        off, base = (struct.unpack_from('<I', raw, p)[0] for p in (0x20, 0x28))
        raw[off + address - base] ^= 1
        return raw

    def test_bad_new_callback_read(self):
        with self.assertRaisesRegex(ValueError, 'anchor mismatch'):
            trace.inspect(self.mutate(0x020D7840), check_sha=False)

    def test_bad_new_callback_blx(self):
        with self.assertRaisesRegex(ValueError, 'anchor mismatch'):
            trace.inspect(self.mutate(0x020D7858), check_sha=False)

    def test_bad_null_check(self):
        with self.assertRaisesRegex(ValueError, 'anchor mismatch'):
            trace.inspect(self.mutate(0x020D7844), check_sha=False)

    def test_bad_state_literal(self):
        with self.assertRaisesRegex(ValueError, 'anchor mismatch'):
            trace.inspect(self.mutate(0x020D788C), check_sha=False)

if __name__ == '__main__':
    unittest.main()
