# The Sims 3 DS — ROM extraction and cut-content triage

## Verified setup

- Input ROM: USA VS3E, 134,217,728 bytes; SHA-256 `b39ba54eb61f0bc05094a362e297f963bf5a08fc05c4cd0f3dbc8dfe45abd6de`.
- NDSFactory v1.3.3 Linux executable unpacked successfully (387,624 bytes).
- NDSFactory did not launch: this environment lacks Qt 6.4+; the available melonDS-bundled Qt does not supply the `Qt_6.4` symbol version.
- Independently extracted original ARM9, ARM7, FNT, FAT, overlay table, and NitroFS without changing the input ROM.
- NitroFS/FAT inventory: 983 entries; index at `file_manifest.csv`.

## Initial assets worth investigating

| Package | ROM file bytes | Why investigate |
|---|---:|---|
| `DATA/BACKEND/Accessories.package` | 4,199,199 | Potential unused gameplay data and/or assets |
| `DATA/BACKEND/Animations.package` | 20,517,654 | Potential unused gameplay data and/or assets |
| `DATA/BACKEND/Furniture.package` | 15,355,400 | Potential unused gameplay data and/or assets |
| `DATA/BACKEND/Lots.package` | 1,126,573 | Potential unused gameplay data and/or assets |
| `DATA/BACKEND/GeneralInteractions.package` | 76,388 | Potential unused gameplay data and/or assets |
| `DATA/BACKEND/ObjectInteractions.package` | 277,648 | Potential unused gameplay data and/or assets |
| `DATA/BACKEND/Opportunities.package` | 46,728 | Potential unused gameplay data and/or assets |
| `DATA/BACKEND/LifetimeRewards.package` | 128,732 | Potential unused gameplay data and/or assets |
| `DATA/BACKEND/Tutorial.package` | 874,698 | Potential unused gameplay data and/or assets |
| `DATA/BACKEND/Vehicles.package` | 668,481 | Potential unused gameplay data and/or assets |
| `DATA/CAS/CASClothes.package` | 18,623,479 | CAS customization possibilities |
| `DATA/CAS/CASHair.package` | 8,545,434 | CAS customization possibilities |

## Important limitations

These filenames demonstrate asset presence only. No asset is confirmed cut or unused yet. Confirm by parsing internal package directories and correlating resource identifiers with code and live gameplay references.
NDSFactory is a ROM unpacker/repacker, not a source-code decompiler. The original .nds and proprietary extracted data are not included in this report archive.

## Next technical milestone

1. Decode internal `.package` directory/index formats and enumerate resource IDs.
2. Cross-reference code references, menu tables, and UI resources to detect orphaned assets.
3. Classify each candidate as verified unused, inaccessible but referenced, or unconfirmed.
4. Implement a minimal reversible patch only after a specific candidate is validated; test on melonDS.
