#!/usr/bin/env python3
"""Offline inventory of apartment-related names in an authorized Sims 3 DS extraction.

No original assets are copied, modified, embedded, or uploaded. A match is a lead,
NOT evidence that an apartment interior was implemented or intended to be enterable.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

TERMS = (
    'strangetown', 'mesa flats', 'mesaflats', 'belladonna',
    'apartment', 'apartments', 'condo', 'condos', 'interior',
)


def scan(root: Path, max_bytes: int = 16 * 1024 * 1024) -> dict:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('The input must be a directory containing an authorized extraction')
    found = []
    scanned = skipped = 0
    for parent, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(parent) / d).is_symlink())
        for filename in sorted(files):
            path = Path(parent) / filename
            if path.is_symlink():
                skipped += 1
                continue
            rel = path.relative_to(root).as_posix()
            try:
                size = path.stat().st_size
                if size > max_bytes:
                    skipped += 1
                    continue
                raw = path.read_bytes()
            except (OSError, PermissionError):
                skipped += 1
                continue
            scanned += 1
            matched = {}
            low_path = rel.casefold()
            for term in TERMS:
                locations = []
                if term in low_path:
                    locations.append({'source': 'filename'})
                ascii_term = term.encode('ascii')
                utf16_term = term.encode('utf-16le')
                for encoding, haystack, needle in (
                    ('ascii', raw.lower(), ascii_term),
                    ('utf16le', raw.lower(), utf16_term),
                ):
                    start = 0
                    while len(locations) < 10:
                        pos = haystack.find(needle, start)
                        if pos < 0:
                            break
                        locations.append({'source': encoding, 'offset': pos})
                        start = pos + len(needle)
                if locations:
                    matched[term] = locations
            if matched:
                found.append({
                    'path': rel, 'size': size,
                    'sha256': hashlib.sha256(raw).hexdigest(),
                    'matches': matched,
                })
    return {
        'schema': 1,
        'warning': 'String hits are leads only; not confirmation of cut content or enterable interiors.',
        'scanned_files': scanned, 'skipped_files': skipped,
        'findings': found,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('extraction', type=Path, help='Privately extracted authorized DS game data')
    parser.add_argument('--output', type=Path, help='Write only metadata as JSON (keep private)')
    parser.add_argument('--max-file-mib', type=int, default=16)
    args = parser.parse_args()
    if args.max_file_mib < 1:
        parser.error('--max-file-mib must be >= 1')
    result = scan(args.extraction, args.max_file_mib * 1024 * 1024)
    data = json.dumps(result, indent=2, ensure_ascii=True) + '\n'
    if args.output:
        args.output.write_text(data, encoding='utf-8')
    else:
        print(data, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
