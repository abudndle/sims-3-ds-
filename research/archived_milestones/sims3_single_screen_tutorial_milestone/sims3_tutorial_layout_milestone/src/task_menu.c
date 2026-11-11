#include "task_menu.h"
#include <stddef.h>
static void task_menu_layout(TaskMenu *m) {
 m->top_world_visible=true;
 m->top_has_hud=false;
 m->bottom_has_actions=(m->phase==TASK_CHOOSING);
 m->bottom_has_tutorial_text=(m->phase!=TASK_CLOSED);
 m->bottom_has_continue=(m->phase==TASK_DONE);
}
void task_menu_init(TaskMenu *m) {
 if(m==NULL) return;
 m->phase=TASK_CLOSED;
 m->available_actions=0;
 m->selected_action=-1;
 task_menu_layout(m);
}
bool task_menu_open(TaskMenu *m, unsigned int count) {
 if(m==NULL || m->phase!=TASK_CLOSED || count==0) return false;
 m->phase=TASK_CHOOSING;
 m->available_actions=count;
 m->selected_action=-1;
 task_menu_layout(m);
 return true;
}
bool task_menu_choose(TaskMenu *m, unsigned int action_index) {
 if(m==NULL || m->phase!=TASK_CHOOSING || action_index>=m->available_actions) return false;
 m->selected_action=(int)action_index;
 m->phase=TASK_RUNNING;
 task_menu_layout(m);
 return true;
}
void task_menu_finish(TaskMenu *m) {
 if(m==NULL || m->phase!=TASK_RUNNING) return;
 m->phase=TASK_DONE;
 task_menu_layout(m);
}
bool task_menu_continue(TaskMenu *m) {
 if(m==NULL || m->phase!=TASK_DONE) return false;
 task_menu_init(m);
 return true;
}
void task_menu_cancel(TaskMenu *m) {
 if(m==NULL || m->phase==TASK_RUNNING) return;
 task_menu_init(m);
}
