"""Read-only provenance tests on synthetic binaries; no commercial ROM."""
import hashlib
import unittest

from tools.pets.manifest_provenance import ManifestError, audit, parse_manifest


def fixture():
    rom = b"HEAD" + b"FIRST" + b"SECOND" + b"TRAILER"
    header = "file_id,path,offset,size,sha256\\n"
    lines = [
        "0,DATA/BACKEND/Animations.package,4,5," + hashlib.sha256(b"FIRST").hexdigest(),
        "1,DATA/BACKEND/Sims.package,9,6," + hashlib.sha256(b"SECOND").hexdigest(),
    ]
    return rom, header + "\\n".join(lines) + "\\n"


class ManifestProvenanceTests(unittest.TestCase):
    def test_matching_file_digests(self):
        rom, manifest = fixture()
        report = audit(rom, manifest, hashlib.sha256(rom).hexdigest())
        self.assertEqual(report["validated_file_records"], 2)
        self.assertEqual(report["validated_backend_package_records"], 2)
        self.assertFalse(report["patch_ready"])
        self.assertFalse(report["native_package_index_verified"])

    def test_revision_mismatch_fails_before_file_scan(self):
        rom, manifest = fixture()
        with self.assertRaisesRegex(ManifestError, "revision"):
            audit(rom, manifest)

    def test_modified_package_rejected(self):
        rom, manifest = fixture()
        edited = rom[:4] + b"OTHER" + rom[9:]
        with self.assertRaisesRegex(ManifestError, "content hash"):
            audit(edited, manifest, hashlib.sha256(edited).hexdigest())

    def test_truncated_region_rejected(self):
        rom, manifest = fixture()
        shortened = rom[:11]
        with self.assertRaisesRegex(ManifestError, "outside ROM"):
            audit(shortened, manifest, hashlib.sha256(shortened).hexdigest())

    def test_duplicate_file_ids_rejected(self):
        _, manifest = fixture()
        with self.assertRaisesRegex(ManifestError, "duplicate"):
            parse_manifest(manifest.replace("1,DATA/BACKEND/Sims", "0,DATA/BACKEND/Sims"))

    def test_path_traversal_rejected(self):
        _, manifest = fixture()
        with self.assertRaisesRegex(ManifestError, "invalid"):
            parse_manifest(manifest.replace("DATA/BACKEND/Sims.package", "../Sims.package"))

    def test_overlap_rejected(self):
        _, manifest = fixture()
        with self.assertRaisesRegex(ManifestError, "overlapping"):
            parse_manifest(manifest.replace(",9,6,", ",8,6,"))

    def test_missing_header_rejected(self):
        with self.assertRaisesRegex(ManifestError, "column"):
            parse_manifest("path,offset\\nfile,1\\n")


if __name__ == "__main__":
    unittest.main()
