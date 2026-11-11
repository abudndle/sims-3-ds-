# Sims 3 DS gameplay Sims icon navigation milestone

This milestone implements **source-level input state routing**. In normal gameplay only, tapping the 40x36 bottom-screen icon at (4,4) returns to PANEL_SIM. Tutorial input is deliberately excluded; Build/Buy and the overworld retain their specialized controls. The cursor and camera are unchanged. This project has not patched the original ARM9 executable.

## Verified

- `bash tests/run_tests.sh` compiles the C module with `-Wall -Wextra -Werror -pedantic` and runs the normal-gameplay navigation tests.
- `python build_preview.py` uses **actual user-provided Sims 3 DS DST1 sprites** extracted from the ROM to generate a 256 x 192 preview. The `button_people.dst` sprite is **an available original icon candidate**, not verified as the precise native Sims-panel icon. Preview panel backgrounds and text are placeholders. This is **not** a melonDS screenshot.
- The source assumes a 256 x 192 touchscreen coordinate system. The original in-game touch input hook, sprite renderer, and hardware display routing remain unlocated/unintegrated.
- No gameplay ROM patch or game screenshot is claimed. The original ROM is unmodified.

## Integration next

1. Locate the game's touch event dispatch and original Sims information navigation function in ARM9.
2. Confirm exact original Sims icon from the HUD resources, replacing the candidate if necessary.
3. Route bottom-screen icon touches to the original panel handler rather than merely changing the standalone state.
4. Validate using a modified ROM in melonDS and test home, away, tutorial, and Build/Buy contexts.

Distribution excludes original binary assets; regenerated screenshot previews contain an arrangement of original user-provided icon graphics.
