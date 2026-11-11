# The Sims 3 DS — display-routing ARM9 reconnaissance

## Verified milestone
Read-only scan of the original **VS3E** USA Nintendo DS ROM for Nintendo DS display-engine hardware-register constants and plausible ARM-state PC-relative LDR references to those constants.

- **25** ARM-state literal-load-pattern matches into the selected display register constants.
- **4** matches referencing `POWCNT1` (`0x04000304`)—the DS power/LCD engine routing register.
- **10** matches referencing the sub-engine display control register (`0x04001000`).
- **11** matches referencing VRAM bank A control (`0x04000240`).

Candidate ARM instruction address `0x020CDA48` loads a constant (`0x04000304`) via a literal at `0x020CDBA8`. This is a **possible display initialization/control lead**, NOT a confirmed screen-switch routine. Other relevant references are in `display_report.json` and `display_report.csv`.

## Run
`python3 scan_display.py '/path/to/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds' -o display_report.json`

`python3 -m unittest -v test_scan_display.py`

## Limitations and next work
The scanner does not implement a full ARM/Thumb disassembler, classify function boundaries, or demonstrate register writes and reachable execution paths. Some matches may be data accidentally resembling ARM instructions. The original DS main/sub 2D engines, 3D engine, VRAM banks, OAM, capture and touch coordinate system all need coordinated handling to put only the world on the upper screen and the full HUD on the lower screen. Swapping a single screen-routing bit is **not sufficient** and may black-screen or misplace the UI.

**No ROM has been modified** in this milestone. No faster camera, cursor, or UI screen swap is installed. The working household gameplay milestone remains the baseline for subsequent melonDS tests.

Game binary and asset files are not included in this package.
