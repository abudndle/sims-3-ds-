"""Read-only NitroFS package metadata inventory for Sims 3 DS Pets research.

No files are extracted or patched. The FNT/FAT tables are parsed from a user-
supplied ROM and only path/size metadata for research targets is reported.
The native pet actor/model format is still unknown.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from tools.arm9_event_boundary.analyze import SHA

TARGETS = {
    "animations.package": "animation resource index",
    "generalinteractions.package": "general interaction resource index",
    "objectinteractions.package": "object interaction resource index",
    "accessories.package": "object/accessory resource index",
    "furniture.package": "object meshes and placements",
    "lots.package": "lot/world resource index",
}
MAX_DIRECTORIES = 4096
MAX_ENTRIES = 8192


def u16(buf, offset):
    if offset < 0 or offset + 2 > len(buf):
        raise ValueError("truncated NitroFS table")
    return struct.unpack_from("<H", buf, offset)[0]


def u32(buf, offset):
    if offset < 0 or offset + 4 > len(buf):
        raise ValueError("truncated NitroFS table")
    return struct.unpack_from("<I", buf, offset)[0]


def parse_tables(fnt, fat, rom_length):
    """Decode NitroFS directory names and file byte ranges, without payloads."""
    if len(fnt) < 8 or len(fat) % 8 or not 0 < len(fat) // 8 <= MAX_ENTRIES:
        raise ValueError("invalid NitroFS directory/FAT table")
    count = u16(fnt, 6)
    if count < 1 or count > MAX_DIRECTORIES or count * 8 > len(fnt):
        raise ValueError("invalid NitroFS directory count")
    file_count = len(fat) // 8
    directories = {}
    used = set()
    active = set()
    seen_file_ids = set()

    def visit(index, prefix):
        if index >= count or index in active or index in used:
            raise ValueError("cyclic or duplicated NitroFS directory")
        active.add(index)
        offset, file_id = u32(fnt, index * 8), u16(fnt, index * 8 + 4)
        if offset < count * 8 or offset >= len(fnt):
            raise ValueError("NitroFS directory listing outside FNT")
        pos = offset
        while True:
            if pos >= len(fnt):
                raise ValueError("unterminated NitroFS directory listing")
            length_flag = fnt[pos]
            pos += 1
            if length_flag == 0:
                break
            name_len = length_flag & 0x7f
            if not name_len or pos + name_len > len(fnt):
                raise ValueError("invalid NitroFS entry name")
            raw_name = fnt[pos:pos + name_len]
            pos += name_len
            try:
                name = raw_name.decode("ascii")
            except UnicodeDecodeError as exc:
                raise ValueError("non-ASCII NitroFS path") from exc
            if name in {".", ".."} or "/" in name or "\\" in name:
                raise ValueError("unsafe NitroFS entry name")
            path = prefix + name
            if length_flag & 0x80:
                subdir = u16(fnt, pos)
                pos += 2
                if subdir < 0xF000 or subdir - 0xF000 >= count:
                    raise ValueError("invalid NitroFS subdirectory id")
                visit(subdir - 0xF000, path + "/")
            else:
                if file_id >= file_count or file_id in seen_file_ids:
                    raise ValueError("invalid or duplicate NitroFS file id")
                start, end = u32(fat, file_id * 8), u32(fat, file_id * 8 + 4)
                if start > end or end > rom_length:
                    raise ValueError("invalid NitroFS file bounds")
                directories[path] = {"file_id": file_id, "size": end - start}
                seen_file_ids.add(file_id)
                file_id += 1
        active.remove(index)
        used.add(index)

    visit(0, "")
    if len(used) != count:
        raise ValueError("unreachable NitroFS directory")
    if len(seen_file_ids) != file_count:
        raise ValueError("unreferenced NitroFS FAT records")
    return directories


def inspect(rom, verify_sha=True):
    if not isinstance(rom, bytes) or len(rom) < 0x200:
        raise ValueError("truncated NDS ROM")
    digest = hashlib.sha256(rom).hexdigest()
    if verify_sha and digest != SHA:
        raise ValueError("unsupported original DS ROM revision")
    def region(offset_at, length_at):
        offset, size = u32(rom, offset_at), u32(rom, length_at)
        if not size or offset < 0x200 or offset % 4 or size > len(rom) - offset:
            raise ValueError("invalid NitroFS table region")
        return rom[offset:offset + size]
    entries = parse_tables(region(0x40, 0x44), region(0x48, 0x4c), len(rom))
    matched = []
    for path, meta in sorted(entries.items()):
        if path.lower().startswith("data/backend/") and path.split("/")[-1].lower() in TARGETS:
            matched.append({
                "path": path,
                "file_id": meta["file_id"],
                "size": meta["size"],
                "research_purpose": TARGETS[path.split("/")[-1].lower()],
                "format_verified": False,
                "pet_assets_confirmed": False,
            })
    return {
        "rom_sha256": digest,
        "known_original_revision": digest == SHA,
        "nitrofs_file_count": len(entries),
        "candidate_packages": matched,
        "missing_target_packages": sorted(set(TARGETS) - {p["path"].split("/")[-1].lower() for p in matched}),
        "pet_actor_hook_verified": False,
        "pets_model_identified": False,
        "patch_ready": False,
        "limitation": "Names and sizes only; no package decoding or runtime pet actor integration.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.dumps(inspect(args.rom.read_bytes()), indent=2) + "\n"
    if args.output:
        args.output.write_text(report)
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
