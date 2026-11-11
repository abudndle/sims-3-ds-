# The Sims 3 DS — ARM7 SPI Access Mapping Milestone

## Result
Analyzed the user's verified VS3E ROM (`Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds`) without modifying it.

- ROM SHA-256: `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`
- 54 candidate PC-relative ARM loads of SPI register addresses in the original ARM7 binary.
- 11 address-proximity groups (160-byte gap heuristic); 10 contain loads of both `SPICNT` (0x040001C0) and `SPIDATA` (0x040001C2).
- Five synthetic decoder/grouping/header tests passed.
- Evidence is in `spi_references.csv`, `spi_groups.csv`, and `spi_report.json`.

## Significant regions

- 0x0238C9DC–0x0238CAA8
- 0x023934BC–0x0239360C
- 0x023939E8–0x02393C34

These are scan ranges, **not validated function boundaries**. The SPI controller services multiple peripherals. The results do **not** identify touchscreen command transfers, X/Y coordinate fields, a game UI dispatcher, or code safe to patch.

## Reproduction

```bash
python -m unittest -v
python scan_spi.py '/path/to/your/verified/Sims 3.nds' --output output
```

Works with Python 3 standard library; no copyrighted game content is included here.

## Next work

1. Inspect individual ARM7 SPI accesses and isolate commands consistent with touch ADC sampling, distinguishing from firmware and power management SPI traffic.
2. Trace their decoded coordinates into ARM7/ARM9 shared memory or FIFO, then identify the game's touchscreen event dispatcher.
3. Test safe screen-input integration only after verifying execution paths; do not patch SPI controls blindly.

## Current project state

No original ROM changed; this archive is an analysis milestone, **not a working top-screen 3D/bottom-screen UI mod** and not a melonDS screenshot.
