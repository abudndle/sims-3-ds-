# Tutorial bottom-screen UI milestone

## Actual changes

- The included BPS modifies exactly three English tutorial strings in `DATA/LOCALIZATION/text_db_dynamic.arc` of the verified US NDSi-enhanced VS3E ROM. ROM file size and other assets remain unchanged. BPS round-trip passed.
- The `source/` folder implements a separate, portable C tutorial state controller for the future patched game: D-Pad blue cursor tutorial, green target+A, camera, bottom arrow navigation, and home-only touchscreen 3D Build/Buy editing.
- All tutorial instruction and action layers are assigned to the bottom LCD; top LCD is world+in-world cursor only. For Build/Buy the bottom LCD is assigned a 3D-edit layer and action controls. These assignments are data/state contracts, not actual Nintendo DS video-register writes.

## Not yet functional in the ROM

- The actual screen/VRAM/3D-engine switch is **not** patched.
- The actual D-Pad/A input handling, gameplay camera and tutorial event checks are **not** patched.
- Bottom 3D touchscreen editing is **not** rendered.
- The BPS is **text-only** and may teach actions that the original, unmodified game cannot perform. There is no new verified melonDS screenshot of this patch.

## Verification commands

```sh
cd source
gcc -std=c99 -Wall -Wextra -Werror -pedantic src/control_ui.c src/camera.c src/tutorial.c tests/test_tutorial.c -o /tmp/sims3_tutorial_test
/tmp/sims3_tutorial_test
```

The original ROM is not included in this distribution.
