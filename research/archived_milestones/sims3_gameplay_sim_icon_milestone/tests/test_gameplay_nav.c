#include "../src/gameplay_nav.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 UIState s;ui_init(&s);
 assert(s.panel==PANEL_SIM);
 s.panel=PANEL_PHONE;assert(gameplay_touch_sim_icon(&s,false,20,20));assert(s.panel==PANEL_SIM);
 s.panel=PANEL_WISHES;assert(!gameplay_touch_sim_icon(&s,false,44,20));assert(s.panel==PANEL_WISHES);
 assert(!gameplay_touch_sim_icon(&s,false,20,40));assert(s.panel==PANEL_WISHES);
 assert(!gameplay_touch_sim_icon(&s,true,20,20));assert(s.panel==PANEL_WISHES);
 assert(gameplay_touch_sim_icon(&s,false,4,4));assert(s.panel==PANEL_SIM);
 s.panel=PANEL_INVENTORY; assert(gameplay_touch_sim_icon(&s,false,43,39));assert(s.panel==PANEL_SIM);
 s.panel=PANEL_SKILLS; assert(!gameplay_touch_sim_icon(&s,false,-1,30));assert(s.panel==PANEL_SKILLS);
 assert(!gameplay_touch_sim_icon(&s,false,255,191));assert(s.panel==PANEL_SKILLS);
 assert(ui_enter_mode(&s,MODE_BUY));assert(!gameplay_touch_sim_icon(&s,false,20,20));assert(s.panel==PANEL_SKILLS);
 ui_exit_mode(&s); assert(gameplay_touch_sim_icon(&s,false,20,20));assert(s.panel==PANEL_SIM);
 ui_set_location(&s,LOC_OVERWORLD);assert(s.panel==PANEL_OVERWORLD);
 assert(!gameplay_touch_sim_icon(&s,false,20,20));assert(s.panel==PANEL_OVERWORLD);
 ui_set_location(&s,LOC_HOME);s.panel=PANEL_JOBS;assert(gameplay_touch_sim_icon(&s,false,20,20));assert(s.panel==PANEL_SIM);
 puts("PASS gameplay Sims icon touchscreen routing (normal gameplay only)");return 0;
}
