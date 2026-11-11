# The Sims 3 DS — reworked-controls tutorial TEXT PREVIEW

This is a **real BPS patch to the original USA VS3E Rev 0 ROM localization asset**, built from the user-supplied ROM and verified by reapplying it. It replaces three tutorial/help messages describing the *planned* control and screen configuration.

## Critical limitation

**The new controls and screen routing are NOT implemented in this ROM.** This is a **text-only proof-of-concept**, not a finished or playable controls conversion. Some prompts in the original tutorial still expect the original inputs, including X/B for zoom and L/R for page navigation. The tutorial may be inconsistent until the gameplay/input code is integrated. Do not treat this as the finished control mod.

## Use

```bash
python3 apply_bps.py 'Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds' Sims3_DS_Tutorial_Text_Preview.bps Sims3_Tutorial_Preview.nds
```

Only the English tutorial strings in `DATA/LOCALIZATION/text_db_dynamic.arc` are modified. CRC32 validates the source and output. The original ROM remains unchanged.

## Next engineering milestones

1. Identify in-game tutorial state/input gates and remap them from stylus/X/B/L/R actions to the new controller behavior.
2. Implement the D-Pad blue/green ground cursor and A/B interactions with original DS resources.
3. Move gameplay 3D to the top screen and UI to bottom while preserving touch interactions.
4. Update all English tutorial pages and localization consistency, then validate gameplay in melonDS.

No full ROM or proprietary game assets are included in this patch package.
