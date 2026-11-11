# Sims 3 DS — ARM9 Camera & Input Reference Milestone

## Evidence from original uploaded VS3E ROM

- Exact reference MD5: `7cdf32d02eeeff592a0a4ab6bec7b5c1`.
- SHA-256: `d42e03e66bc2cf447b74038ed0c766573cd70db23eeba69ec22c3df29a93ec8a`.
- ARM9 image begins at ROM offset `0x4000` and is loaded at `0x02004000`; size `0x17C6C0` bytes.
- Read-only scan found **27 ASCII camera/input-related strings with 27 aligned 32-bit literal pointers**.
- Some concrete pointers from the ARM9 image:

| Text | String virtual address | Reference address |
| --- | --- | --- |
| Debug Camera | `0x0217434A` | `0x02044390` |
| Restore Camera | `0x02174357` | `0x02044394` |
| Reset Zoom | `0x021744E0` | `0x0217457C` |
| Zoom %d | `0x021744EB` | `0x0204441C` |
| Disable Player Zoom | `0x021744F3` | `0x020444AC` |
| Enable Player Zoom | `0x02174507` | `0x020444B0` |
| Map View Camera Menu | `0x021736BD` | `0x02042FF4` |

**Important:** These references may be debug UI/menu records. They are *not* identified camera-update function entry points. String-pointer existence alone cannot establish which feature is active in release gameplay or where to inject code safely. No ROM patch was applied.

## Run reproducibly

```sh
python3 scan_camera.py '/path/to/your/VS3E.nds' --output camera_report.json
```

Exports `camera_report.json` and `camera_report.csv` containing addresses and reference counts. This toolkit does not copy game binaries or assets. It is specific to the reference ROM listed above.

## Existing control module checks (independent)

Two native host test executables built with `-std=c99 -Wall -Wextra -Werror -pedantic`. Both passed: UI rules (17 checks) and camera-speed/pan/rotation/zoom intent tests. These tests **do not verify actual camera motion inside the game**.

## Next technical work

1. Disassemble ARM9 around the literal references and identify menu table record structures / genuine call sites.
2. Locate original gameplay camera update handler using branch or runtime tracing, rather than inferring it from debug labels.
3. Confirm zoom/camera behavior in a controlled melonDS gameplay capture.
4. Integrate a small conditional hook only after addresses and calling conventions are validated; package a reversible patch and test it in melonDS.

No playable control-conversion ROM was produced in this milestone.
