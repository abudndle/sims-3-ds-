# The Sims 3 DS — bounded ARM9 Thumb input call tracing

This is a **static reverse-engineering milestone**, not a playable mod. The original user-supplied ROM was only read; it is not included in the archive.

## Verified ROM
- Game: The Sims 3 DS USA NDSi Enhanced (`VS3E`)
- SHA256: `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`
- ARM9 mapped start: `0x02004000`; end exclusive: `0x021806C0`

## Newly verified instruction paths
- `0x02095C0C`: Thumb routine prologue (`push {r3,lr}`), calls a helper and reads `KEYINPUT` via `LDRH` at `0x02095C1E`. It finishes by normalizing/masking button bits and returns at `0x02095C4A` (`pop {r3,pc}`). A direct Thumb `BL` at **`0x02095CEA`** targets this entry.
- `0x020A14E4`: separate Thumb routine beginning `push {r4,lr}`; performs calls and reads a `KEYINPUT` register literal at `0x020A150E` followed by `LDRH` at `0x020A1512`; a direct Thumb `BL` at **`0x020A2712`** targets this entry.

The results are supported by actual Thumb-1 instruction bytes and LLVM disassembly of the adjacent ROM instructions. Scanner searches the entire bounded ARM9 image for BL/BLX encodings and identifies exact immediate destinations. It does not prove callers execute during gameplay. The second routine's name and exact purpose remain tentative.

## Reproduce
```
python -m unittest -v test_trace.py
python trace.py 'Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds' --out report.json
```

## Next integration blocker
The input consumer/gameplay event dispatcher and ARM7 touchscreen-coordinate transfer remain unconfirmed. Disassembly and tracing of these **two caller sites** should precede any code injection. The current original UI/rendering layout and faster camera are unmodified. No physical-hardware or modified-ROM testing occurred for this milestone.
