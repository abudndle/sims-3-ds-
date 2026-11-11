# Sims 3 DS: Resource format milestone

This milestone inventories the internal signature families of every `.package` file in the extracted USA `VS3E` ROM.

## Reproduce

```bash
python analyze_packages.py path/to/owned/game.nds file_manifest.csv --out metadata
```

Inputs must be taken from the **same ROM revision**. This script checks each package's SHA-256 from the supplied manifest before classification. It is read-only and does not emit game resources.

## Results

- 26 packages passed manifest hash and bounds validation.
- 6 `DSM1`, 7 `DST1`, 6 `BM*`, 1 `BML-08`, 1 `NPCS`, 2 CAS-style prefixes, and 3 unclassified.
- Signature identification is **not complete decoding** of any internal index.
- **No unused or cut assets have been confirmed**, and no patch has been applied.

## Technical next milestone

Determine the record/directory structure of `DSM1` and `DST1` using multiple samples. Enumerate asset identifiers, then cross-reference those identifiers against gameplay and menu references. Do not infer unused content from the presence of a resource package alone.
