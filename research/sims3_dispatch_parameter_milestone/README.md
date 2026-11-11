# The Sims 3 DS — ARM7 dispatch-parameter provenance milestone

Original ROM: USA/NDSi Enhanced VS3E; SHA-256 `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`.

## Confirmed findings

The general peripheral dispatcher at ARM7 `0x0238CB20` saves its second argument (`r1`) in `r8` and dispatches on selector `r0` (0 through 25).

* The caller at `0x0238C904` loads the selector from `[r4+8]` (`0x0238C8BC`), loads the parameter from `[r4+12]` (`0x0238C8C0`), and truncates that parameter to 16 bits (`0x0238C8F8`/`0x0238C900`) before dispatch. `r4` points to a command structure at this code location; the structure's origin has not been determined.
* Case 24 at `0x0238CEF8` copies dispatcher argument `r8` to `r0` and calls the SPI read helper `0x0238CA54` at `0x0238CEFC`. This proves the read command is supplied by the dispatcher caller; it is not a fixed touch ADC command.
* Case 25 at `0x0238CF04` extracts `(r8 >> 8) & 0xFF` as its command and `r8 & 0xFF` as payload, calling the SPI write helper `0x0238C9D8` at `0x0238CF10`.
* Two other dispatcher call sites `0x0238D33C` and `0x0238D348` select commands 6/7 and 4/5 respectively, based on bits of an existing register. Both set `r1=0`.

These instructions and five direct branches are verified against the exact ROM revision, not generalized to different versions. The analysis does **not** prove which SPI device is selected at runtime, a coordinate decoder, or an ARM9 UI handler. No ROM patch was made.

## Reproduce

```bash
python3 -m unittest -v test_analyze.py
python3 analyze.py '/path/to/original Sims 3 VS3E.nds' --out results.json
```

Eleven tests check the SHA-256, exact ARM7 opcode anchors and BL targets, observed provenance, and rejection of damaged code/other ROMs. The package includes only analysis scripts and JSON, not copyrighted ROM bytes.

## Next development objective

Trace the producer of `[r4+8]` and `[r4+12]`, then correlate the SPI-device selection and 12-bit ADC output with ARM7→ARM9 communication in a runtime trace. Do not install a gameplay hook until actual touch samples and menu event dispatch are proven.
