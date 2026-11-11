# The Sims 3 DS — ARM7 SPI Caller Milestone

## Verified result

Analyzed the user's original USA VS3E NDSi-enhanced ROM, identifying **23** direct ARM-state `BL` call edges into five local SPI-related ARM7 routines. The result is a static control-flow inventory rather than a runtime trace or a working mod.

| Routine | Direct ARM BL callers | Interpretation |
|---|---:|---|
| `0x0238C9D8` | 4 | Sends byte through SPI setup/helper path |
| `0x0238CA54` | 8 | SPI transfer helper that reads peripheral reply |
| `0x0238CAC8` | 4 | Composes calls to both helpers |
| `0x0238CAF0` | 4 | Another wrapper around both helpers |
| `0x0238CB20` | 3 | Larger peripheral dispatch structure |

Direct, verified edges include `0x0238CAD8 -> 0x0238CA54`, `0x0238CAE4 -> 0x0238C9D8`, `0x0238CB00 -> 0x0238CA54`, `0x0238CB14 -> 0x0238C9D8`, `0x0238CBB8 -> 0x0238CAC8`, `0x0238CBC4 -> 0x0238CAF0`. All are in the ARM7 load range read from the ROM header.

The helpers select SPI peripheral 2 in the previously verified code, but the higher-level `0x0238CB20` routine handles other peripheral operations as well. Do **not** infer that every call is touchscreen input, or that a direct caller is the final game UI handler.

## Reproducing

```sh
python3 -m unittest -v test_trace_spi_callers.py
python3 trace_spi_callers.py '/path/to/your/Sims 3 DS USA.nds' --output ./results
```

Output: `call_graph.json` and `direct_callers.csv`. The script only reads the ROM and does not include or distribute any proprietary bytes.

## Next investigation

Trace `0x0238CB20`'s command-dispatch branches and touchscreen ADC commands, then follow resulting sample values through conversion/storage and ARM7→ARM9 transfer. Validate in an emulator debugger before patching touch events or top/bottom screen routing.

## Status

- Analyzer executed successfully against the uploaded ROM; five tests passed.
- **No executable hook, patched ROM, or melonDS UI modification** has been completed.
