# Sims 3 DS — ARM7 command consumer dispatch milestone

## Verified milestone

Read-only disassembly and opcode validation against the supplied Sims 3 DS USA `VS3E` ROM, SHA-256 `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`.

The record-processing loop at **0x0238C5B0** uses a **four-entry halfword jump table** at 0x0238C5EC to select a handler by record type:

| Record type | Jump landing | Direct handler BL target | Secondary command selectors |
|---|---|---|---|
| 0 | 0x0238C5F4 | 0x0238D920 | 0, 1, 2, and conditional 16 |
| 1 | 0x0238C60C | 0x01B69CC0 (as encoded) | Undetermined |
| 2 | 0x0238C5FC | 0x0238E3B8 | 0x40, 0x41, 0x42 |
| 3 | 0x0238C604 | 0x0238C7F0 | Previously traced peripheral commands |

The type-1 branch destination is **outside the loaded ARM7 image**; do not interpret it as a valid callable function without proving relocation, overlay, or other runtime behavior. The prior 13 direct producer calls only create types 0, 2, and 3, so no direct type-1 producer was found in that earlier scope.

The type-0 handler loads the secondary selector at `[r10+4]` (0x0238D928) and compares against 0, 1, 2 and 16. The type-2 handler loads `[r6+4]` (0x0238E3E4) and compares against 64, 65 and 66. These are *record command selectors*, not decoded touch X/Y coordinates.

All **19 ARM instruction anchors** and **3 in-image handler BL edges** are validated. Nine tests cover original ROM, table mapping, selectors and corruption rejection. No copyrighted ROM bytes, extracted game assets, working input hook, or emulator screenshots are distributed.

## Reproduce

```sh
export SIMS3_ROM='/path/to/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds'
python3 -m unittest -v test_analyze.py
python3 analyze.py "$SIMS3_ROM" --out results.json
```

`results.json` is the analysis result generated using the exact supplied ROM. The analyzer never modifies the input ROM.

## Next target

Trace type-0/type-2 message fields and callback destinations; independently locate ARM7 touchscreen coordinate publication and ARM9 UI reception using verified dataflow or runtime tracing. The SPI command-record service is not established as the touch pipeline.
