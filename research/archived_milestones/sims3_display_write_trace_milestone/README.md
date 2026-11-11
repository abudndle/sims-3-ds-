# The Sims 3 DS — Display-register write tracing milestone

## Verified results

Read-only ARM9 analysis of the uploaded, verified USA VS3E NDSi-enhanced ROM. The scanner identified **23 PC-relative display-register address load groups with 62 direct memory access instructions** (read/write candidates) in bounded, straight-line ARM-state scans.

These include the following high-confidence *syntactic* register access sequences:

- `0x020CDA48`: loads `POWCNT1` (`0x04000304`) address into r1; reads `LDRH` at `0x020CDA50`; writes `STRH` at `0x020CDA58`, `0x020CDA6C`, and `0x020CDA78`.
- `0x020D8A38`: also loads `POWCNT1` into r1; reads at `0x020D8A40`, writes at `0x020D8A48`.
- `0x020CDD20`: loads sub display control (`0x04001000`) into r2; reads word at `0x020CDD24` and writes at `0x020CDD30`.
- `0x020D00DC`: loads sub display control into r3; reads at `0x020D00E4`, writes at `0x020D00F0`.

## Why this matters

These instructions are plausible integration locations for determining *where* the game configures the display engines, which is necessary before moving the existing 3D scene and UI to the correct Nintendo DS LCDs. They are **not confirmed safe patch locations**. The scanner does not prove that any given code path runs during gameplay, identify the exact meaning of the bits changed, or locate the game's higher-level render and touchscreen callbacks.

## Reproduce

```bash
python3 trace_display_writes.py '/path/to/verified Sims 3 DS ROM.nds' -o display_writes.json
python3 -m unittest -v test_trace.py
```

Outputs: `display_writes.json` and `display_writes.csv`. The scanner does not modify the ROM. Tests cover ARM word and halfword access decoding and branch boundaries.

## Next engineering step

Use emulator tracing or debugging to establish which POWCNT1 and display-control writes execute during gameplay, decode the written register bit values, and identify frame rendering / overlay / input dispatch calls. Keep top LCD exclusively for the 3D world and its cursor, with the original UI and tutorial on the lower touch LCD. The bottom 3D Build/Buy view requires separate rendering/capture scheduling and must not be assumed possible from an LCD route swap.

**No gameplay patch or screen-conversion ROM has been built in this milestone.** The user's proprietary ROM files are excluded from this package.
