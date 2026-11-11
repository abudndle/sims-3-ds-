# The Sims 3 DS — DSM1 cross-reference milestone

This is a **read-only** resource inventory built from a user-provided `VS3E` game dump. The original ROM was not modified.

## Verified output

- All 26 `.package` file bounds and SHA-256 hashes validated against the prior NitroFS manifest.
- Six `DSM1` packages share a version-like field `03010101` (bytes at 0x04–0x07) and marker `0x2a2b1b11` (little-endian u32 at 0x0c).
- The u32 fields at offsets 0x10, 0x14 and 0x18 are equal within each of the six packages. **Their semantics are unknown.**
- 575 unique `.dst` strings, 4,318 occurrences; 11 names occur in multiple DSM1 packages.
- 28 names have a literal occurrence in the ARM9 executable (not evidence of execution/use).
- Two names (`gym.dst`, `police.dst`) occur in an *additional* `.package` outside their own DSM1 set.
- 30 names have matching standalone NitroFS basenames. Most references are likely embedded data, not missing files.

## Files

`resource_crossreferences.csv` gives per-name textual cross-references and the first within-package string offset.

`dsm1_header_observations.csv` records verified raw header fields. The field names intentionally do not claim decoded meanings.

`summary.json` has validated totals. `resource_crossrefs.py` regenerates these reports from the unmodified user ROM and original file manifest.

Run:

```bash
python3 resource_crossrefs.py '/path/to/Sims3.nds' file_manifest.csv --out results
```

## Next milestone

Decode record boundaries and object indices, link object IDs to catalog/unlock tables, then isolate a reproducible test case and make a reversible patch. Do not infer cut content merely from names or lack of literal references: code may refer to IDs, hashes or compressed resources.

No ROM or copyrighted game payloads are included in this report.
