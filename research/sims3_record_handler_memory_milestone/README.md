# Sims 3 DS — ARM7 record-handler write-target milestone

## Verified result

Read-only static analysis of the user's original USA VS3E Nintendo DS ROM, SHA-256 `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`.

The type-0 and type-2 handlers have **five exact 16-bit store paths** whose destination addresses can be resolved from actual PC-relative `LDR` instructions and literal-pool values, rather than raw byte search.

| Handler | Store instruction | Destination | Meaning established |
|---|---|---|---|
| type 0 (`0x0238D920`) | `0x0238D9F0` | `0x02FFFFAA` | Shared-memory halfword store; value loaded from stack `[sp+8]` |
| type 0 | `0x0238D9F8` | `0x02FFFFAC` | Adjacent shared-memory halfword store; `[sp+10]` |
| type 2 (`0x0238E3B8`) | `0x0238E478` | `0x02FFFF94` | Shared-memory halfword store |
| type 2 | `0x0238E4E4` | `0x0400010C` | DS Timer 3 counter/reload register `TM3CNT_L` |
| type 2 | `0x0238E4F0` | `0x0400010E` | DS Timer 3 control register `TM3CNT_H` |

The type-2 handler also executes an `ORR` immediate `0xC0` at `0x0238E4EC` before the timer-control write. This is timer enable/IRQ-related flag manipulation; it is not a touchscreen coordinate decode. Conditional paths matter: this table does not imply every store executes on every command.

The type-0 shared-memory halfwords immediately follow the previously mapped `0x02FFFFA8` location, but their *meaning* is not yet verified. In particular, they are **not proven touchscreen X/Y coordinates**. The type-2 path links some record commands to timer operation, useful for deprioritizing that command group as a direct touchscreen-hook target.

## Regression checks

`analyze.py` confirms ROM hash, ARM7 bounds, five PC-relative loads, five literal values, five exact stores and eight additional selector/value instructions. `test_analyze.py` exercises ten tests, including altered ROM, corrupted literal, instruction, store, and stack-value source detection.

```sh
cd sims3_record_handler_memory_milestone
python3 -m unittest -v test_analyze.py
python3 analyze.py '/path/to/original VS3E.nds' --out results.json
```

The toolkit does not include original ROM bytes, game assets, a patched ROM or a simulated screenshot.

## Next milestone

Find the corresponding ARM9 reads of `0x02FFFFAA` / `0x02FFFFAC` (if they exist), or identify the ARM7 routine that writes primary touchscreen samples from the original game's input service. Only after cross-core dataflow and runtime behavior are established can these fields be considered for a reversible touch-control hook.
