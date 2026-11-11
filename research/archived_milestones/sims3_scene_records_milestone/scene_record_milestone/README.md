# Sims 3 DS — Scene record and developer-testbed milestone

## Verified against original supplied ROM
- Game code: VS3E; ROM SHA-256: `b39ba54eb61f0bc05094a362e297f963bf5a08fc05c4cd0f3dbc8dfe45abd6de`.
- Identified **35** `DATA/BACKEND/LOTS/TERRAIN/*.dsm` scene files. The first observed `.dst` reference has a byte immediately before its name matching the number of such names in every scene (**35/35**). Consecutive names occur at a consistent 64-byte stride (**all 62 named slots across 35 scenes**). This is a validated name-slot pattern, not a full scene-data decoder.
- Found **5** files in the development/test-named `DATA/LODTESTBED/` directory: `Blue Box.dsm`, `Green Box.dsm`, `Red Box.dsm`, `Yellow Box.dsm` and `boxes.dst`.
- Each emitted file was bounds-checked and SHA-256 verified against the existing NitroFS manifest before scanning.

## How to reproduce

```bash
python3 scan_scene_records.py '/path/to/The Sims 3.nds' file_manifest.csv --out scene_reports
```

Outputs: `terrain_scenes.csv`, `terrain_references.csv`, `development_testbed.csv`, `summary.json`. `test_log.json` shows the test output for the uploaded ROM. No proprietary game payloads or ROM copies are included in this toolkit.

## Caution
`LODTESTBED` strongly suggests internal testing assets, but does not establish that they are *unreachable* in gameplay. Do not label these as confirmed cut content without loading/cross-reference evidence. There is no restored-content patch yet. The original ROM was not changed.

## Next technical target
Investigate pointers/scene-loader and resource indexing in ARM9; see whether `LODTESTBED` paths appear in code or data references, whether these scenes can be loaded safely, and only then build a reversible patch for a confirmed inaccessible asset or scene.
