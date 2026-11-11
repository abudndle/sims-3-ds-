#include "../src/task_menu.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
 TaskMenu m; task_menu_init(&m);
 assert(m.top_world_visible && !m.top_has_hud && !m.bottom_has_continue);
 assert(!task_menu_open(&m,0));
 assert(task_menu_open(&m,3));
 assert(m.bottom_has_actions && m.bottom_has_tutorial_text && !m.bottom_has_continue);
 assert(!task_menu_choose(&m,3));
 assert(task_menu_choose(&m,1));
 assert(m.phase==TASK_RUNNING && !m.bottom_has_continue && !m.bottom_has_actions);
 assert(!task_menu_continue(&m));
 task_menu_cancel(&m);
 assert(m.phase==TASK_RUNNING);
 task_menu_finish(&m);
 assert(m.bottom_has_continue && !m.top_has_hud);
 assert(task_menu_continue(&m));
 assert(m.phase==TASK_CLOSED);
 puts("PASS: bottom task choices, top world isolation, task completion gate");
 return 0;
}
