# Sims 3 DS — dual-screen HUD layout (current requirement)

**Status:** design requirement only; the modified playable ROM is not yet complete.

## Screen arrangement

**Top screen:** display the original live 3D world. Keep the actual game rendering, Sims, objects, animations and world interactions. Do not place HUD panels, notifications or newly invented overlays on the top screen.

**Bottom touchscreen:** display the original game's HUD with all its original artwork, sizes, positions, touch controls, behaviors and information. Nothing is redesigned, scaled, or repositioned merely because it is accessed by page navigation.

- **Page 0 (default):** the same original bottom-screen HUD in exactly the position it occupied alongside the 3D gameplay.
- **Pages 1 onward:** the original HUD/information panels formerly displayed on the top screen, shown on the bottom touchscreen one at a time. Preserve their original assets, layout, content and functions.
- **Navigation:** left/right touchscreen arrows switch among the existing HUD screens, returning to Page 0 when navigating around the ends. These are the only new navigation affordances. Keep them out of the existing HUD touch targets. Do not move or reset the 3D world while changing pages.
- **Page count/order:** derive from original game screens; do not invent separate pages for features that were not originally standalone screens.

## Notifications: same original bottom-screen presentation

- Display original game notifications **on the bottom screen exactly as the game normally does**, using their original UI, placement, timing, controls and behavior.
- **Do not build a new notification overlay or persistent-popup layer**, and do not put notifications over the top-screen 3D scene.
- Do not force original transient notifications to stay until a new dismissal action; do not invent a FIFO replacement, dedicated notification page, or new popup placement.
- Job opportunities likewise use the original game's notification details and expiry/revisit behavior only if that behavior can be verified. Do not invent a new page, reopen control or expiration timer.

## Original assets and scope

Use the original authorized game assets in the private/local workspace; never put copyrighted ROMs, extracted proprietary art or unlicensed game data in the public repository or CI artifacts. Preserve the in-game visual appearance rather than drawing a new HUD.

Existing source-only modules under `tools/hud_notifications`, `tools/hud_overlay_controller`, `tools/hud_job_offers`, and `tools/hud_game_session` were developed under an earlier **persistent-overlay proposal**. **That proposal is superseded.** Those modules and any old passing tests do **not** establish correct notification behavior and **must not be integrated into the ROM as an invented overlay**. Audit original notification behavior before deciding whether any logic from them is reusable.

## Acceptance criteria

1. Real gameplay shows the original 3D world on the top screen without any HUD panels or notifications there.
2. The original bottom HUD appears on Page 0 at the same positions, scale and functionality as in the game.
3. All original top HUD panels can be reached on the bottom touchscreen using left/right arrows, while preserving their appearance and functionality.
4. Navigation only changes the active HUD screen, without interrupting the top-screen world.
5. All notifications appear and behave in their **original bottom-screen locations**, without an added overlay system.
6. Verify all active touch targets, notifications, gameplay transitions, save behavior and DS/DSi compatibility in a patched ROM running in melonDS.

No source-only layout/state model is evidence that the full ROM conversion works. Keep the executable integration milestone open until emulator verification succeeds.
