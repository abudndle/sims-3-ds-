import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'audit_ds_apartments.py'
spec = importlib.util.spec_from_file_location('audit_ds_apartments', MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ApartmentAuditTests(unittest.TestCase):
    def test_detects_filename_ascii_and_utf16(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'Mesa Flats.dst').write_bytes(b'no secret here')
            (root / 'scene.bin').write_bytes(b'Go to Belladonna Cove Condos' + 'Strangetown Apartments'.encode('utf-16le'))
            report = module.scan(root)
            self.assertEqual(report['scanned_files'], 2)
            self.assertEqual(len(report['findings']), 2)
            a, b = report['findings']
            self.assertIn('mesa flats', a['matches'])
            self.assertTrue(any(x['source'] == 'filename' for x in a['matches']['mesa flats']))
            self.assertTrue(any(x['source'] == 'ascii' for x in b['matches']['belladonna']))
            self.assertTrue(any(x['source'] == 'utf16le' for x in b['matches']['strangetown']))
            self.assertNotIn('Go to Belladonna', str(report))

    def test_skips_large_files_and_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'big_apartment.bin').write_bytes(b'x' * 20)
            (root / 'empty.bin').write_bytes(b'normal')
            (root / 'linked_apartment').symlink_to(root / 'big_apartment.bin')
            report = module.scan(root, max_bytes=10)
            self.assertEqual(report['scanned_files'], 1)
            self.assertEqual(report['skipped_files'], 2)
            self.assertFalse(report['findings'])

    def test_rejects_file_as_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rom.nds'
            path.write_bytes(b'data')
            with self.assertRaises(ValueError):
                module.scan(path)


if __name__ == '__main__':
    unittest.main()
