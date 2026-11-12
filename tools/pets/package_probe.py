"""Read-only signature probe for Sims 3 DS NitroFS .package files.

It reports only sizes, hashes and four-byte signatures of independently
identified files. It does not parse undocumented resource tables and does
not extract, modify or distribute original package contents.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from tools.arm9_event_boundary.analyze import SHA
from tools.pets.asset_candidates import parse_tables, u32
from tools.pets.dbpf_index_candidate import IndexFormatError, probe_dbpf_v1

MAX_REPORT_PACKAGES = 256
SIGNATURES = {
    b"DBPF": "DBPF-like header candidate (resource index UNVERIFIED)",
    b"RIFX": "RIFX-like header candidate (resource index UNVERIFIED)",
}


def inspect(rom, verify_sha=True):
    if not isinstance(rom, bytes) or len(rom) < 0x200:
        raise ValueError("truncated NDS ROM")
    rom_sha = hashlib.sha256(rom).hexdigest()
    if verify_sha and rom_sha != SHA:
        raise ValueError("unsupported original DS ROM revision")

    def table(offset_field, size_field):
        start, length = u32(rom, offset_field), u32(rom, size_field)
        if not length or start < 0x200 or start % 4 or length > len(rom) - start:
            raise ValueError("invalid NitroFS metadata table bounds")
        return rom[start:start + length]

    fnt = table(0x40, 0x44)
    fat = table(0x48, 0x4c)
    entries = parse_tables(fnt, fat, len(rom))
    candidates = [(name, record) for name, record in entries.items()
                  if name.lower().startswith("data/") and name.lower().endswith(".package")]
    if len(candidates) > MAX_REPORT_PACKAGES:
        raise ValueError("too many packages to report")
    report = []
    for name, record in sorted(candidates):
        file_id = record["file_id"]
        start, end = struct.unpack_from("<II", fat, file_id * 8)
        # The NitroFS parser has already checked these bounds.
        header = rom[start:min(start + 4, end)]
        classification = SIGNATURES.get(header, "unknown or proprietary package format")
        # Any profile match is structural only; it is NOT proof of the DS
        # engine's package/resource format or pet model support.
        index_candidate = None
        if header == b"DBPF":
            try:
                index_candidate = probe_dbpf_v1(rom[start:end])
            except IndexFormatError:
                pass
        # No resource bytes, arbitrary strings, or original graphics are emitted.
        report.append({
            "path": name,
            "file_id": file_id,
            "size": end - start,
            "header_signature_hex": header.hex(),
            "signature_classification": classification,
            "resource_index_verified": False,
            "index_profile_candidate": index_candidate,
            "pet_assets_confirmed": False,
        })
    return {
        "original_sha256": rom_sha,
        "known_original_revision": rom_sha == SHA,
        "packages_examined": len(report),
        "packages": report,
        "package_index_decoder_verified": False,
        "pet_model_identified": False,
        "patch_ready": False,
        "limitations": [
            "Header recognition is NOT proof of the resource index format.",
            "No actor creation hook or DS rendering capability has been established.",
            "No game asset data is included in this report.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="User-owned original Sims 3 DS .nds")
    parser.add_argument("--output", type=Path, help="Optional metadata-only JSON output")
    args = parser.parse_args()
    report = json.dumps(inspect(args.rom.read_bytes()), indent=2) + "\n"
    if args.output:
        args.output.write_text(report)
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
