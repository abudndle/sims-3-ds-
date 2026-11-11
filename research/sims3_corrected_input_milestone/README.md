# Sims 3 DS — corrected ARM9 input mapping milestone

**ROM:** user-provided `Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds`; read only. This toolkit contains no game binaries or copyrighted assets.

## Critical correction

An earlier milestone misread the Nintendo DS header ARM9 fields as `(file_offset, load_base, size)` instead of `(file_offset, entry, load_address, size)`. The correct load address is `0x02004000`, entry address `0x02004800`, ARM9 binary size `0x17C6C0`, and image ends at `0x021806C0` (exclusive). Consequently, **the previously claimed ARM9 routine at `0x021BE974` is outside the actual ARM9 image**. That earlier routine identification and its alleged caller analysis must not be used as a patch location. Other prior address reports may also require review if produced by the same incorrect mapping assumption.

## Verified new leads

Two 32-bit, aligned `KEYINPUT` (`0x04000130`) literal words occur in the actual ARM9 image:

- `0x02095C4C`, referenced by the Thumb literal load `0x02095C1A` (`0x480C`)
- `0x020A1584`, referenced by the Thumb literal load `0x020A150E` (`0x481D`)

Three `IPCFIFOCNT` (`0x04000184`) literals and one `IPCSYNC` (`0x04000180`) literal were also found. See `report.json` for exact addresses, loads and SHA-256.

This is a **static register-literal analysis**, not proof that these routines handle normal gameplay, nor proof of touchscreen coordinates or the Sims UI dispatcher.

## Run

```sh
python -m unittest -v test_analyze.py
python analyze.py '/path/to/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds' --out report.json
```

## Next stage

Disassemble the Thumb functions around `0x02095C1A` and `0x020A150E`, trace callers and state structures; inspect IPC and ARM7 touch-coordinate decoding. Only attempt an emulator-tested ROM patch once a valid UI update hook and safe patch location have been identified.

No original ROM bytes were modified. No working control or screen conversion patch is supplied.
