# The Sims 3 DS — control and UI rework

Independent source, tests and research for a Nintendo DS/DSi-enhanced Sims 3 control/UI mod.

## Goal
- Top screen: original 3D world, unobstructed by menus and HUD.
- Bottom touchscreen: original-style Sim info, mood, needs, wishes, inventory, jobs, relationships, skills, phone, tutorial and interactions.
- D-pad world-space cursor, A interact, B cancel, camera behavior studied against The Sims 3: Pets 3DS.
- Home-only Build/Buy menus, bottom-screen house editing, existing game saves preserved.

## Actual progress
- Unmodified Sims 3 DS has previously reached household gameplay in melonDS.
- Independent source prototypes for control logic and bottom-screen UI exist, but are not integrated into the retail ROM.
- Static ARM7/ARM9 analysis mapped command queues, SPI callers and shared-memory references.
- Touchscreen coordinate decoding and ARM9 gameplay UI hook are not yet established.
- **No verified playable control-rework ROM exists yet.**

## Organization and reproducibility
- Public: independently authored scripts, tests, reports and source.
- Private: restricted reference inventories, protected build configuration, and user-controlled original game assets. Private repository: https://github.com/abudndle/sims-3-ds-private-
- Original working DS ROM reference SHA-256: `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`
- Provide your own legally obtained game dump locally when running analyzers. No original ROM or extracted game assets in public git history or CI artifacts.

## Warning
Do not conflate static research findings with a runtime-tested modification. Game files are proprietary and must not be redistributed without appropriate permission.
