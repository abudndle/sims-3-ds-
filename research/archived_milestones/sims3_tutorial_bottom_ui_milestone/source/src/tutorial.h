#ifndef SIMS3_TUTORIAL_H
#define SIMS3_TUTORIAL_H
#include <stdbool.h>
#include <stdint.h>
#include "control_ui.h"
/* A portable contract for the future ROM tutorial hook, not a rendering patch. */
typedef enum {
 TUT_INTRO, TUT_MOVE_CURSOR, TUT_TARGET, TUT_CAMERA,
 TUT_SIM_PANEL, TUT_BUILD_VIEW, TUT_FINISHED
} TutorialStep;
typedef enum {
 TUTE_CONTINUE, TUTE_CURSOR_MOVED, TUTE_TARGET_GREEN,
 TUTE_INTERACT_A, TUTE_CAMERA_CHANGED, TUTE_PANEL_ARROW,
 TUTE_ENTER_BUILD, TUTE_TOUCH_PLACEMENT
} TutorialEvent;
typedef enum { TUT_BOTTOM_TEXT=1, TUT_BOTTOM_ACTIONS=2,
 TUT_BOTTOM_3D_EDIT=4, TUT_TOP_WORLD=8, TUT_TOP_CURSOR=16 } TutorialLayer;
typedef struct {
 TutorialStep step;
 unsigned int completed_events;
 bool interaction_seen;
} TutorialState;
void tutorial_init(TutorialState *t);
bool tutorial_event(TutorialState *t, TutorialEvent event, const UIState *ui);
unsigned int tutorial_layers(const TutorialState *t);
const char *tutorial_instruction(const TutorialState *t);
#endif
