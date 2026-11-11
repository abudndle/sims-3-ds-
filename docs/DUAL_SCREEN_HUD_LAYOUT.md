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
- **Entering or exiting Buy/Build, original phone features or a social interaction:** use the original game's own transition, cancellation and touchscreen interaction rules. The normal lot HUD carousel must not hijack controls inside those modes.
- Verify these transitions in the patched ROM and melonDS, especially pen targets, page reset, camera ownership, and return-from-map behavior. Source-only models are insufficient to claim compatibility.

## Original three-dot HUD menu and social interaction

- The existing **three dots (`...`)** on the bottom gameplay HUD open the game's **original blue button strip**, using the original icons, order, artwork, positions and touch behavior. This is a temporary HUD-menu expansion, **not an additional page**.
- **There is no Relationships HUD page.** Do not create a Relationships carousel screen, a dedicated phone-accessed Relationships page, or extra page-navigation dots for Relationships. Any original phone features remain accessible through the original phone button without inventing a separate carousel page.
- **While talking to or socially interacting with another Sim inside a lot:** keep the live **3D social interaction visible on the top screen**. Any relationship indicator or interaction-specific UI must use the game's **original compact/contextual presentation**; **do not replace the entire bottom touchscreen with a Relationships panel**. Preserve the visible 3D scene and the original bottom-edge portrait, `...` expansion control and blue icon row when those controls normally appear, as in the user-supplied social-interaction screenshot. Do not invent a large relationship list, new full-screen view or extra carousel page.
- **When the social interaction ends, is interrupted, or is cancelled:** remove only the interaction-specific indicator and return to the prior normal bottom-screen control state, including prior HUD selection and `...` menu state. Do not perform an unnecessary screen swap or reset the top-screen camera.
- When changing the Sim being interacted with, use only the game's original contextual information for the new Sim; avoid stale indicators after interaction ends. Exact original indicator geometry and triggering must be audited from gameplay captures before ROM integration.
- **After leaving the neighborhood/map and re-entering a lot:** restore the original in-lot gameplay HUD. Tapping `...` expands the original contextual icon strip shown in the supplied map-exit screenshot—not a new screen.
- Small HUD page arrows must not interfere with the original three-dot menu or existing touch controls. Neither the three-dot menu nor contextual relationship information creates a new HUD page.

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

1. Normal gameplay shows the original 3D world on the top screen without new HUD panels or notification overlays there; the original Buy/Build modes retain their original two-screen arrangements and social interactions keep 3D on top.
2. The original bottom HUD appears on Page 0 at the same positions, scale and functionality as in the game.
3. All original top HUD panels can be reached on the bottom touchscreen using left/right arrows, while preserving their appearance and functionality.
4. Navigation only changes the active HUD screen, without interrupting the top-screen world.
5. All notifications appear and behave in their **original bottom-screen locations**, without an added overlay system.
6. Tapping the original three dots reveals the existing blue button bar without changing pages. Social interactions keep 3D conversation visible on top and original compact controls on the bottom; any relationship indication stays contextual and never occupies the whole touchscreen.
7. Buy/Build activate via original buttons only, retaining their original two-screen 3D touchscreen controls; neither is a HUD carousel page.
8. Leaving a lot restores the original neighborhood/map touchscreen input and HUD; returning to a lot restores the correct in-lot Page 0 without stale controls.
9. Confirm that Relationships is not a HUD carousel page, that the three-dot menu only expands the original button bar, and that temporary social-interaction relationship information restores the prior HUD on exit.\n10. Verify all active touch targets, notifications, gameplay transitions, save behavior and DS/DSi compatibility in a patched ROM running in melonDS.

No source-only layout/state model is evidence that the full ROM conversion works. Keep the executable integration milestone open until emulator verification succeeds.
