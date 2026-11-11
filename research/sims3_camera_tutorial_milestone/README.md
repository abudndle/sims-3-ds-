# The Sims 3 DS — Create-a-Sim access milestone

## Confirmed
- Launched the user-supplied VS3E US NDSi-enhanced ROM with melonDS 1.1 under Xvfb (:88).
- Reached the original title screen and profile selection via X11 touchscreen input.
- Progressed to Create-a-Sim: original 3D Sim and the Basics, Appearance, Clothes, Personality and Play UI are visible in actual emulator captures.
- Captured PNG screenshots directly from the emulator; original ROM remains unchanged.
- Set temporary keyboard mappings for X, B, A and D-Pad and sent X and B events. These events were delivered to the X11 window but no zoom effect in the gameplay tutorial was verified.

## Not confirmed
- Completion of the original in-game controls tutorial; live world gameplay with the new profile; button-controlled camera motion; new blue/green cursor system; screen swap; faster camera; any modified ROM.

## Files
- `verified_progress_montage.png`: authentic emulator frames assembled into a sheet (no generated game artwork).
- Individual source screenshots for stages.
- `advance_tutorial.py`: X11 melonDS automation to reproduce the navigation. Requires local ROM, executable and Xvfb.
- `verification.json`: local ROM and screenshot SHA-256s.

Note: Create-a-Sim appeared through the new profile path, not as proof of finishing the previous tutorial.
