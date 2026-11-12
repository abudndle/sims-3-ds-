# The Sims 3 (Nintendo DS): cut-content evidence register

Status: **research only — not a ROM restoration**. Scope: Nintendo DS game, not PC, Wii, or Nintendo 3DS assets or features. Follow [issue #4](https://github.com/abudndle/sims-3-ds-/issues/4).

## Evidence levels

- **Released/inaccessible**: location or feature demonstrably exists but players cannot reach/use it in ordinary play. This alone does **not** prove a cut feature.
- **Unused data**: file/assets are present in a retail release but runtime use has not been demonstrated. This alone does **not** prove intended gameplay.
- **Debug-only**: retail binary contains functionality reached through a debugger or cheat. Retaining development tools is not proof they were meant as user-facing content.
- **Confirmed cut/restorable**: requires an asset/function/entry-path analysis and an explicit demonstration that content was intended to be accessible, plus a safe patch plan.
- **Restored**: actual integrated modification is verified in melonDS; do not use this label for research or prototypes.

## A. Apartment access in Beacon Bay

The released DS game names **Strangetown Apartments**, **Mesa Flats** and **Belladonna Cove Condos**. Sources report that apartments house townies but their interiors and residents cannot be viewed. This establishes **released/inaccessible**, not **confirmed cut interiors**.

Source: https://sims.fandom.com/wiki/The_Sims_3_%28Nintendo_DS%29

**Unknown:** existence of interior models, room data, apartment load targets, usable door triggers, scripts or save flags. Do not invent apartments or mark them restorable until recovered from a legally obtained DS game dump and verified.

Required checks on private authorized ROM:
1. Extract NitroFS inventory, retain SHA-256 and the ROM revision/region; do not commit proprietary bytes.
2. Search case-insensitively for names and possible identifiers: `Strangetown`, `Mesa`, `Belladonna`, `apartment`, `condo`, `flat`.
3. Identify any candidate room/lot/scene assets by file format, internal references, and cross-references (not merely filenames).
4. Compare working enterable lots' door interactions and load targets with apartment exteriors.
5. In melonDS, inspect a normal retail baseline for door hotspots; only attempt a reversible isolated patch when a real load target exists.
6. Prove entry, return path, interaction behavior, and save compatibility. If no interior asset exists, report that *restoration* is blocked and a new interior would be original mod content.

## B. European debug menu (verified documented debug functionality)

The Cutting Room Floor documents a **European retail version** debug menu accessible using an Action Replay code and pressing **L**, preferably while in a household:
```
1202485C 0000D010
94000130 000001FF
1202485C 0000E00C
D2000000 00000000
```
Source: https://tcrf.net/The_Sims_3_(Nintendo_DS)/Debug_Menu
Alternative mirror: https://tcrf.tiago.zip/wiki/The_Sims_3_%28Nintendo_DS%29-2fDebug_Menu

Documented categories: wishes/opportunities; moods, skills, motives, traits; inventory/accessories; Sim control (including *send current Sim to a lot*); relationships; career; wonders; autonomy; debug interactions.

**Critical limitation:** the source warns that the game crashes after Moodlet 17 when adding moodlets using this debug menu. Do not ship/debug-enable unguarded commands or expose unsafe actions to regular players.

**Candidate apartment experiment:** compare the European debug menu's `send current sim to a lot` destination enumeration with the normal neighborhood's lot list. Record whether apartments appear as destinations and whether any verified interior is loaded. A listed destination alone does not prove it is functional.

## C. Verified unused graphics (not automatically playable cut features)

The Cutting Room Floor reports the following Nintendo DS unused graphics:
- `Sims3Logo-Jp.bmp` — Japanese logo
- `default_custom_material.bmp` — developer image
- `Icon_Placeholder.bmp` — phone placeholder
- `player_placeholder_large.bmp` and `player_placeholder_medium.bmp` — player icon placeholders
- `w_lifetime_placeholder_Small.bmp` — lifetime wish placeholder

Source: https://tcrf.net/The_Sims_3_(Nintendo_DS)

Treat these as documented **unused graphics**, not as proof of removed playable mechanics or a reason to overwrite the game's original HUD.

## D. Earlier reported possible test assets (unverified)

Prior investigation noted `DATA/LODTESTBED/Blue Box.dsm`, `Green Box.dsm`, `Red Box.dsm`, `Yellow Box.dsm` and `boxes.dst`. **No independent file/path verification in the currently accessible repository was completed here.** Classify as unverified candidates pending ROM inventory and runtime cross-references.

## Repository/tooling blockers

At time of writing:
- The public README states that independent control/UI prototypes are **not integrated** into a modified retail ROM, and no verified playable rework ROM exists.
- The private README states that private references and manifests exist, but full original DS ROM files are **not uploaded**.
- Do not copy a ROM, extracted copyrighted graphics/models, or private binaries to the public repo or GitHub Actions artifacts.
- Do not accidentally apply PC, Wii or 3DS cut-content lists to the DS game.

## Next testable milestone

**Reproduce and inventory the European debug-menu destinations with a user-owned European DS ROM in melonDS; audit apartment door-to-interior links in parallel.** A passing milestone requires (a) build/revision hash, (b) evidence of menu/destination behavior, (c) candidate asset-to-code cross-reference or documented absence, and (d) a binary decision: native restoration possible, further analysis needed, or original mod content would be required. No code may be marked 'restored' without a booted modified ROM and functionality tests.
