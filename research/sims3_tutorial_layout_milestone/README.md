# The Sims 3 DS — single-screen tutorial layout milestone

**Scope:** A portable C layout compositor for the **bottom** DS touchscreen (256 × 192 px). It is not yet linked or injected into the original game's ARM9 binary.

## Completed
- Every tutorial state is mapped into bounded bottom-LCD rectangles. The top screen is reserved for the 3D world/cursor in the contract.
- The bottom-screen text, task selection, Back/Continue and information-panel arrows occupy a single page; no text or controls are assigned to the top screen.
- Four interaction choices can fit; the compositor deliberately rejects more than four, pending pagination support. Do not silently drop available actions in the eventual game.
- Continue is gated by a completion event; Build/Buy state reserves a bottom-screen 3D viewport without overlapping text.
- Touch hit-test function ignores disabled controls and out-of-bounds input.
- Tests cover all tutorial states, nonoverlap and clipping, 1–4 interactions, invalid 5-interaction layout, and Continue lock/unlock.
- Original ROM's `DATA/BACKEND/CallButton.bmp` used in the development-only sample preview. Final game must bind the original UI assets via the DS resource loader. Preview graphics otherwise use wireframe boxes and placeholder typography, **not an emulator screenshot**.

## Tests
```
for t in layout control_ui camera tutorial task_menu; do
 gcc -std=c99 -Wall -Wextra -Werror -pedantic src/*.c tests/test_${t}.c -o /tmp/sims3_${t}_test
 /tmp/sims3_${t}_test
done
```

## Blocking integration tasks
1. Recover the game's actual tutorial text draw functions, touch menu/event dispatch, and interaction completion callbacks.
2. Hook the bottom-screen compositor into the real ARM9 UI draw scheduler with original textures, fonts, dialogue, and anchors.
3. Separate world-space cursor/3D rendering from UI layers; verify top 3D LCD and touchscreen capture integration under DS hardware constraints.
4. Extend layout to paginate >4 interactions without losing available actions; integrate bottom 3D editing view.
5. Build a reversible ROM patch and verify *modified* gameplay in melonDS. No such ROM patch is shipped here.

The uploaded original ROM is untouched. This archive includes source, tests, wireframe previews, and docs, not the ROM or game assets.
