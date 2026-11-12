# The Sims 3: Pets — Nintendo DS mod

## Scope
Add pet gameplay to the *existing The Sims 3 DS* project while retaining the original game's world, lot/map transitions, bottom-screen HUD, and Build/Buy interaction rules. This is a fan-made Pets feature mod, not a claim that the 3DS Pets game can be run directly on DS.

## Milestone P1: gameplay rules prototype (implemented, source-only)
- Cats and dogs, names and household ownership (maximum 3 pets in the prototype; provisional balance decision).
- Hunger, energy, hygiene, fun and bond; feed, play, groom, rest, and dog-only walk.
- Deterministic need decay and a versioned, separate serialization shape.
- Host tests: `python -m unittest discover -s tests -p 'test_pets*.py' -v`.
- **Not wired to the game's saves or ROM**. Never overwrite retail save data with this prototype format.

## Milestone P2: host-mode integration contract (source-only boundary added; ROM hook unverified)
- **Implemented in source:** `tools/pets/session.py` gates adoption, selection, interactions and time progression to active in-lot gameplay, clears selection on map/Build/Buy/social/paused transitions, and returns data snapshots without touching the original game's UI or save data.
- **Tests added:** `tests/test_pets_session.py` checks gating, safe transitions, and re-selection after menus.
- **Host dispatch contract added:** `tools/pets/bridge.py` validates a limited event vocabulary (`enter_mode`, `adopt`, `select`, `interact`, `advance_time`, `snapshot`), rejects unknown fields/types and supplies detached state snapshots. `tests/test_pets_bridge.py` verifies mode boundaries, rejection without mutation and allowed actions. This does not install an ARM9 hook or intercept game controls.
- **Read-only feasibility inventory added:** `tools/pets/native_readiness.py` validates original DS ROM SHA-256, established ARM9 touchscreen anchors, ARM7/ARM9 sizes, overlay-table and NitroFS boundaries. Run `python3 -m tools.pets.native_readiness /path/to/your/original.nds --output pets_native_readiness.json` locally; outputs only aggregate metadata, no assets. Six synthetic-fixture regression tests run without a retail ROM.
- Still required: document actual input, actor/object tables, save layout, animation budgets and pet actor slots from a legally acquired personal DS dump. Neither native actor location nor patch-ready hook is claimed.
- **Asset metadata investigation added:** `tools/pets/asset_candidates.py` walks the DS NitroFS FNT/FAT directory structure, validates file bounds and identifies animation/interaction/object packages by name and file ID without extracting any ROM data. Run locally with `python3 -m tools.pets.asset_candidates /path/to/your/original.nds --output pets_asset_candidates.json`. Findings are candidates only, not confirmed animal models or patch hooks.
- **Header signature probe added:** `tools/pets/package_probe.py` checks the first four bytes of each NitroFS `.package` and returns a metadata-only report. A `DBPF` or `RIFX` signature is classified as a **candidate**, not a verified resource index; unknown formats are explicitly marked unknown. Run locally: `python3 -m tools.pets.package_probe /path/to/your/original.nds --output package_signatures.json`. No retail package data is committed or exported.
- **Conservative DBPF index-candidate validator:** `tools/pets/dbpf_index_candidate.py` recognizes only a synthetic, fixed-20-byte version-1/index-7 profile with strict table and payload bounds; `package_probe.py` reports matching type IDs as *candidate evidence* only. All other package layouts remain unverified, and even a structural match does not prove native DS resource interpretation. Tests: `python3 -m unittest discover -s tests -p 'test_pets_dbpf_index_candidate.py' -v`.
- **Revision provenance guard:** `tools/pets/manifest_provenance.py` verifies the archived 983-file NitroFS manifest against its actual source-ROM SHA-256 (`b39ba54e...`) and individual file hashes before treating package metadata as verified. The existing ARM9 touchscreen audits target a *different* DS/DSi ROM revision (`d42e03e6...`), so offsets cannot be carried across without separate verification. Local command: `python3 -m tools.pets.manifest_provenance /path/to/Rev0.nds research/sims3_analysis/file_manifest.csv --output pets_manifest_audit.json`. No full original ROM is currently in the connected private repository, so actual input-file verification remains outstanding.
- **Standalone package evidence check:** `tools/pets/local_package_verification.py` verifies an individually extracted original `.package` against its exact archived manifest path, byte count, and SHA-256. This avoids requiring an entire ROM for the next local step. Run `python3 -m tools.pets.local_package_verification /path/to/Animations.package research/sims3_analysis/file_manifest.csv --rom-path DATA/BACKEND/Animations.package --output pets_package_evidence.json`. The local original package must be user-authorized and is never uploaded or included in CI output. This check does not establish pet models, animation decoding or ROM hooks.
- Confirm whether the DS world can allocate/render/animate extra animal actors without disrupting Sim gameplay.
- Locate a safe runtime hook for pet actions; preserve original map and Buy/Build behavior.
- Keep any recovered original assets in the private repository or local workspace; do not commit them publicly.

## Milestone P3: in-game pet interactions (not started)
- Household adoption and pet selection controls through game-compatible menus.
- Dog/cat pathing, feeding, sleeping, play, grooming and simple autonomous behavior.
- UI that follows original HUD transitions without adding a fabricated relationships carousel page.
- Map and home-only Buy/Build transitions remain identical to the DS game.

## Milestone P4: assets and persistence (isolated host-side persistence implemented; ROM persistence not started)
- Use independently created animal art or appropriately authorized locally held assets.
- Determine native animation and texture constraints before import.
- **Implemented in source:** versioned JSON sidecar in `tools/pets/storage.py`, SHA-256 integrity validation, strict `.pets.json` destination restriction, size limit, and atomic replacement; it never reads or edits the original `.sav` file.
- **Tested in host environment:** roundtrip, tampering, malformed/version failures, atomic replacement, `.sav` isolation, symlink rejection, size limit. Run `python3 -m unittest discover -s tests -p 'test_pets_storage.py' -v`.
- **Not yet integrated:** DS/DSi runtime persistence, automatic saving, retail save compatibility, in-game save hooks, and emulator verification.
- No private ROMs or copyrighted assets in public CI.

## Milestone P5: patched ROM and melonDS verification (not started)
- Build only using a user-supplied original game dump and a patching workflow.
- Verify emulator boot, pet lifecycle, original HUD, save/reload, map transitions and Buy/Build.
- Publish source and patch instructions rather than redistributing the original ROM.

## Honest status
P1 is independent gameplay code only. P2 includes a source-only host-mode safety contract; P4 includes host-only sidecar persistence. Neither is a native ROM hook. The project does **not** yet have an integrated, playable Pets ROM, pet models, or verified original-game hooks. Actual memory/asset research is the next blocking work.
