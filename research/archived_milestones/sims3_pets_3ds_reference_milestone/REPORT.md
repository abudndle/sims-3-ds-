# The Sims 3: Pets (Nintendo 3DS) reference — milestone 1

## Verified inputs
- Decrypted CCI product code: **CTR-P-AS4E**.
- CCI size: **407,015,424 bytes**.
- NCCH/ExeFS and RomFS metadata parsed without modifying the image.
- **40 RomFS entries** across **4 directories**.
- Executable section `.code`: **2,154,468 bytes**.
- **136 selected string-reference occurrences** from 3DS data archives.

## Concrete reference targets
- `Binaries.arc`: `ZoomRotateCamera`, `Camera - Starting Angle by Lot ID`, and `Camera - Starting Zoom by Lot ID`.
- `Binaries.arc`: `cursor_terrain`, `cursor_tile`, and `cursor_wall`.
- `Datasets.arc`: `cursor_color` and `cursor_square_solid`.
- `Models.arc`: `BUILDMODE_CURSOR` (possible model identifier).
- `Flashes.arc`: `hud_buy_mode_btm`, `SetUpHUDLayout`, and `H2D_BuildModeBtnReleased` (possible interface symbols).
- `Shaders.arc`: `new_cursor_03_buildmode`.

These are strings observed in the original 3DS resource archives, not proof of code-function locations, complete reconstructed UI panels, or compatibility with DS hardware. The archive's internal formats require decoding before assets can be reused or behavior reconstructed.

## Application to the DS mod
1. Identify 3DS movement and camera parameters from archive records and executable routines.
2. Compare camera and cursor mechanics with user-supplied screenshots; recreate mechanics in the DS control source using original **DS** assets.
3. Investigate `hud_buy_mode_btm` as a 3DS reference for interface flow, not for directly copying 3DS assets into the DS game.
4. Integrate reworked code with verified ARM9/ARM7 DS routines and run on melonDS before claiming real gameplay.

## Current limitations
The delivered files are metadata, offsets, lexical candidate scans, and reproducible read-only tooling. No control patch has been injected into the original DS ROM, and no new DS gameplay screenshot has been captured. Both supplied 3DS ROM/CIA and DS ROM were left unchanged.
