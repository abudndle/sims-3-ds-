"""Read-only source-ROM provenance check for the archived Sims 3 DS manifest.

The archived NitroFS manifest was measured on an NTR-VS3E revision (b39...),
while touchscreen hook audits use a different DSi-enhanced revision (d42...).
A matching file name is not enough to transfer offsets or hook addresses.
This tool neither extracts proprietary files nor writes to a ROM.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path

MANIFEST_ROM_SHA = "b39ba54eb61f0bc05094a362e297f963bf5a08fc05c4cd0f3dbc8dfe45abd6de"
ARM9_HOOK_ROM_SHA = "d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a"
FIELDS = ("file_id", "path", "offset", "size", "sha256")
MAX_ROWS = 8192
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(ValueError):
    """Untrusted manifest or incompatible input revision."""


def parse_manifest(source):
    if not isinstance(source, str) or len(source) > 2_000_000:
        raise ManifestError("invalid manifest text")
    reader = csv.DictReader(io.StringIO(source))
    if reader.fieldnames != list(FIELDS):
        raise ManifestError("manifest column mismatch")
    rows = []
    paths = set()
    ids = set()
    for entry in reader:
        if len(rows) >= MAX_ROWS:
            raise ManifestError("too many manifest entries")
        if None in entry or any(value is None for value in entry.values()):
            raise ManifestError("malformed manifest entry")
        try:
            file_id = int(entry["file_id"])
            offset = int(entry["offset"])
            size = int(entry["size"])
        except ValueError as exc:
            raise ManifestError("noninteger manifest field") from exc
        path = entry["path"]
        digest = entry["sha256"]
        if (file_id < 0 or offset < 0 or size < 0 or
                not path or path.startswith("/") or "\\" in path or
                ".." in path.split("/") or digest != digest.lower() or
                not SHA_PATTERN.fullmatch(digest)):
            raise ManifestError("invalid manifest record")
        if path in paths or file_id in ids:
            raise ManifestError("duplicate manifest path or id")
        paths.add(path)
        ids.add(file_id)
        rows.append({"file_id": file_id, "path": path, "offset": offset,
                     "size": size, "sha256": digest})
    if not rows:
        raise ManifestError("empty manifest")
    if ids != set(range(len(rows))):
        raise ManifestError("manifest file ids are not contiguous")
    bounds = sorted((row["offset"], row["offset"] + row["size"]) for row in rows)
    if any(right[0] < left[1] for left, right in zip(bounds, bounds[1:])):
        raise ManifestError("overlapping manifest ranges")
    return rows


def audit(rom, manifest_text, expected_sha=MANIFEST_ROM_SHA):
    """Check whole-ROM provenance before verifying archived file digests."""
    if not isinstance(rom, bytes):
        raise ManifestError("ROM must be bytes")
    if not SHA_PATTERN.fullmatch(expected_sha):
        raise ManifestError("invalid expected revision")
    sha = hashlib.sha256(rom).hexdigest()
    if sha != expected_sha:
        raise ManifestError(
            "ROM revision does not match archive provenance; do not reuse "
            "file offsets or apply cross-revision ARM9 hooks"
        )
    rows = parse_manifest(manifest_text)
    wrong = []
    for row in rows:
        end = row["offset"] + row["size"]
        if end > len(rom):
            raise ManifestError("manifest file range outside ROM")
        actual = hashlib.sha256(rom[row["offset"]:end]).hexdigest()
        if actual != row["sha256"]:
            wrong.append(row["file_id"])
    if wrong:
        raise ManifestError("manifest content hash mismatch for file IDs: " +
                            ",".join(map(str, wrong[:8])))
    targets = [r for r in rows if r["path"].lower().startswith("data/backend/")
               and r["path"].lower().endswith(".package")]
    return {
        "rom_sha256": sha,
        "archived_revision_verified": sha == MANIFEST_ROM_SHA,
        "matches_arm9_hook_revision": sha == ARM9_HOOK_ROM_SHA,
        "validated_file_records": len(rows),
        "validated_backend_package_records": len(targets),
        "package_metadata": [
            {"path": r["path"], "file_id": r["file_id"],
             "size": r["size"], "sha256": r["sha256"]}
            for r in targets
        ],
        "native_package_index_verified": False,
        "pet_actor_hook_verified": False,
        "patch_ready": False,
        "limitations": [
            "Manifest file hashes verify archived file identity, not internal resource indexes.",
            "NTR-VS3E archived offsets must not be reused in the DSi-enhanced ARM9 revision.",
            "No proprietary payloads, real pet models, or native integration hooks are exported.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.dumps(audit(args.rom.read_bytes(),
                              args.manifest.read_text(encoding="utf-8")), indent=2) + "\n"
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
