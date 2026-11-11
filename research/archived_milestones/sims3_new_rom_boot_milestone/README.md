# The Sims 3 DS — new ROM boot verification

## Confirmed
- New ROM matches OpenTS3-DS reference MD5 `7cdf32d02eeeff592a0a4ab6bec7b5c1`.
- melonDS 1.1 Linux launched the original uploaded new ROM.
- Emulator log reported `Secure area decryption OK` and `Inserted cart with game code: VS3E`.
- Real emulator desktop captures show the EA logo at ~14 seconds and Sims 3 loading-tip screen at ~30 seconds.

## Not yet confirmed
- Main-menu navigation, an actual interactive 3D scene, save/load functionality and controller tests.
- Any top-screen conversion or faster camera mod integrated into the actual ROM.

## Contents
- `boot_14s.png`, `boot_30s.png`: actual screenshots captured in melonDS with Xvfb
- `rom_comparison.json`: metadata and hashes of uploaded ROM variants
- `melonds.log`: launch log, including secure area decryption outcome

The original uploaded ROM files were not patched or distributed in this package.
