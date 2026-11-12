"""Verify a user-extracted Sims 3 DS package against an archived file digest.

Accepts an individual .package and the public manifest: a full original ROM
is not required. Strictly compares exact bytes/size/hash, then probes the
header and conservative candidate index WITHOUT exporting game data.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .dbpf_index_candidate import probe_dbpf_v1, IndexFormatError
from .manifest_provenance import parse_manifest, ManifestError, MANIFEST_ROM_SHA

MAX_PACKAGE_BYTES = 64 * 1024 * 1024


def verify_package(data, manifest_text, package_path):
    if not isinstance(data, bytes) or len(data) > MAX_PACKAGE_BYTES:
        raise ManifestError("invalid or oversized package")
    if not isinstance(package_path, str) or not package_path.lower().endswith(".package"):
        raise ManifestError("expected a NitroFS .package path")
    rows = parse_manifest(manifest_text)
    record = next((r for r in rows if r["path"] == package_path), None)
    if record is None:
        raise ManifestError("package not found in archived manifest")
    if len(data) != record["size"]:
        raise ManifestError("package size mismatch")
    digest = hashlib.sha256(data).hexdigest()
    if digest != record["sha256"]:
        raise ManifestError("package SHA-256 mismatch")
    header = data[:4]
    candidate = None
    if header == b"DBPF":
        try:
            candidate = probe_dbpf_v1(data)
        except IndexFormatError:
            pass
    return {
        "original_manifest_revision_sha256": MANIFEST_ROM_SHA,
        "package_path": package_path,
        "package_size": len(data),
        "package_sha256": digest,
        "exact_archived_package_verified": True,
        "header_signature_hex": header.hex(),
        "candidate_index_profile": candidate,
        "native_ds_resource_format_verified": False,
        "pet_models_verified": False,
        "patch_ready": False,
        "limitations": [
            "Exact archived file identity is verified, not the runtime's parser.",
            "The archive belongs to one DS revision; hooks for another revision remain separate.",
            "No extracted proprietary bytes are included in the output.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Locally extracted original package")
    parser.add_argument("manifest", type=Path, help="Archived public file_manifest.csv")
    parser.add_argument("--rom-path", required=True, help="Original NitroFS path, e.g. DATA/BACKEND/Animations.package")
    parser.add_argument("--output", type=Path, help="Optional metadata-only report")
    args = parser.parse_args()
    if args.package.stat().st_size > MAX_PACKAGE_BYTES:
        parser.error("package size exceeds safety limit")
    result = verify_package(args.package.read_bytes(), args.manifest.read_text(encoding="utf-8"), args.rom_path)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
