# Development status — 2026-11-11

## Confirmed
- Original VS3E ROM reaches household gameplay in melonDS (prior local run).
- Independent cursor/UI prototypes, original-format investigation, and static ARM7 call graphs exist locally.
- ARM7 command queues, SPI helper calls, record dispatchers and shared-memory halfword destinations have been analyzed.
- The latest public source in `tools/arm7_handler_memory/` validates five static ARM7 write paths against a user-supplied ROM.

## Not complete
- Touchscreen 12-bit X/Y coordinate extraction and ARM9 event dispatcher.
- In-game input hook and executable injection.
- Runtime-tested top-screen world-only and bottom-screen UI rework.
- Original-asset rendering inside a modified ROM.
- Real modified-ROM melonDS screenshots.

## Test command
```bash
SIMS3_DS_ROM=/path/to/your/original.nds python -m unittest discover -s tools/arm7_handler_memory -p 'test_*.py' -v
```

No private original game files are required for the public no-ROM smoke tests (ROM-dependent tests are skipped).

## Repository boundary
Public source and reports: `abudndle/sims-3-ds-`.
Private reference inventory and build coordination: `abudndle/sims-3-ds-private-`.
