# The Sims 3: Pets — Nintendo DS mod

## Scope
Add pet gameplay to the *existing The Sims 3 DS* project while retaining the original game's world, lot/map transitions, bottom-screen HUD, and Build/Buy interaction rules. This is a fan-made Pets feature mod, not a claim that the 3DS Pets game can be run directly on DS.

## Milestone P1: gameplay rules prototype (implemented, source-only)
- Cats and dogs, names and household ownership (maximum 3 pets in the prototype; provisional balance decision).
- Hunger, energy, hygiene, fun and bond; feed, play, groom, rest, and dog-only walk.
- Deterministic need decay and a versioned, separate serialization shape.
- Host tests: `python -m unittest discover -s tests -p 'test_pets.py' -v`.
- **Not wired to the game's saves or ROM**. Never overwrite retail save data with this prototype format.

## Milestone P2: host-mode integration contract (source-only boundary added; ROM hook unverified)
- **Implemented in source:** `tools/pets/session.py` gates adoption, selection, interactions and time progression to active in-lot gameplay, clears selection on map/Build/Buy/social/paused transitions, and returns data snapshots without touching the original game's UI or save data.\n- **Tests added:** `tests/test_pets_session.py` checks gating, safe transitions, and re-selection after menus.\n- Still required: document actual input, object tables, save layout, animation budgets and pet actor slots from a legally acquired personal DS dump.
- Confirm whether the DS world can allocate/render/animate extra animal actors without disrupting Sim gameplay.
- Locate a safe runtime hook for pet actions; preserve original map and Buy/Build behavior.
- Keep any recovered original assets in the private repository or local workspace; do not commit them publicly.

## Milestone P3: in-game pet interactions (not started)
- Household adoption and pet selection controls through game-compatible menus.
- Dog/cat pathing, feeding, sleeping, play, grooming and simple autonomous behavior.
- UI that follows original HUD transitions without adding a fabricated relationships carousel page.
- Map and home-only Buy/Build transitions remain identical to the DS game.

## Milestone P4: assets and persistence (not started)
- Use independently created animal art or appropriately authorized locally held assets.
- Determine native animation and texture constraints before import.
- Reverse-engineer and test a save extension or sidecar that cannot corrupt existing saves.
- No private ROMs or copyrighted assets in public CI.

## Milestone P5: patched ROM and melonDS verification (not started)
- Build only using a user-supplied original game dump and a patching workflow.
- Verify emulator boot, pet lifecycle, original HUD, save/reload, map transitions and Buy/Build.
- Publish source and patch instructions rather than redistributing the original ROM.

## Honest status
P1 is independent gameplay code only. P2 now includes a source-only host-mode safety contract, but **no native ROM hooks**. The project does **not** yet have an integrated, playable Pets ROM, pet models, or verified original-game hooks. Actual memory/asset research is the next blocking work.
