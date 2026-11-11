# Sims 3 DS: DSM1 resource-reference indexing milestone

## Verified results

- Six DSM1 package SHA-256 hashes were checked against the original ROM file manifest.
- 586 package/resource-name pairs, 575 distinct `.dst` reference names, 4,318 textual occurrences.
- 31 package/name pairs have a matching standalone NitroFS basename; other resources may be embedded within packages.
- This is an index of visible strings **not** a full DSM1 decoder, object extractor, or proof that resources are unused.
- No original copyrighted content, ROM or binary resources are included in this toolkit.

## Run

```bash
python3 build_reference_index.py /path/to/your/rom.nds /path/to/file_manifest.csv --out results
```

Both original ROM and existing `file_manifest.csv` are needed. The script validates all examined packages before processing; invalid hashes or offsets cause an error. Package-relative first offsets are in `dsm1_references.csv`.

## Restoration validation needed next

Decode DSM1 record tables and references, then cross-check the executable's resource-loading paths and game unlock/career/catalog metadata. Only mark cut content after determining that a concrete asset or feature is omitted from normal gameplay. Rebuild patches should be reversible and tested in melonDS.
