# Sims 3 DS — ARM7 card-bus vs touchscreen-SPI classification milestone

## What changed

A fresh ARM7 instruction trace ruled out a plausible but incorrect touch-ADC command lead. The code at `0x0238FA50` loads `0xB8` as a command, and at `0x0238FA5C` may conditionally switch to `0x90`. At `0x0238FA6C`, it calls `0x0238F978`.

The target routine loads the following hardware-register addresses from its PC-relative literal pool:

| Instruction | Loaded address | Meaning |
|---|---|---|
| `0x0238F97C` | `0x040001A4` | Game-card bus control |
| `0x0238F998` | `0x040001A0` | Game-card bus command/data region |

These are *not* the DS touchscreen SPI registers `0x040001C0` and `0x040001C2`. The numeric `0x90` alone does not identify a touchscreen ADC sample. Therefore this path is **not an appropriate hook for the requested touch UI**.

## Verification

- Against the user-supplied original USA `VS3E` ROM (MD5 `7cdf32d02eeeff592a0a4ab6bec7b5c1`).
- Checked candidate ARM instructions and the `BL` destination, then decoded the target routine's PC-relative address literals.
- Seven unit tests passed.
- No game ROM or copyrighted ROM binary is distributed here; original ROM unchanged.

## Reproduce

```bash
python3 -m unittest -v test_analyze.py
python3 analyze.py '/path/to/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds' --output results.json
```

## Next action

Instrument actual reads/writes to touchscreen SPI (`SPICNT` at `0x040001C0`, `SPIDATA` at `0x040001C2`) in an emulator debugger, collect the command bytes and sample results during a touch interaction, then correlate with ARM9 UI event handling. Avoid assuming command constants elsewhere are ADC commands without verifying the active SPI device.

## Mod integration status

This milestone is negative identification of an unsafe candidate. It **does not** install a touchscreen handler, move the 3D view to the top, or produce a modified playable ROM.
