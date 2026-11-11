# The Sims 3 DS — ARM7 command-record producer handoff milestone

## Scope
Read-only static examination of the USA VS3E Nintendo DS/DSi-enhanced game ROM (SHA-256 `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`). No original ROM bytes distributed or patched.

## Verified new finding

The peripheral dispatcher at `0x0238CB20` receives a selector and a parameter from a **command record**, and the record can now be traced one level upstream:

1. `0x0238C5B0` begins an ARM7 loop. It loads a global context pointer from a literal (`0x0380B548`) and passes `r1 = sp` as an output pointer to `0x02385C68` via BL at `0x0238C5CC`.
2. `0x0238C5D0` reads a returned record pointer from `[sp]` into `r0`; `0x0238C5D4` loads its first word `[r0]` as a record-type discriminator, accepting types `0`–`3`.
3. A four-entry halfword jump table at `0x0238C5EC` with offsets `[4, 28, 12, 20]` relative to PC base `0x0238C5F0` dispatches **type 3** to `0x0238C604`, which calls `0x0238C7F0`.
4. `0x0238C7F4` saves the received `r0` record pointer in `r4`. `0x0238C8BC` reads the selector at `[r4+8]`, and `0x0238C8C0` reads the parameter at `[r4+12]`. The latter is narrowed to 16 bits before BL at `0x0238C904` to `0x0238CB20`.

**Interpretation:** this is a confirmed **record-reader → command-handler → SPI dispatcher** code relationship. The record reader resembles a queue/receive routine; its producer and any IPC hardware origin remain **unverified**. No touchscreen X/Y decoder or ARM9 gameplay UI handler is established. This is not a playable mod.

## Reproduce

```sh
cd sims3_command_record_handoff_milestone
python3 -m unittest -v test_analyze.py
python3 analyze.py '/path/to/original_Sims_3_VS3E.nds' --out results.json
```

The analyzer verifies 21 anchored ARM opcodes/data words, three ARM `BL` targets, and ROM identity. Eight regression tests include negative corruption tests. It never writes to the ROM.

## Next technical step

Inspect the producer for the `0x02385C68` record-reader path and whether the resulting event structure is delivered through ARM7/ARM9 IPC. Independently trace standard touch-sampling and shared-memory coordinate values in live melonDS debugging before wiring a UI hook. Avoid treating SPI configuration and peripheral command dispatch as a proved touchscreen pipeline.
