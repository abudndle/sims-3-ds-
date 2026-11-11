# The Sims 3 DS — command producer caller classification

## Result

Read-only analysis of USA VS3E Nintendo DS ROM, SHA256:
`d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`

The 13 direct ARM7 `BL` calls to `0x0238C4C0` divide into **three immediate record types**. Each class is verified by the actual unconditional ARM `MOV r0,#type` instruction at its precise setup address, plus the ARM branch destination.

| Type | Number | ARM7 call sites |
| --- | ---: | --- |
| `0` | 4 | `0x0238D768`, `0x0238D7D8`, `0x0238D820`, `0x0238DB5C` |
| `2` | 4 | `0x0238E158`, `0x0238E214`, `0x0238E25C`, `0x0238E724` |
| `3` | 5 | `0x0238C784`, `0x0238C7AC`, `0x0238D400`, `0x0238D43C`, `0x0238D4E4` |

- Record type 3 has the strongest previously established structural connection to the peripheral command dispatch handler.
- Records of types 0 and 2 have not been classified into precise user-facing subsystem semantics.
- There is **no proof** this command queue carries touch screen samples; it may instead carry internal ARM7 service commands. These are **not** 13 touch input events.
- This package does not contain a modified ROM, proprietary assets, or melonDS screenshots.

## Reproduce

```sh
python3 -m unittest -v test_analyze.py
python3 analyze.py '/path/to/original VS3E.nds' --out results.json --csv callers.csv
```

The scanner checks the ROM SHA-256, ARM7 bounds, the complete set of 13 caller addresses, 13 precise type-setup ARM opcodes, and the 13 branch targets. Nine tests cover valid results, counts, branch decoding and corruption rejection. No ROM bytes are written.

## Next technical target

Trace producer call-site parameters and record type 0/2 consumers to locate any IPC or touch-state handoff **only if supporting instruction evidence exists**. Independently investigate the usual ARM7 input and touchscreen sample publishing path, rather than treating the general-purpose SPI command queue as the touch reader.
