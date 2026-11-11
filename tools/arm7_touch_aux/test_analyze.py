"""Regression suite; set SIMS3_DS_ROM for ROM-based assertions."""
import os,struct,unittest
from pathlib import Path
import analyze

class DecodeTests(unittest.TestCase):
    def test_aux_12bit(self):
        d=analyze.decode_command(0xE4)
        self.assertEqual((d["channel_name"],d["mode_bits"],d["single_ended"]),("AUX",12,True))
    def test_aux_8bit(self):
        d=analyze.decode_command(0xEC)
        self.assertEqual((d["channel_name"],d["mode_bits"]),("AUX",8))
    def test_coordinate_comparison(self):
        self.assertEqual(analyze.decode_command(0xD4)["channel_name"],"X")
        self.assertEqual(analyze.decode_command(0x94)["channel_name"],"Y")
    def test_missing_start(self):
        with self.assertRaises(ValueError):analyze.decode_command(0x64)
    def test_bad_range(self):
        for n in (-1,256):
            with self.assertRaises(ValueError):analyze.decode_command(n)

class OriginalROMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=os.environ.get("SIMS3_DS_ROM")
        if not path:raise unittest.SkipTest("SIMS3_DS_ROM not set; originals stay outside public CI")
        cls.rom=Path(path).read_bytes()
    def test_original(self):
        result=analyze.inspect(self.rom)
        self.assertEqual(result["verified_sites"],13)
        self.assertEqual([d["channel"] for d in result["commands"]],[6,6])
    def test_wrong_hash(self):
        with self.assertRaisesRegex(ValueError,"hash"):analyze.inspect(self.rom[:-1])
    def modified(self,address):
        data=bytearray(self.rom);offset=struct.unpack_from("<I",data,0x30)[0]
        data[offset+address-analyze.BASE]^=1
        return data
    def test_corrupt_command(self):
        with self.assertRaisesRegex(ValueError,"mismatch"):analyze.inspect(self.modified(0x0238E8D4),False)
    def test_corrupt_spi_pointer(self):
        with self.assertRaisesRegex(ValueError,"mismatch"):analyze.inspect(self.modified(0x0238E86C),False)

if __name__=="__main__":unittest.main()
