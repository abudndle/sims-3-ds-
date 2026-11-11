#ifndef SIMS3_GAMEPLAY_NAV_H
#define SIMS3_GAMEPLAY_NAV_H
#include "control_ui.h"
/* Logical coordinates of bottom touchscreen, not emulator window. */
#define GAMEPLAY_NAV_W 256
#define GAMEPLAY_NAV_H 192
/* Fixed Sims navigation icon in normal gameplay only. */
#define SIMS_ICON_X 4
#define SIMS_ICON_Y 4
#define SIMS_ICON_W 40
#define SIMS_ICON_H 36
/* Returns true if the Sims icon consumed this touch. Tutorial input MUST use its own route. */
bool gameplay_touch_sim_icon(UIState *state, bool tutorial_active, int touch_x, int touch_y);
/* Allows other gameplay panels to be returned to the Sim panel, but not from editing modes. */
bool gameplay_return_to_sim(UIState *state, bool tutorial_active);
#endif
