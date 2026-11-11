# The Sims 3 DS — ARM7 command-record queue producer milestone

## Proven static findings

Original USA VS3E ROM SHA-256: `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`.

- **Record producer `0x0238C4C0`**: accepts up to four additional 32-bit parameter words (checked at `0x0238C4D0`), populates a record using input registers plus stack arguments, advances a **16-slot ring index** using `AND #15` (`0x0238C554`), then calls the queue push routine at `0x0238C570`.
- **Queue push helper `0x02385BDC`**: stores a **pointer** into a circular pointer queue at `0x02385C40`, then increments queue occupancy at `0x02385C48`.
- **Queue pop helper `0x02385C68`**: loads the pointer from `[buffer+read_index*4]` at `0x02385CC0`, copies it to the caller's output slot at `0x02385CC4`, and decrements occupancy before returning.
- **Consumer `0x0238C5B0`** calls the queue pop helper at `0x0238C5CC`, obtains the same record pointer and dispatches on its type, eventually reaching the previously mapped SPI-command dispatcher for type 3.
- The source code contains **13 verified ARM BL calls** directly targeting the producer `0x0238C4C0`; all caller addresses are in `results.json`.
- **Queue context literal** `0x0380B548` is used at producer and consumer call sites. Other data structures around `0x0380B5A8` appear involved in the record ring, but static mapping does not prove cross-CPU delivery.

This gives an actual **producer → pointer queue → consumer** chain. It does **not** prove that the events are touchscreen input. This record path may carry general commands between game subsystems. No touchscreen X/Y decoder, ARM9 UI handler, or playable gameplay patch is established.

## Reproduce

```bash
python3 -m unittest -v test_analyze.py
python3 analyze.py '/path/to/original_VS3E.nds' --out results.json
```

The analyzer is read-only; it verifies ARM7 bounds, 29 opcode/data sites, 3 BL edges, 13 independent call sites, and ROM SHA-256. Tests include intentional corruption of both instruction and branch bytes. The copyrighted ROM is not included.

## Next stage

Examine the producer's 13 callers to classify record types and determine whether any truly originate from ARM7 touchscreen sampling or originate from ARM9 via IPC. If no touch samples appear, investigate the normal Nintendo DS touch input IPC path independently.
