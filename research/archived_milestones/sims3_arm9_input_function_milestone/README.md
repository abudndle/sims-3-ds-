# The Sims 3 DS — ARM9 low-level input snapshot milestone

This toolkit contains a reproducible read-only analysis of the user-provided USA VS3E (NDSi enhanced) ROM. It does **not** contain ROM binaries, copyrighted game data, or an executable patch.

## Findings

- A plausible ARM-state input sampling routine spans `0x021BE974`–`0x021BEA24` (exclusive), 176 bytes / 44 aligned words.
- `0x021BE9D8`: `LDR r2,[pc,#0x50]` loads literal `0x021BEA30`.
- The literal value is `0x04000130`, the DS `KEYINPUT` register.
- `0x021BEA04`: `LDRH r2,[r2]` dereferences the `KEYINPUT` register address previously loaded into `r2` at `0x021BE9D8`. This is a candidate hardware button-state read, not a touch-coordinate read.
- The routine stores multiple input/status fields into a caller-provided structure (via `r5`), consistent with collection of a hardware input snapshot. This is a static inference, not a runtime trace.
- No direct ARM BL call to its entry was found in the scanned primary ARM9 binary. Callers might use a function pointer, overlays, or other instruction modes; this remains unknown.

## How to reproduce

`python analyze_input_function.py '/path/to/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds' --output input_function.json`

`python -m unittest -v test_input_function.py`

The analyzer validates six hard-coded instruction signatures to reject incompatible revisions. It reads the ROM without writing it. `input_function.json` contains addresses, opcodes, and SHA-256 hashes but **no extracted code binaries**.

## What is not established

- Which game loop calls the routine, and whether any direct code path handles the Sims icon.
- ARM7 touch-panel IPC structures and the coordinate dispatcher.
- Safe hook/injection locations, or any patched screen UI.
- Successful runtime invocation in melonDS.

## Next engineering task

Trace references to the routine through ARM/Thumb functions, overlays and function-pointer tables, and inspect the ARM7 touch IPC pipeline. Only then attempt a reversible patch and boot it with the existing melonDS test harness.
