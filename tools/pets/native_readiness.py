"""Read-only native integration readiness audit for user-owned The Sims 3 DS ROM.

No patch bytes, offsets for insertion, pet actor locations or executable hook
are invented. Counts and confidence boundaries only; never exports ROM assets.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from tools.arm9_event_boundary.analyze import SHA, inspect as inspect_touch


def _region(rom, offset_at, size_at, label, alignment=4):
    offset, size = (struct.unpack_from("<I", rom, pos)[0]
                    for pos in (offset_at, size_at))
    if size == 0:
        if offset:
            raise ValueError(f"{label}: nonzero offset for empty region")
        return {"present": False, "size": 0}
    if offset < 0x200 or offset % alignment or size > len(rom) - offset:
        raise ValueError(f"{label}: invalid ROM bounds or alignment")
    return {"present": True, "size": size}


def inspect(rom, verify_sha=True):
    """Check original ROM identity, read-only ARM9 touch anchors and tables.

    With verify_sha=False the result is test-only; NEVER indicates a known
    retail revision or a safe patch location.
    """
    if not isinstance(rom, bytes) or len(rom) < 0x200:
        raise ValueError("truncated NDS ROM")
    digest = hashlib.sha256(rom).hexdigest()
    if verify_sha and digest != SHA:
        raise ValueError("unsupported game ROM SHA-256")
    # Headers store the ARM9 binary at 0x20, main-memory load address at 0x28
    # and length at 0x2c. The touch audit independently validates this region.
    touch = inspect_touch(rom, check_sha=verify_sha)
    arm9 = _region(rom, 0x20, 0x2c, "ARM9")
    arm7 = _region(rom, 0x30, 0x3c, "ARM7")
    overlays9 = _region(rom, 0x50, 0x54, "ARM9 overlays")
    overlays7 = _region(rom, 0x58, 0x5c, "ARM7 overlays")
    fnt = _region(rom, 0x40, 0x44, "NitroFS FNT")
    fat = _region(rom, 0x48, 0x4c, "NitroFS FAT")
    for label, region in (("ARM9 overlays", overlays9), ("ARM7 overlays", overlays7)):
        if region["size"] % 32:
            raise ValueError(f"{label}: table size not divisible by 32")
    if fat["size"] % 8:
        raise ValueError("NitroFS FAT: table size not divisible by 8")
    return {
        "revision_sha256": digest,
        "known_original_revision": digest == SHA,
        "arm9_bytes": arm9["size"],
        "arm7_bytes": arm7["size"],
        "arm9_overlay_records": overlays9["size"] // 32,
        "arm7_overlay_records": overlays7["size"] // 32,
        "nitrofs_fat_records": fat["size"] // 8,
        "nitrofs_fnt_present": fnt["present"],
        "touch_boundary_anchors_verified": touch["verified_anchors"],
        "verified_callback_call": touch["callback_call"],
        "pets_actor_hook_verified": False,
        "pets_renderer_hook_verified": False,
        "pets_save_hook_verified": False,
        "patch_ready": False,
        "required_next_evidence": [
            "Locate and runtime-trace an original actor creation/destruction path.",
            "Identify unused safe actor slots and DS geometry/animation budgets.",
            "Locate the verified gameplay event callback target and map modes.",
            "Verify an isolated persistence mechanism and emulator regressions.",
        ],
        "disclaimer": "Read-only static inventory; no pet actors, hooks, rendering or playable ROM established.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="User-owned unmodified original .nds")
    parser.add_argument("--output", type=Path, help="Write metadata-only JSON report")
    args = parser.parse_args()
    result = inspect(args.rom.read_bytes())
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
