# Sims 3 Pets 3DS camera matching milestone

**Finding:** The decrypted 3DS `DATA/Binaries.arc` contains `ZoomRotateCamera` (file-relative offset `0x953321`) and labels for starting angle/zoom by lot. These labels are not camera rate constants. No real speed multipliers have been verified from the supplied 3DS cartridge.

This tool calculates relative camera speeds from comparable measured DS and 3DS gameplay traces. For each axis (pan, yaw, zoom), take several samples in both games using the same input duration and compare displacement in comparable units. Calculate a median units-per-second rate to reduce noise. Input CSV columns are `game,axis,duration_seconds,delta`. `game` is `ds` or `pets3ds`; `axis` is `pan`, `yaw` or `zoom`.

Example command after collecting *actual* traces:

`python3 calibrate_camera.py my_measurements.csv --report measurements.json --header pets3ds_camera_calibration.h`

The generated header supplies Q16 scaling values for a future DS camera hook. These multipliers must be applied to verified original camera routines; the existing `camera.c` is host-side request logic, and no hook has been verified. Matching apparent camera response also depends on FOV, acceleration, zoom range, frame rate, and input sampling. At least one real gameplay test on both platforms is needed before claiming a match.

Verified: `python3 -m unittest -v test_calibrate.py`.

**Status:** calibration mechanism implemented and unit-tested; 3DS movement speed not measured; no ROM patch yet.
