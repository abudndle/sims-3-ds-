# Apartment audit — private, offline runbook

This is a **read-only investigation**, not a ROM patch or proof of unused apartment interiors. See [cut-content evidence](cut-content-evidence.md) and [issue #4](https://github.com/abudndle/sims-3-ds-/issues/4).

## Preconditions
- Use an authorized, personally obtained **Nintendo DS** game dump (do not confuse it with the PC or 3DS versions).
- Extract the game data **outside the public Git checkout** in a private workspace. Never check in original assets or full scan reports. Do not upload ROMs or source assets to public GitHub Actions.
- Record the game region and SHA-256 privately so debug-menu behavior is not confused between European and North American releases.

## Run

```sh
python3 -m unittest discover -s tests -p 'test_audit_ds_apartments.py' -v
python3 tools/audit_ds_apartments.py /private/path/to/extracted-data \
    --output /private/path/to/apartment-audit.json
```

The resulting JSON lists matched filenames, sizes, SHA-256 hashes, and byte offsets for ASCII and UTF-16LE string matches, never the matching asset bytes. It skips symbolic links and files over 16 MiB by default (override with `--max-file-mib`). **Keep the JSON private** until its filenames and metadata have been reviewed.

The scanner matches the strings `Strangetown`, `Mesa Flats`, `Belladonna`, `apartment`, `condo`, and `interior` (including spelling variations). It may miss non-text numeric lot references, compressed assets, unusual encodings, or strings in big skipped files. False positives are expected.

## Interpret findings

1. Match in a name string or filename: **location mentioned**, not an enterable room.
2. Referenced interior asset in an otherwise used lot loading table: **candidate**; confirm layout, geometry and loader compatibility.
3. Valid apartment lot ID in the European debug menu: **candidate**; prove what loads and whether interaction/save/return works.
4. Functional interior in a patched build, reproducibly booted in melonDS: only then mark **restored**.

Do not run destructive debug commands against your main save. Use a clean copied save. The documented European debug menu has crash-prone commands.

## Next milestone acceptance
- Private ROM revision/hash identified.
- Scanner report inspected without leaking original bytes.
- Apartment lot/door/loader references cross-checked with at least one working enterable lot.
- European debug menu destinations recorded in melonDS when a valid European ROM is available.
- Written conclusion: native interior found / no native interior found / still unresolved.
