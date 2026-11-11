# Sims 3 DS — bottom-screen task tutorial milestone

## User requirement
During tutorials, the top Nintendo DS display contains **only the 3D game world and its in-world blue/green cursor**. Former top-screen tutorial text and interaction-choice menus move to the bottom touchscreen. After a task is completed in the top-screen world, the **Continue** button appears on the bottom touchscreen and must be pressed to progress. No Continue action is accepted before task completion.

## Implemented here (portable C, tested)
- `src/tutorial.[ch]`: a new task-running tutorial step after the interactive-target step, with `TUTE_TASK_COMPLETED` completion signal and explicit bottom-screen Continue gate.
- `src/task_menu.[ch]`: bottom-screen interaction choices, in-progress state, completion, and Continue behavior. It preserves top-world-only layout flags throughout.
- Existing camera and UI state modules retained from the prior source milestone.
- All four host-side C tests pass with GCC `-Wall -Wextra -Werror -pedantic`.

## Still not in the real DS ROM
These routines are **not hooked** into the Sims 3 DS ARM9 executable. The necessary live event sources (task completion, interaction list, game tutorial state), actual dual-screen render routing, and original DS UI sprite data bindings still require reverse engineering and ROM patching. No modified ROM or melonDS capture of the new feature is claimed. The original DS game remains unchanged.

## Build and test
```
cd sims3_task_tutorial_milestone
for test in test_control_ui test_camera test_tutorial; do
  gcc -std=c99 -Wall -Wextra -Werror -pedantic src/control_ui.c src/camera.c src/tutorial.c tests/$test.c -o /tmp/$test
  /tmp/$test
done
gcc -std=c99 -Wall -Wextra -Werror -pedantic src/task_menu.c tests/test_task_menu.c -o /tmp/test_task_menu
/tmp/test_task_menu
```

## Event wiring required for future ROM integration
1. The original DS object's selectable interactions -> `task_menu_open(count)` with original labels/icons supplied by the game.
2. Bottom-screen user selects action -> `task_menu_choose(index)`; dispatch selection into the original interaction engine.
3. The original task-completion callback -> `task_menu_finish()` and `tutorial_event(..., TUTE_TASK_COMPLETED, ...)`.
4. Bottom-screen Continue button -> `task_menu_continue()` and `tutorial_event(..., TUTE_CONTINUE, ...)`.
5. Screen composer draws gameplay 3D and world cursor on the top LCD. Text, task menu, Continue button and all HUD live on the bottom LCD.
6. For Build/Buy, bottom interactive 3D view requires a separate pipeline/engine validation, not covered by this milestone.
