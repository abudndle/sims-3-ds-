#!/usr/bin/env python3
"""Read-only reference indexing for Sims 3 DS DSM1 resources. Does not export assets."""
import argparse, csv, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

REF_RE = re.compile(rb'(?<![A-Za-z0-9_./-])[A-Za-z0-9_][A-Za-z0-9_./-]{1,94}\.dst(?![A-Za-z0-9_./-])', re.I)

def build(rom, manifest, output):
    records = list(csv.DictReader(manifest.open(newline='', encoding='utf-8')))
    output.mkdir(parents=True, exist_ok=True)
    nitro_names = {r['path'].split('/')[-1].lower() for r in records}
    refs = []
    summary = []
    with rom.open('rb') as fh:
        fh.seek(0, 2)
        rom_len = fh.tell()
        for r in records:
            if not r['path'].endswith('.package'):
                continue
            start, size = int(r['offset']), int(r['size'])
            if min(start, size) < 0 or start + size > rom_len:
                raise ValueError('Invalid ROM bounds: ' + r['path'])
            fh.seek(start)
            data = fh.read(size)
            if hashlib.sha256(data).hexdigest() != r['sha256']:
                raise ValueError('Hash mismatch: ' + r['path'])
            if data[:4] != b'DSM1':
                continue
            found = defaultdict(list)
            for match in REF_RE.finditer(data):
                # Require a zero terminator or structured delimiter: reduces accidental bytestring hits.
                end = match.end()
                if end < len(data) and data[end] not in (0, 1, 2, 3, 4, 8, 16, 32):
                    continue
                filename = match.group().decode('ascii')
                found[filename.lower()].append(match.start())
            for name, offsets in sorted(found.items()):
                refs.append({'package': r['path'], 'resource_reference': name,
                             'occurrences': len(offsets), 'first_offset_hex': hex(offsets[0]),
                             'standalone_nitrofs_basename': 'yes' if name.split('/')[-1] in nitro_names else 'no'})
            summary.append({'package':r['path'],'unique_dst_references':len(found),
                            'total_dst_references':sum(map(len,found.values()))})
    columns = ['package','resource_reference','occurrences','first_offset_hex','standalone_nitrofs_basename']
    with (output/'dsm1_references.csv').open('w',newline='',encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, columns);writer.writeheader();writer.writerows(refs)
    unique = {r['resource_reference'] for r in refs}
    result = {'validated_dsm1_packages':len(summary),'package_summaries':summary,
              'package_name_pairs':len(refs),'unique_dst_names_across_packages':len(unique),
              'total_textual_reference_occurrences':sum(x['occurrences'] for x in refs),
              'references_with_standalone_file':sum(x['standalone_nitrofs_basename']=='yes' for x in refs),
              'cut_content_confirmed':0,
              'caveat':'Strings referencing .dst resources are not evidence of cut content. Some references may point to packed internal resources rather than standalone NitroFS files; offsets are package-relative.'}
    (output/'reference_summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('rom',type=Path)
    p.add_argument('manifest',type=Path)
    p.add_argument('--out',type=Path,default=Path('reference_index'))
    a=p.parse_args()
    print(json.dumps(build(a.rom,a.manifest,a.out),indent=2))
