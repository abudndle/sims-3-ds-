# Sims 3 DS — validated button input literal pairs

## Milestone outcome

Read-only scan of the user-supplied USA `VS3E` Nintendo DS ROM. Both candidate Thumb input routines reference the hardware button register `0x04000130` and the shared input-related location `0x02FFFFA8`. This is a stronger, independently checkable fact than a merely named 'input function'. It does **not** prove either routine consumes touchscreen XY coordinates.

### Verified instruction-to-literal references

| Routine candidate | Thumb LDR | Literal pool | Literal value |
|---|---|---|---|
| A | `0x02095C1A` | `0x02095C4C` | `0x04000130` KEYINPUT |
| A | `0x02095C1C` | `0x02095C50` | `0x02FFFFA8` input-related shared state |
| B | `0x020A150E` | `0x020A1584` | `0x04000130` KEYINPUT |
| B | `0x020A1510` | `0x020A1588` | `0x02FFFFA8` input-related shared state |

A has halfword load instructions at `0x02095C1E` and `0x02095C20`; B has halfword loads at `0x020A1512` and `0x020A1514`. Those provide evidence the addresses are consumed as input in these local snippets, rather than being arbitrary data strings. The scanner strictly validates ARM9 ROM bounds and uses Thumb PC-aligned literal load encoding.

## Reproduce

```bash
cd sims3_input_literal_milestone
python -m unittest -v
python analyze_input_literals.py '/path/to/your/VS3E.nds' --output input_literals.json
```

Five synthetic-decoder/bounds tests passed, and both exact literal pairs were verified against the actual uploaded ROM. The extracted input report includes the source ROM SHA-256, so it can be matched to a later build.

## Next engineering step

Capture runtime memory reads or breakpoints around these four instructions while interacting with **physical buttons** and **touchscreen UI** separately. Observe which consumers react to tap XY data. Only then locate the UI dispatcher and an appropriate reversible hook. Merely patching the shared-state address, or flipping the display register, would risk breaking touchscreen interaction.

The original ROM and game assets are deliberately not bundled or modified. There is no playable modified ROM or modified gameplay screenshot in this milestone.
