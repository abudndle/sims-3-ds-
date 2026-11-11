# Sims 3 DS — dual-screen HUD layout (current requirement)

**Status:** design requirement only; the modified playable ROM is not yet complete.

## Screen arrangement

**Top screen during normal gameplay:** display the original live 3D world. Keep the actual game rendering, Sims, objects, animations and world interactions. Do not place HUD panels, notifications or newly invented overlays on the top screen.

**Bottom touchscreen during normal gameplay:** display the original game's HUD with all its original artwork, sizes, positions, touch controls, behaviors and information. Nothing is redesigned, scaled, or repositioned merely because it is accessed by page navigation.

- **Page 0 (default):** the same original bottom-screen HUD in exactly the position it occupied alongside the 3D gameplay.
- **Pages 1 onward:** the original HUD/information panels formerly displayed on the top screen, shown on the bottom touchscreen one at a time. Preserve their original assets, layout, content and functions.
- **Navigation:** small left/right touchscreen arrows switch among existing HUD screens, returning to Page 0 when navigating around the ends. The arrows must occupy minimal screen space without covering original buttons or their touch targets. Do not move or reset the 3D world while changing pages.
- **Page count/order:** derive from original game screens; do not invent separate pages for features that were not originally standalone screens.

## Lot gameplay versus leaving the lot

The user-supplied six-panel mockup is the **in-lot gameplay reference**, not a replacement for the neighborhood/map interface.

- **While inside a lot:** use the same top/bottom screen pairings shown in the approved six-panel lot mockup. Page 0 is the original gameplay HUD, with the original 3D scene on top and original touchscreen gameplay controls below. Other lot HUD selections retain the corresponding original assets and screen placements shown in the reference; the added page arrows are small and do not cover existing controls.
- **When leaving the lot for the neighborhood/map:** exit the in-lot HUD/page system and **restore the original normal touchscreen controls for that outside-lot mode**. Do not leave the in-lot HUD, compact carousel navigation, or in-lot camera/touch mapping active on the map.
- **In the neighborhood/map:** preserve the original touch-to-select, navigation and contextual menu actions, including their exact original icon strip and positions; do not introduce a new touchscreen control scheme.
- **When entering a lot again:** return to its correct in-lot default view (Page 0 gameplay HUD) and restore the in-lot 3D/top and HUD/bottom pairing. The original three-dot button reveals the contextual buttons appropriate to the current game mode.
- **Entering or exiting Buy/Build or phone/Relationships:** use the original game's own transition, cancellation and touchscreen interaction rules. The normal lot HUD carousel must not hijack controls inside those modes.
- Verify these transitions in the patched ROM and melonDS, especially pen targets, page reset, camera ownership, and return-from-map behavior. Source-only models are insufficient to claim compatibility.

## Original three-dot button bar and relationship view

- Tapping the existing **three dots (`...`)** in the original gameplay HUD expands the **original blue icon/button bar**, matching the user-supplied screenshot: phone, home/build-related controls, and the game's other original buttons in their original order and artwork. The dots reveal the existing buttons; they do **not** open a newly redesigned tab system.
- **Relationships has its own original view accessed through the phone button**, rather than appearing as a permanent HUD-carousel page. Selecting the relationship function opens that view in the original game's style and retains its existing interactions.
- **While the Relationships view is open, the 3D camera/world view is temporarily displayed on the bottom screen** as requested, with the original relationship UI on the other screen as appropriate to that view. Keep this temporary screen configuration until the player explicitly cancels/exits Relationships, then restore the previous normal gameplay screen/page and the original bottom HUD/button-bar state.
- **After leaving the neighborhood/map and re-entering a lot:** return to the original in-lot gameplay HUD rather than a special map-only tab page. Tapping the original `...` control must expand the **exact original bottom-screen blue button strip shown in the user's map-exit screenshot**. This is the existing contextual row of game controls, including the phone, home and other original icons; retain the exact artwork, order, placement and touch actions. Do not construct an extra screen or duplicate those buttons as page-navigation icons. The map-exit state and button bar should follow the original game flow, not a newly invented menu.
- The separate HUD-page arrows are intentionally compact and must not replace or interfere with the original three-dot menu, phone controls or cancellation behavior.

## Original Buy and Build Mode (not carousel pages)

- The original Buy Mode and Build Mode are entered **only through their original buttons and game conditions**, including the controls revealed by the three-dot button bar. They are **not** added as pages in the HUD carousel and should not appear merely by tapping the left/right page arrows.
- Once entered, preserve the **entire original two-screen configuration**. Keep the original Household Funds, instructions and related top-screen panels on top; keep the **original interactive 3D scene, placement grid, category buttons, furniture picker, item details, confirm/cancel and other touch controls on the bottom touchscreen**.
- Preserve the original mode's original asset positions, touch behavior, gameplay state and exit/return behavior. Do not redesign the Buy or Build UI or transfer their touchscreen interactions to the top screen.

## Notifications: same original bottom-screen presentation

- Display original game notifications **on the bottom screen exactly as the game normally does**, using their original UI, placement, timing, controls and behavior.
- **Do not build a new notification overlay or persistent-popup layer**, and do not put notifications over the top-screen 3D scene.
- Do not force original transient notifications to stay until a new dismissal action; do not invent a FIFO replacement, dedicated notification page, or new popup placement.
- Job opportunities likewise use the original game's notification details and expiry/revisit behavior only if that behavior can be verified. Do not invent a new page, reopen control or expiration timer.

## Original assets and scope

Use the original authorized game assets in the private/local workspace; never put copyrighted ROMs, extracted proprietary art or unlicensed game data in the public repository or CI artifacts. Preserve the in-game visual appearance rather than drawing a new HUD.

Existing source-only modules under `tools/hud_notifications`, `tools/hud_overlay_controller`, `tools/hud_job_offers`, and `tools/hud_game_session` were developed under an earlier **persistent-overlay proposal**. **That proposal is superseded.** Those modules and any old passing tests do **not** establish correct notification behavior and **must not be integrated into the ROM as an invented overlay**. Audit original notification behavior before deciding whether any logic from them is reusable.

## Acceptance criteria

1. Normal gameplay shows the original 3D world on the top screen without new HUD panels or notification overlays there; the original Buy/Build and Relationships views retain the temporary screen arrangements described above.
2. The original bottom HUD appears on Page 0 at the same positions, scale and functionality as in the game.
3. All original top HUD panels can be reached on the bottom touchscreen using left/right arrows, while preserving their appearance and functionality.
4. Navigation only changes the active HUD screen, without interrupting the top-screen world.
5. All notifications appear and behave in their **original bottom-screen locations**, without an added overlay system.
6. Tapping the original three dots reveals the existing original blue button bar; the phone opens the distinct Relationships view with the requested temporary bottom-screen camera, and cancelling restores normal gameplay.
7. Buy/Build activate via original buttons only, retaining their original two-screen 3D touchscreen controls; neither is a HUD carousel page.
8. Leaving a lot restores the original neighborhood/map touchscreen input and HUD; returning to a lot restores the correct in-lot Page 0 without stale controls.
9. Verify all active touch targets, notifications, gameplay transitions, save behavior and DS/DSi compatibility in a patched ROM running in melonDS.

No source-only layout/state model is evidence that the full ROM conversion works. Keep the executable integration milestone open until emulator verification succeeds.
