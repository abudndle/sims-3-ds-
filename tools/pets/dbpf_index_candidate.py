"""Conservative DBPF v1-style index *candidate* validator.

This is deliberately NOT a confirmed Sims 3 DS .package decoder. It only
accepts the well-defined 20-byte (type, group, instance, offset, size) test
profile if its entire index is structurally coherent. It returns no payload
bytes and does not interpret object/model resource types.
"""
import struct

INDEX_RECORD_SIZE = 20
MAX_RECORDS = 100000
HEADER_SIZE = 0x40


class IndexFormatError(ValueError):
    """Candidate package cannot be decoded safely under this profile."""


def _read32(data, offset):
    if offset + 4 > len(data):
        raise IndexFormatError("truncated index header")
    return struct.unpack_from("<I", data, offset)[0]


def probe_dbpf_v1(data):
    """Parse only a strict DBPF-style version-1, fixed-20-byte test profile.

    The original game's format, index version and resource identity remain
    unverified unless actual private-package evidence independently confirms
    this same profile. Never treat this output as a usable ROM patch plan.
    """
    if not isinstance(data, bytes) or len(data) < HEADER_SIZE:
        raise IndexFormatError("truncated package header")
    if data[:4] != b"DBPF":
        raise IndexFormatError("not a DBPF signature")
    major = _read32(data, 4)
    minor = _read32(data, 8)
    index_major = _read32(data, 0x20)
    count = _read32(data, 0x24)
    index_offset = _read32(data, 0x28)
    index_size = _read32(data, 0x2C)
    if (major, minor, index_major) != (1, 0, 7):
        raise IndexFormatError("unsupported DBPF version/index profile")
    if count > MAX_RECORDS:
        raise IndexFormatError("resource count exceeds safety cap")
    if index_size != count * INDEX_RECORD_SIZE:
        raise IndexFormatError("index size does not match 20-byte record profile")
    if index_offset < HEADER_SIZE or index_offset > len(data) or index_size > len(data) - index_offset:
        raise IndexFormatError("index outside package")
    if count == 0:
        return {"candidate_profile": "DBPF-v1-index7-fixed20",
                "index_entry_count": 0, "resource_types": [],
                "validated": True, "ds_format_confirmed": False}
    index_end = index_offset + index_size
    types = set()
    keys = set()
    ranges = []
    for i in range(count):
        position = index_offset + i * INDEX_RECORD_SIZE
        typ, group, instance, start, size = struct.unpack_from("<IIIII", data, position)
        if not size or start < HEADER_SIZE or start > len(data) or size > len(data) - start:
            raise IndexFormatError("resource payload outside package")
        if start < index_end and start + size > index_offset:
            raise IndexFormatError("resource overlaps index")
        key = (typ, group, instance)
        if key in keys:
            raise IndexFormatError("duplicate type/group/instance")
        keys.add(key)
        types.add(typ)
        ranges.append((start, start + size))
    ranges.sort()
    if any(right[0] < left[1] for left, right in zip(ranges, ranges[1:])):
        raise IndexFormatError("overlapping resources")
    return {
        "candidate_profile": "DBPF-v1-index7-fixed20",
        "index_entry_count": count,
        "resource_types": [f"0x{t:08X}" for t in sorted(types)],
        "validated": True,
        "ds_format_confirmed": False,
    }
