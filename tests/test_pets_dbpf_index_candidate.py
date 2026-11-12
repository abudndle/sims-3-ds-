"""Fully synthetic candidate-index tests, no private game material."""
import struct
import unittest

from tools.pets.dbpf_index_candidate import IndexFormatError, probe_dbpf_v1


def make_package():
    payload = bytearray(0x100)
    payload[:4] = b"DBPF"
    struct.pack_into("<III", payload, 4, 1, 0, 0)
    # Synthetic fixed-20 profile: index at 0x40; payload after index at 0x80.
    struct.pack_into("<IIII", payload, 0x20, 7, 2, 0x40, 40)
    struct.pack_into("<IIIII", payload, 0x40, 0x123, 1, 5, 0x80, 16)
    struct.pack_into("<IIIII", payload, 0x54, 0x456, 1, 6, 0xA0, 16)
    return bytes(payload)


class CandidateIndexTests(unittest.TestCase):
    def test_strict_synthetic_profile(self):
        result = probe_dbpf_v1(make_package())
        self.assertEqual(result["index_entry_count"], 2)
        self.assertEqual(result["resource_types"], ["0x00000123", "0x00000456"])
        self.assertFalse(result["ds_format_confirmed"])

    def test_reject_unknown_signature(self):
        with self.assertRaises(IndexFormatError):
            probe_dbpf_v1(b"JUNK" + make_package()[4:])

    def test_reject_unknown_version(self):
        buf = bytearray(make_package())
        struct.pack_into("<I", buf, 0x20, 8)
        with self.assertRaisesRegex(IndexFormatError, "unsupported"):
            probe_dbpf_v1(bytes(buf))

    def test_reject_index_overrun(self):
        buf = bytearray(make_package())
        struct.pack_into("<I", buf, 0x28, 0xFF)
        with self.assertRaisesRegex(IndexFormatError, "outside"):
            probe_dbpf_v1(bytes(buf))

    def test_reject_index_count_mismatch(self):
        buf = bytearray(make_package())
        struct.pack_into("<I", buf, 0x24, 3)
        with self.assertRaisesRegex(IndexFormatError, "index size"):
            probe_dbpf_v1(bytes(buf))

    def test_reject_resource_over_index(self):
        buf = bytearray(make_package())
        struct.pack_into("<I", buf, 0x40 + 12, 0x48)
        with self.assertRaisesRegex(IndexFormatError, "overlaps index"):
            probe_dbpf_v1(bytes(buf))

    def test_reject_duplicate_key(self):
        buf = bytearray(make_package())
        struct.pack_into("<III", buf, 0x54, 0x123, 1, 5)
        with self.assertRaisesRegex(IndexFormatError, "duplicate"):
            probe_dbpf_v1(bytes(buf))

    def test_reject_payload_overlap(self):
        buf = bytearray(make_package())
        struct.pack_into("<I", buf, 0x54 + 12, 0x88)
        with self.assertRaisesRegex(IndexFormatError, "overlapping resources"):
            probe_dbpf_v1(bytes(buf))

    def test_reject_invalid_resource_bounds(self):
        buf = bytearray(make_package())
        struct.pack_into("<I", buf, 0x54 + 12, 0xFC)
        with self.assertRaisesRegex(IndexFormatError, "outside"):
            probe_dbpf_v1(bytes(buf))


if __name__ == "__main__":
    unittest.main()
