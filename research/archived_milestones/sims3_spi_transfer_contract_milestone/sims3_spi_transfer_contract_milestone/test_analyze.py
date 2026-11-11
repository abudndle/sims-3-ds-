import struct
import unittest
from analyze import BASE, CHECKS, arm_bl_target, check_arm7, word

class SPITransferContractTests(unittest.TestCase):
    def setUp(self):
        size = max(CHECKS) - BASE + 4
        self.data = bytearray(size)
        for address, (opcode, _) in CHECKS.items():
            struct.pack_into('<I', self.data, address - BASE, opcode)

    def test_known_opcode_contract(self):
        result = check_arm7(self.data)
        self.assertEqual(result['read_helper']['returned_width_bits'], 8)

    def test_helper_target_forward(self):
        self.assertEqual(arm_bl_target(0x0238CA04, 0xEB000009), 0x0238CA30)

    def test_helper_target_backward(self):
        self.assertEqual(arm_bl_target(0x0238CA80, 0xEBFFFFEA), 0x0238CA30)

    def test_mutated_return_mask_rejected(self):
        tampered = self.data[:]
        struct.pack_into('<I', tampered, 0x0238CAB0 - BASE, 0xE2000CFF)
        with self.assertRaisesRegex(ValueError, 'unexpected ARM7'):
            check_arm7(tampered)

    def test_mutated_spi_control_rejected(self):
        tampered = self.data[:]
        struct.pack_into('<I', tampered, 0x0238CAC0 - BASE, 0x8201)
        with self.assertRaises(ValueError):
            check_arm7(tampered)

    def test_bad_arm_bl_rejected(self):
        with self.assertRaises(ValueError):
            arm_bl_target(0x0238CA04, 0xE1A00000)

    def test_address_boundaries(self):
        with self.assertRaises(ValueError):
            word(self.data, BASE - 4)
        with self.assertRaises(ValueError):
            word(self.data, BASE + len(self.data))

    def test_misaligned_address_rejected(self):
        with self.assertRaises(ValueError):
            word(self.data, BASE + 1)

    def test_send_payload_is_masked_to_byte(self):
        self.assertEqual(CHECKS[0x0238CA14][0], 0xE20610FF)
        self.assertEqual(CHECKS[0x0238CAB0][0], 0xE20000FF)

if __name__ == '__main__':
    unittest.main()
