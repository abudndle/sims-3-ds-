# The Sims 3 DS — cross-CPU shared-input reference milestone

## Verified scope

The supplied USA VS3E game ROM (SHA-256 `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`) was analyzed read-only. ARM7 and ARM9 binaries were located using the actual NDS header, not guessed entry addresses.

A bounded scanner decodes 16-bit Thumb `LDR Rt,[PC,#imm]` and 32-bit ARM PC-relative `LDR` instructions, resolves their literal pools, and selects shared input/IPC-region addresses. It yielded **28 instruction-to-literal matches** across both processors. This scan is not complete disassembly and some decoded patterns could be data interpreted as instructions.

### Cross-CPU reference leads

| Shared memory address | ARM9 instruction lead(s) | ARM7 instruction lead(s) |
|---|---|---|
| `0x02FFFF94` | `0x020D7DAC` | `0x0238E170`, `0x0238E21C`, `0x0238E474` |
| `0x02FFFF98` | `0x02180270` | `0x023943B4`, `0x02394C9C`, `0x023974A4` |
| `0x02FFFFA8` | `0x02095C1C`, `0x02098B42`, `0x020A1510`, `0x020C9578` | `0x02388028` |

All addresses above are **static literal-load candidates**. The exact semantics of the underlying shared structures (touch X/Y, pressure, buttons or other state) are not proven. In particular the `0x02180270` reference is near the ARM9 image boundary and warrants code-vs-data scrutiny. The hardware ADC/touch data path and UI tap dispatcher remain to be discovered. No executable patch has been created.

## Reproduction

```sh
python -m unittest -v
python scan_handoff.py '/path/to/your/USA-VS3E.nds' --out .
```

The script produces `handoff.csv` and `handoff.json` without changing the ROM. Five host-side unit tests pass. Its results include original ROM SHA-256 and exact input-image address spans.

## Next task

Disassemble ARM7 code around the `0x02FFFF94` / `0x02FFFF98` references and ARM9 consumer paths. Use melonDS debugging to distinguish touch taps from buttons and measure exact X/Y shared-state fields, before making any reversible hook patch. Ultimately, the Sims-icon touch event should route to the normal Sim Information panel only in normal gameplay, and other bottom-screen UI controls should remain separate from tutorial progression.
