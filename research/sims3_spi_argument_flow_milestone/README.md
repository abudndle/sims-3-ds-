# The Sims 3 DS — ARM7 SPI argument-flow milestone

This milestone examines the 12 direct ARM7 branch-with-link calls to the previously mapped low-level SPI transfer helpers (`0x0238C9D8`, `0x0238CA54`) in the verified USA VS3E ROM. It does not modify the game ROM or claim in-game control changes.

## Reproducible findings

- 12 direct helper calls mapped in ARM7.
- Three calls have an unambiguous immediately preceding unconditional `MOV r0,#0` instruction: `0x0238CCF0`, `0x0238D224`, `0x0238D31C`.
- Seven calls immediately load `r0` from another register (`r4`, `r5`, `r6`, or `r8`), so the command value is dynamic or determined upstream.
- The remaining two calls have nearby non-immediate assignments. These are marked as unverified leads rather than proven values.
- At `0x0238CF10`, the preceding instruction masks `r8` to 8 bits for `r1`; an earlier `AND r0,r0,#255` is a nearby lead, not a fully established dataflow proof.
- Static matching does not tell us which calls execute in gameplay, which SPI device is selected at the instant of execution, or where X/Y touch coordinates are decoded.

## Verification

Run:

```sh
python3 -m unittest -v test_analyze.py
python3 analyze.py '/path/to/Sims 3 USA.nds' --out results
```

Tested with Python 3, 9 unit tests passed, 12 calls found. Output includes a ROM SHA-256 for reproducibility. The CSV and JSON contain code addresses and classified instructions only, not proprietary game assets or executable code.

## Next technical action

Identify the device-select register's live value during candidate SPI calls and follow the actual ADC X/Y command sequence (`0xD0` / `0x90`, as relevant to the DS touchscreen protocol). Then trace output registers and stores/IPC into ARM9. Without execution-path confirmation, these candidate functions are not safe control-patch entry points.
