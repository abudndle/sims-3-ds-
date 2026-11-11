# The Sims 3 DS — ARM7 SPI byte-transfer contract milestone

This read-only milestone inspects the user's verified USA VS3E Nintendo DS ROM (`SHA-256 d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`). It does not contain proprietary assets or ROM binary data.

## What has been confirmed

Two ARM7 functions have been verified at the level of their exact instruction encodings, rather than nearby command guesses.

| Entry | Static call contract | Relevant evidence |
|---|---|---|
| `0x0238C9D8` | SPI write, accepts command `r0` and payload `r1`; both are masked to eight bits | `0x0238C9F4`, `0x0238CA14` masks, `0x0238CA18` write |
| `0x0238CA54` | SPI read, sets bit 7 in command `r0`, sends a zero dummy byte, reads `SPIDATA`, returns the low eight bits | `0x0238CA6C`, `0x0238CA90`, `0x0238CA94`, `0x0238CAAC`, `0x0238CAB0` |
| `0x0238CA30` | Shared SPI byte transfer helper | BL calls from `0x0238CA04`, `0x0238CA80` |

Both high-level helpers use SPI control value `0x8202` and addresses `SPICNT=0x040001C0`, `SPIDATA=0x040001C2`, with literal slots checked inside the respective functions. The SPI control word selects SPI device 2. The result says **nothing yet** about whether the code samples touchscreen X/Y positions. In particular, the read helper returns *one* eight-bit result per invocation, not a reconstructed twelve-bit coordinate. A higher-level caller *might* combine multiple reads; that has not been demonstrated here.

## Repeat the milestone

```bash
cd sims3_spi_transfer_contract_milestone
python -m unittest -v
python analyze.py '/path/to/Sims 3 USA VS3E.nds' --output results.json
```

The program rejects a different ROM checksum, a changed critical instruction or control-register literal, and unexpected BL destinations. The nine regression tests cover correct and corrupted instruction patterns. To independently examine the ARM7 instruction stream with installed LLVM, extract the ARM7 image using the NDS header at `0x30` and disassemble the load-addressed ARM section.

## What remains unresolved

1. Whether these SPI helpers execute for game touchscreen sampling during play.
2. Where any 12-bit ADC conversions are combined and calibrated.
3. How coordinates cross ARM7/ARM9 and reach the game's touchscreen/UI dispatcher.
4. Integration and emulator verification of the requested Sims 3 DS control/UI modification.

Original ROM unchanged. No in-game patch or melonDS screenshot is claimed for this milestone.
