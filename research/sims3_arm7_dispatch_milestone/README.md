# The Sims 3 DS — ARM7 peripheral dispatch-table milestone

## Verified milestone

The correct USA NDSi-enhanced `VS3E` ROM contains a 26-case ARM7 computed jump table at `0x0238CB20`. The instruction sequence bounds the selector with a comparison to `25`, calculates a PC-relative halfword table entry, and jumps to `0x0238CB50 + offset`. All **26** entries resolve to unique, 4-byte-aligned ARM7 addresses within the original ARM7 binary. The result is independently reproducible.

The decoded cases are saved in `dispatch_cases.csv` and `dispatch_report.json`. Examples:

- Case 1 → `0x0238CB80`
- Case 4 → `0x0238CBB4` (starts by loading immediate 4 into r0)
- Case 5 → `0x0238CBC0` (starts by loading immediate 4 into r0)
- Case 10 → `0x0238CBEC`
- Case 25 → `0x0238CF04`

This dispatcher invokes peripheral-support routines including the SPI helpers identified in the previous milestone. **It is not confirmed to be a touch-coordinate decoder or the ARM9/UI touchscreen dispatcher.** It includes commands for other peripheral operations. More instruction-level data-flow analysis is required to map touchscreen sampling, coordinate calibration, and ARM7-to-ARM9 delivery.

## Reproduction

```bash
python3 -m unittest -v test_dispatch.py
python3 analyze_dispatch.py '/path/to/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds' --out .
```

The analyzer validates ROM header bounds, the exact switch instruction structure, all 26 targets and unique target alignment. It only reads the ROM. Nothing is injected, and no proprietary game bytes are included in this toolkit.

## Next engineering task

Follow cases and their parameter values into the SPI helpers, identify ADC command bytes for touch X/Y, and trace the resulting values to a shared memory structure consumed by ARM9. Only after runtime verification should the new game UI handlers be hooked. The 3D-top / original-UI-bottom game patch remains unimplemented.
