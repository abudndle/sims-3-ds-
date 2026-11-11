# Sims 3 DS — final dual-screen HUD layout specification

Status: **approved design requirement; not yet integrated into a playable ROM**.

## Top screen — gameplay view
- Retain the game's original live 3D scene as the top-screen gameplay view.
- Remove the original informational HUD overlays from the top screen and move their functions to pages on the bottom screen. Do **not** remove Sims, furniture, world rendering, animations or interactions from the 3D scene.
- Do not place the bottom-screen controls HUD over the top-screen scene.

## Bottom screen — touch-accessible HUD carousel
- **Page 0 (default):** the game's **original bottom-screen HUD associated with the 3D gameplay view**, preserving its existing graphics, buttons and functionality. It remains displayed on the bottom touchscreen, not on the top screen.
- **Pages 1 onward:** the game's **original top-screen Sim-information HUD panels** (Sim overview/info, needs/mood, wishes, inventory, relationships, skills, career/job, phone and any other panels as established by original-game asset/behavior audit). Relocate each original information panel to bottom-screen display. Preserve its own contents, graphical style, states and interactions; do not replace it with a generic reimagined HUD.
- Show **left and right page arrows on every bottom-screen page**, including page 0. These navigate among available HUD pages. Page 0 is first when gameplay starts or the HUD is reset. Navigation wraps from the last page to page 0 and backwards from page 0 to the last page.
- Make page arrows the primary HUD navigation; do not require button shortcuts. Keep original HUD touch targets functional. Layout/placement must prevent arrow targets from blocking important existing controls.
- Page switching changes only the bottom-screen HUD; the top-screen 3D scene continues rendering without disruption, camera reset or world reload.
- Opening an in-game subpanel returns to the same page unless the original workflow requires navigation. Gameplay transitions can explicitly reset page selection to page 0.
- The order and number of information pages must be confirmed from original game UI assets/screens. The navigation code accepts an ordered list rather than assuming every listed category is a separate actual panel.

## Bottom-screen notifications — persistent overlay on the active page
- Job opportunities, skill gains/level-ups, career updates, and all original gameplay notifications appear in a **layer on top of the currently selected bottom-screen HUD page** (including Page 0 and every Sim-information page). Notifications are **not a separate HUD page**.
- The notification remains visible **until the player explicitly clears, acknowledges, or resolves it**. Do not automatically dismiss it after a timeout merely because its original presentation was temporary.
- Navigating with the left/right HUD arrows changes the page **beneath** the overlay; the notification persists above the newly selected page until cleared. Do not reset the underlying page when a notification arrives or is dismissed.
- Maintain a FIFO queue so multiple notifications do not replace or lose one another; clearing the currently displayed notification reveals the next one.
- Preserve original message text, icons, actions and audio where feasible after original-game audit. Reserve reachable navigation and dismissal touch regions; ensure important HUD controls can still be accessed or are restored after dismissal.
- Keep the top-screen 3D view unobstructed by all notification messages.

## Implementation sequencing
1. Inventory exact original top/bottom HUD screen assets and functions and verify target positions.
2. Implement page selection and arrow touch regions independent of proprietary assets; add unit tests.
3. Integrate preserved original bottom HUD on Page 0, original top information HUD pages from Page 1 onward, and a persistent notifications overlay above the active bottom-screen page.
4. Keep 3D scene top-screen-only and remove top informational overlays.
5. Validate every page's controls, switching during active gameplay, and save continuity in melonDS. Produce real captures from a modified ROM, not concept art.

## Acceptance checks
- A fresh gameplay session shows original 3D gameplay on top and the former bottom 3D-control HUD as page 0 **on bottom**.
- Both navigation arrows are visible and work by touch on all pages.
- Every original top-screen Sim-information HUD is reachable on the bottom touchscreen in its original style and retains full behavior.
- Switching pages never moves or interrupts the 3D scene on top.
- No Sim information is permanently lost in the conversion.
- Job opportunities, skill gains/level-ups and other gameplay alerts display **over the active bottom HUD page until cleared**; changing pages never dismisses the overlay, and notifications have no dedicated page.
- Test on both DS and DSi emulation; keep proprietary ROM/artwork in the private/local workspace.

This specification supersedes earlier proposals to replace original HUDs wholesale or show permanent information overlays on the top screen.
