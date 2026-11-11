# Sims 3 DS — ARM9 input reference milestone

## Verified against supplied working ROM

- Source: `Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds` (user-provided; not distributed).
- ROM SHA-256: `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`.
- ARM9 base: `0x02004800`.
- Static ARM-state PC-relative literal-load scan located **13 instruction candidates** for input/IPC registers:
  - `KEYINPUT` at `0x021BE9D8` (one).
  - `EXTKEYIN` at `0x021BF220` and `0x021C4DA8` (two).
  - `IPCSYNC`: four references.
  - `IPCFIFOCNT`: six references.
- **Do not treat these as verified game input dispatch hooks**. They may be initialization, library, dead, or data-like sequences. No ARM7 touch-message tracing has been completed.

## Reproduce

```sh
python3 -m unittest -v test_scan.py
python3 scan_input.py '/path/to/owned/rom.nds' --output input_references.json
```

Reports include hexadecimal ARM9 addresses, ROM offsets, encoded opcodes, literal address, destination register, and neighboring words. No ROM changes are made.

## Next milestone for actual DS mod

1. Disassemble around `0x021BE9D8` and investigate its callers; identify existing key processing and polling cadence.
2. Trace the ARM7->ARM9 IPC/touch path; locate the current bottom-screen Sims-panel event handler and original sprite reference.
3. Verify on hardware/emulator with a reversible hook before inserting new UI state handling.
4. Only then test a gameplay patch in melonDS. The full top-screen 3D/bottom-screen UI conversion remains unimplemented.

This artifact contains no copyrighted game binaries or original assets.
