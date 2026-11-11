# Original Sims 3 DS DST1 UI assets — verified decode milestone

- Input: supplied `VS3E` Nintendo DS ROM extraction (`DATA/BACKEND/HUD`). Original ROM unchanged.
- New verified format subset: `DST1` header, width/height at offsets `0x0c`/`0x0e`, palette count at `0x10`, palette BGR555 from `0x12`, linear 4-bit pixels after palette; first palette entry rendered transparent for the visual preview.
- The original button sprites decode to recognizable graphics; the atlas was generated directly from original DST1 bytes, not generative art.
- `actual_rom_asset_tutorial_preview_256x192.png` is a **layout preview using real extracted sprites**. Backgrounds and text are placeholders, not game graphics or a melonDS capture.
- A decoded sprite is not proof that the game uses that sprite for the proposed purpose; it remains to hook the game's original resource loader, scene renderer and touch input.
- The 3D view/top-screen reassignment, camera-speed matching and task UI are not yet integrated in the ROM.
- To reproduce in this environment: `python sims3_dst_asset_milestone_build.py`. Input files must come from your own game dump.

Tests: every successful asset has an exact predicted length; preview is exactly 256x192; all its asset placements lie within bounds.
