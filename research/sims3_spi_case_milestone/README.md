# The Sims 3 DS — ARM7 SPI command-case semantics milestone

## Result

The original USA NDSi-enhanced Sims 3 DS ROM (`VS3E`) contains a 26-way ARM7 dispatch table at `0x0238CB20`. Six entries have now been decoded beyond their destinations:

| Case | Action | Bit mask | Wrapper |
|---|---|---|---|
| 4 | set bits (OR) | `0x04` | `0x0238CAC8` |
| 5 | clear bits (AND NOT) | `0x04` | `0x0238CAF0` |
| 6 | set bits (OR) | `0x08` | `0x0238CAC8` |
| 7 | clear bits (AND NOT) | `0x08` | `0x0238CAF0` |
| 8 | set bits (OR) | `0x0C` | `0x0238CAC8` |
| 9 | clear bits (AND NOT) | `0x0C` | `0x0238CAF0` |

Each case target and its branch path was verified from the actual ARM instruction encodings; wrapper operations were verified from their instructions. The helpers call SPI read/write routines using the ARM7 SPI hardware registers. These cases behave as peripheral configuration bit toggles, **not a demonstrated touch X/Y ADC reader**. The earlier broad description of the entire dispatch table as a touchscreen dispatcher is NOT justified. Other cases and other routines may still handle touch input; none is yet confirmed.

## Reproduce

```sh
python3 analyze_spi_cases.py '/path/to/Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds' --out .
python3 -m unittest -v test_spi_cases.py
```

Tests require the input ROM at the known test path in `test_spi_cases.py`; adapt `ROM` in that file if needed. No NDS data is embedded or redistributed in this package. Original ROM untouched. The scanner verifies exact instructions and rejects changed or out-of-bounds bytes.

## Next technical work

Trace the other dispatcher cases and search for actual ADC command bytes and 12-bit X/Y sample assembly. Verify values in a runtime trace before connecting the ARM9 touchscreen UI dispatcher. The requested screen-routing, task menus, cursor, faster camera, and original-asset controls have **not** been installed in a playable ROM.
