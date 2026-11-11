# The Sims 3 DS: control/UI rework - first source milestone

This is original, portable C *logic*, not a patched or bootable The Sims 3 DS ROM.
The source is provided to make a real implementation possible without claiming the original game's address mappings are known.

## Tested now
- D-Pad cursor position clamped to DS resolution (256x192), no speed control
- Blue cursor normally; green for a target identified as interactive
- Build/Buy only when the selected Sim is home
- Go Out only while live at home; Go Home only in overworld
- Overworld panel routing; touch-arrow panel navigation state
- Three independent overworld highlight flags

## Still necessary for an actual DS game mod
1. Reverse-engineer VS3E screen/VRAM display routing and original interaction + touch logic.
2. Map original 3D scene projection/raycast; cursor coordinates are not world coordinates yet.
3. Locate and extract exact original Build/Buy, Phone, Wishes, Moodlets, Needs and status sprites.
4. Hook input without overriding core game actions; implement A/B and camera actions.
5. Reroute top gameplay 3D renderer, bottom 2D HUD. Original DS 3D engine has hardware constraints for touch 3D Build/Buy; validate feasibility.
6. Patch ROM using discovered hooks, test real hardware and melonDS. No original ROM/assets are bundled.

## Host verification
`gcc -std=c99 -Wall -Wextra -Werror -pedantic src/control_ui.c tests/test_control_ui.c -o test_ui && ./test_ui`

## Original ROM baseline
Game code VS3E, 134217728 bytes. SHA256: b39ba54eb61f0bc05094a362e297f963bf5a08fc05c4cd0f3dbc8dfe45abd6de

## Original catalog resource paths identified in uploaded ROM
- DATA/BACKEND/CATALOG/addwalls.dst
- DATA/BACKEND/CATALOG/doors.dst
- DATA/BACKEND/CATALOG/floor.dst
- DATA/BACKEND/CATALOG/functioncomfort.dst
- DATA/BACKEND/CATALOG/functionlighting.dst

These are data records, not necessarily the corresponding UI icon textures.
