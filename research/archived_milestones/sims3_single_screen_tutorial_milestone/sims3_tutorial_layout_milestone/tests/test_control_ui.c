#include "../src/control_ui.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
 UIState s; ui_init(&s);
 assert(ui_show_build_buy(&s)); assert(ui_show_go_out(&s));
 assert(ui_enter_mode(&s,MODE_BUILD)); assert(s.mode==MODE_BUILD);
 assert(ui_enter_mode(&s,MODE_BUY)); ui_exit_mode(&s);
 assert(ui_cursor_color(&s)==CURSOR_BLUE);
 s.target=TARGET_INTERACTIVE; assert(ui_cursor_color(&s)==CURSOR_GREEN);
 ui_press(&s,KEY_RIGHT|KEY_UP,0); assert(s.cursor_x==131 && s.cursor_y==93);
 for(int i=0;i<400;i++)ui_press(&s,KEY_RIGHT|KEY_DOWN,0);
 assert(s.cursor_x==255 && s.cursor_y==191);
 ui_set_location(&s,LOC_OVERWORLD);
 assert(!ui_show_build_buy(&s)); assert(ui_show_go_home(&s));
 assert(!ui_enter_mode(&s,MODE_BUILD)); assert(!ui_enter_mode(&s,MODE_BUY));
 assert(s.panel==PANEL_OVERWORLD);
 ui_set_location(&s,LOC_OTHER_LOT); assert(!ui_show_build_buy(&s));
 ui_next_panel(&s,1); assert(s.panel==PANEL_NEEDS);
 ui_set_location(&s,LOC_HOME); assert(ui_enter_mode(&s,MODE_BUILD));
 ui_set_location(&s,LOC_OVERWORLD); assert(s.mode==MODE_LIVE);
 /* Start, Select and D-Pad do not alter a game-speed state (not defined). */
 puts("PASS: 17 logical checks, screen/state module"); return 0;
}
