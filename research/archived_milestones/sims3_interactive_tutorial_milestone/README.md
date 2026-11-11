# The Sims 3 DS: Interactive Tutorial Boot Milestone

## Verified
- Tested unmodified user-supplied `Sims 3, The (USA) (En,Fr,Es) (NDSi Enhanced).nds` in Linux melonDS 1.1 under Xvfb.
- Valid game title screen with animated 3D background.
- Sent real X11 virtual touchscreen click to the prompt, reached `Welcome to Beacon Bay` and profile selection.
- Selected first profile and accepted the introductory tour.
- Entered in-game 3D tutorial scene (Sim visible outdoors and house visible).
- Advanced tutorial to an original **Controls** panel which says: "The X Button zooms you in and the B Button zooms you out. Try using the X Button now."
- Screenshots are real melonDS screen captures, not mockups.

## Not yet verified
- Completing the tutorial, new live gameplay, keyboard input via X/B, profile save/load, or installed control mod.
- No dual-screen interface swap, faster camera, cursor mod, or built ROM patch has been integrated.

## Hardware interpretation
The original game has zoom assigned to X/B during the tutorial. Proposed DS control rework should account for this; earlier X/Y mappings were only conceptual.

## Steps reproduced
1. Start melonDS with uploaded reference ROM in DS mode under Xvfb.
2. Touch `(120, 398)` in the 256px-wide emulator window (top screen begins y=22, bottom begins y≈214).
3. Select first save slot `(56,301)` and confirm `(220,353)`.
4. Accept tutorial `(110,325)`.
5. Touch blue progress arrow `(210,345)`.
These coordinates correspond to this session's 1x layout and may change with window scale.

## Assets and distribution
Only screenshots and metadata are included; no ROM or copyrighted raw game assets.
