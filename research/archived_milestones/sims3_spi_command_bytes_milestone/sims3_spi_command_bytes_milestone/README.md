# The Sims 3 DS — ARM7 SPI command-byte provenance milestone

This read-only analyzer checks the USA VS3E ROM (SHA-256 `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`) and validates 12 exact ARM7 direct calls to its SPI byte-transfer helpers.

## New finding

The read helper `0x0238CA54` applies `ORR r0, r0, #0x80` at `0x0238CA6C`. Its callers include these command-byte candidates:

| Call site | Kind | Effective byte | Confidence |
|---|---|---|---|
| `0x0238CCF0` | read | `0x80` | Fixed immediate `r0=0` |
| `0x0238CD34` | read | `0x82` | Inferred from dispatcher-local `r5=2` |
| `0x0238CD9C` | read | `0x83` | Inferred from dispatcher-local `r6=3` |
| `0x0238CE00` | read | `0x83` | Inferred from dispatcher-local `r6=3` |
| `0x0238D224` | read | `0x80` | Fixed immediate `r0=0` |
| `0x0238D31C` | send | `0x00` | Fixed immediate `r0=0` |

**These are command-byte calculations, not coordinate samples.** The preserved-register inference uses exact dispatcher `MOV` instructions `0x0238CB30` (r5=2) and `0x0238CB34` (r6=3), but is not full control-flow/liveness proof. Six of twelve callers remain dynamic or unresolved, including callers with `r8`, whose value is passed into dispatcher at `0x0238CB28`.

A superficially interesting command byte is not sufficient to label a path touch X/Y. The previously verified SPI helper returns an eight-bit read, with no confirmed ADC X/Y assembly or ARM9 game-menu dispatcher. This milestone does not modify the ROM or provide a playable patch.

## Reproduce

```bash
cd sims3_spi_command_bytes_milestone
python -m unittest -v
python analyze.py '/path/to/Sims 3 USA VS3E.nds' --out results
```

Nine tests verify call count, fixed-command classifications, unknown classifications, opcode anchors, branch targets, and rejection of modified or different ROMs. `results/commands.csv` and `results/commands.json` include all 12 calls, confidence and source addresses. This ZIP omits copyrighted ROM bytes.

## Next technical step

Resolve the six dynamic call arguments (especially the r8 entry parameter) with a bounded interprocedural ARM7 control-flow trace, then trace any genuine touch-coordinate producer into ARM9 IPC and UI code. Prefer runtime tracing to prove sampling and integration before modifying input handling.
