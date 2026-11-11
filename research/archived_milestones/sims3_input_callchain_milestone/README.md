# The Sims 3 DS — ARM9 input call-chain milestone

This read-only analysis uses the verified USA VS3E NDSi Enhanced ROM, SHA-256 `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`. It does not distribute the ROM or modify its contents.

## Verified static Thumb BL call-chain candidates

- `0x02095D94` -> candidate consumer at `0x02095CBC` -> at `0x02095CEA` calls hardware input routine `0x02095C0C`.
- `0x020847C8` -> candidate consumer at `0x020A2690` -> at `0x020A2712` calls input routine `0x020A14E4`.

These four immediate branch destinations were computed from Thumb BL instruction encoding in the bounded ARM9 binary. Each candidate routine begins with a Thumb PUSH instruction. This improves the static call map but **does not establish that these paths are active during gameplay** or that either implements touch UI. Some matched bytes can theoretically be literal data, and reverse engineering of full function boundaries remains necessary.

## Reproduce

```sh
python3 -m unittest -v test_trace_callchain.py
python3 trace_callchain.py '/path/to/your/Sims 3 DS.nds' --output callchain.json
```

The tool reads only, validates ARM9 bounds from the DS ROM header, rejects out-of-image addresses, and emits the source ROM SHA-256 plus callsites and byte encodings.

## Next integration prerequisites

1. Inspect control flow around `0x02095D94` and `0x020847C8` to identify their enclosing routines and their callers.
2. Establish the ARM7 touchscreen-coordinate data transfer and the ARM9 UI dispatcher via runtime tracing.
3. Confirm behavior in melonDS before attempting a reversible patch.
4. Integrate the previously host-tested Sims-icon, tutorial, and task state code **only after** a safe input/UI hook is identified.

**Status:** two 2-hop static input paths mapped; no gameplay screen-routing patch, interactive control modification, or modified-ROM test has been completed in this milestone.
