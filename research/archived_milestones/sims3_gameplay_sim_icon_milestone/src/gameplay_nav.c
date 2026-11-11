#include "gameplay_nav.h"
bool gameplay_return_to_sim(UIState *s, bool tutorial_active){
 if(!s || tutorial_active || s->mode!=MODE_LIVE) return false;
 /* In the overworld, the location controls remain primary until a lot is entered. */
 if(s->location==LOC_OVERWORLD) return false;
 s->panel=PANEL_SIM;
 return true;
}
bool gameplay_touch_sim_icon(UIState *s, bool tutorial_active, int x, int y){
 if(x<SIMS_ICON_X || x>=SIMS_ICON_X+SIMS_ICON_W ||
    y<SIMS_ICON_Y || y>=SIMS_ICON_Y+SIMS_ICON_H) return false;
 return gameplay_return_to_sim(s,tutorial_active);
}
