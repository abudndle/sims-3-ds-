# The Sims 3 DS — SPI helper command-provenance milestone

Analyzed the user's verified 128 MiB `VS3E` Nintendo DS ROM with a read-only scanner. The original ROM is unchanged.

## Findings

- Exactly 12 aligned ARM `BL` instructions in the ARM7 binary directly target one of the two previously identified SPI transfer helpers `0x0238C9D8` (`spi_send`) and `0x0238CA54` (`spi_read`).
- The helper caller inventory includes new targets at `0x0238CCF0`, `0x0238CD34`, `0x0238CD9C`, `0x0238CE00`, `0x0238CEFC`, `0x0238CF10`, `0x0238D224`, and `0x0238D31C`, in addition to previously analyzed wrapper calls.
- A preceding `MOV r0,#imm` appears near some calls (values 0 or 3). This is merely a nearby constant: intermediate instructions or branches may change `r0`, so it is not confirmed as the actual SPI command.
- The inspection **does not** establish that these helpers sample X/Y touchscreen coordinates or that they connect to the game UI event dispatcher.
- No ROM patch is created, and this milestone has no emulator gameplay capture.

## Reproduce

```bash
python3 -m unittest -v test_trace.py
python3 trace.py '/path/to/Sims 3 DS VS3E.nds' --out results
```

Files: `trace.py`, `test_trace.py`, `results/spi_helper_calls.csv`, `results/spi_helper_calls.json`. Only metadata and scripts are distributed, no original game binaries/assets.

## Next investigation

Disassemble the eight non-wrapper call sites with register-flow tracking, then identify true ADC X/Y sample commands and their store/IPC handoff. Follow with debugger traces and a minimal reversible ROM input patch only when the actual game UI handler is confirmed.
