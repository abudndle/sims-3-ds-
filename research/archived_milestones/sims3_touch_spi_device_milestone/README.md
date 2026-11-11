# Sims 3 DS — ARM7 touchscreen SPI device selection milestone

## Verified on the original VS3E ROM

The read-only analyzer finds **two ARM7 SPI setup sequences** selecting device **2 (touchscreen)** with the enabled SPI control word `0x8202`.

| SPI control register loaded | `0x8202` loaded | `STRH` to SPICNT |
|---|---|---|
| `0x0238C9DC` | `0x0238C9F0` | `0x0238C9F8` |
| `0x0238CA58` | `0x0238CA68` | `0x0238CA70` |

The actual halfword-write opcode is `0xE1C540B0` at both write sites. The first routine additionally masks the input command to eight bits before writing SPI data; the second similarly prepares and transmits a command byte. The static pattern is consistent with touchscreen SPI transfer setup, but does **not** demonstrate X/Y coordinate decoding, task UI dispatch, or runtime control flow.

## Reproduce

```
python -m unittest -v test_trace_touch_spi.py
python trace_touch_spi.py '/path/to/Sims 3 DS USA VS3E.nds' --output results
```

No copyrighted ROM data is included in this package. It uses the user's own ROM when supplied. ROM unchanged; no modified ROM or emulator screenshot was produced by this milestone.

## Next milestone

Trace callers and the command bytes passed to the touchscreen SPI routine, then identify coordinate processing and shared-memory transfer to ARM9. Confirm with debugger/emulator traces before changing the original game's input or UI.
