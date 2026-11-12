"""Synthetic-only tests for exact-package validation without a full retail ROM."""
import hashlib
import unittest

from tools.pets.local_package_verification import verify_package
from tools.pets.manifest_provenance import ManifestError

PATH = "DATA/BACKEND/Animations.package"


def manifest(package):
    header = "file_id,path,offset,size,sha256\n"
    return header + f"0,{PATH},1024,{len(package)},{hashlib.sha256(package).hexdigest()}\n"


class LocalPackageVerificationTests(unittest.TestCase):
    def test_matching_package_is_verified_without_claiming_models(self):
        data = b"UNKN" + b"testcontent"
        result = verify_package(data, manifest(data), PATH)
        self.assertTrue(result["exact_archived_package_verified"])
        self.assertFalse(result["pet_models_verified"])
        self.assertFalse(result["patch_ready"])
        self.assertIsNone(result["candidate_index_profile"])

    def test_hash_mismatch_blocks_inference(self):
        data = b"UNKN" + b"testcontent"
        changed = b"UNKN" + b"testcontenx"
        with self.assertRaisesRegex(ManifestError, "SHA-256"):
            verify_package(changed, manifest(data), PATH)

    def test_size_mismatch(self):
        data = b"ABCD"
        with self.assertRaisesRegex(ManifestError, "size mismatch"):
            verify_package(data + b"x", manifest(data), PATH)

    def test_wrong_path_rejected(self):
        data = b"ABCD"
        with self.assertRaisesRegex(ManifestError, "not found"):
            verify_package(data, manifest(data), "DATA/BACKEND/Sims.package")

    def test_unknown_container_not_claimed_as_valid_index(self):
        data = b"DBPF" + b"\\0" * 100
        result = verify_package(data, manifest(data), PATH)
        self.assertIsNone(result["candidate_index_profile"])
        self.assertFalse(result["native_ds_resource_format_verified"])

    def test_reject_excessive_size(self):
        with self.assertRaisesRegex(ManifestError, "oversized"):
            verify_package(b"x" * (64 * 1024 * 1024 + 1), manifest(b"x"), PATH)

    def test_no_proprietary_payload_in_report(self):
        data = b"UNKN" + b"SECRET_PAYLOAD_BYTES"
        result = verify_package(data, manifest(data), PATH)
        self.assertNotIn("SECRET_PAYLOAD_BYTES", repr(result))


if __name__ == "__main__":
    unittest.main()
