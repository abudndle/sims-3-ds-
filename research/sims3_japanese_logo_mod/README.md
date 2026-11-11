# The Sims 3 DS — Japanese Title Logo Mod v1

A **real ROM asset replacement mod**, using the Japanese-localized logo bitmap already present inside the USA VS3E Rev 0 ROM. This changes only the `DATA/BACKEND/MENU/Sims3Logo.bmp` file contents, leaving NitroFS offsets, FAT, code, and all other files unchanged. It does not unlock gameplay or restore the LODTESTBED scenes.

## Installation

Requires Python 3.9+ and a personally dumped USA `VS3E` Rev 0 ROM matching the source CRC32 embedded in the patch.

```bash
python3 apply_bps.py "your-original.nds" Sims3_DS_Japanese_Title_Logo_v1.bps "Sims3_JP_Logo_Mod.nds"
```

Run the output with melonDS. The original file is not modified. The patch is in standard BPS format and also works with BPS-capable patchers.

## What changes

Original NitroFS path: `DATA/BACKEND/MENU/Sims3Logo.bmp` (offset 87095808; 50232 bytes). Replaces bitmap data with `Sims3Logo_Jp.bmp` (50230 bytes, padded with two zero bytes to preserve the original allocation). Both images are 256 × 192, 8-bit indexed BMPs. The bitmap's own BMP header remains intact.

## Verification

- Input ROM CRC32 check prevents application to incompatible revisions.
- BPS output CRC32 verifies all bytes after patching.
- The output differs only inside one known asset region; no executable code modified.
- **Visual gameplay boot has not been confirmed.** If the earlier secure-area issue remains, this title image may not be visible in melonDS even though the ROM was patched correctly.
- This is a **logo mod**, not confirmed cut gameplay content.

## Copyright

Patch contains only changed image data sourced from the user's own game ROM; no complete ROM is included. Do not distribute the original ROM.
