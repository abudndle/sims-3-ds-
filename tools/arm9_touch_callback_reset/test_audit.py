import os
import struct
import unittest
from pathlib import Path
import audit

class DecoderTests(unittest.TestCase):
    def test_event_literal(self):
        self.assertEqual(audit.pc_literal_address(0xE59F3240,0x020D73B0),0x020D75F8)
    def test_init_literal(self):
        self.assertEqual(audit.pc_literal_address(0xE59F4060,0x020D7604),0x020D766C)
    def test_wrong_opcode(self):
        with self.assertRaises(ValueError):
            audit.pc_literal_address(0xE5840004,0x020D7628)
    def test_wrong_type(self):
        with self.assertRaises(ValueError):
            audit.pc_literal_address(None,0)
    def test_short_header(self):
        with self.assertRaisesRegex(ValueError,'truncated'):
            audit.arm9_reader(b'\0'*16)
    def test_invalid_header(self):
        with self.assertRaisesRegex(ValueError,'header invalid'):
            audit.arm9_reader(b'\0'*64)

class OriginalROMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=os.environ.get('SIMS3_DS_ROM')
        if not path:raise unittest.SkipTest('SIMS3_DS_ROM not configured')
        cls.data=Path(path).read_bytes()
    def mutated(self, address):
        b=bytearray(self.data)
        off=struct.unpack_from('<I',b,0x20)[0]
        base=struct.unpack_from('<I',b,0x28)[0]
        b[off+address-base]^=1
        return b
    def test_original_rom(self):
        result=audit.inspect(self.data)
        self.assertEqual(result['verified_instruction_and_literal_anchors'],len(audit.ANCHORS))
        self.assertEqual(result['initialization']['callback_slot_offset'],4)
    def test_sha_guard(self):
        with self.assertRaisesRegex(ValueError,'SHA256'):
            audit.inspect(self.data[:-1])
    def test_init_reset_corruption(self):
        with self.assertRaisesRegex(ValueError,'anchor mismatch'):
            audit.inspect(self.mutated(0x020D7628),False)
    def test_init_zero_corruption(self):
        with self.assertRaisesRegex(ValueError,'anchor mismatch'):
            audit.inspect(self.mutated(0x020D7620),False)
    def test_shared_literal_corruption(self):
        with self.assertRaisesRegex(ValueError,'anchor mismatch'):
            audit.inspect(self.mutated(0x020D766C),False)
    def test_event_literal_corruption(self):
        with self.assertRaisesRegex(ValueError,'anchor mismatch'):
            audit.inspect(self.mutated(0x020D75F8),False)
    def test_callback_call_corruption(self):
        with self.assertRaisesRegex(ValueError,'anchor mismatch'):
            audit.inspect(self.mutated(0x020D73E8),False)

if __name__ == '__main__':unittest.main()
