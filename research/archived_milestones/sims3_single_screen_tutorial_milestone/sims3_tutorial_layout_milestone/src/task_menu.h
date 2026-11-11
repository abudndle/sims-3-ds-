#ifndef SIMS3_TASK_MENU_H
#define SIMS3_TASK_MENU_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* View model for UI placement, not a hook into original game task lists. */
typedef enum { TASK_CLOSED, TASK_CHOOSING, TASK_RUNNING, TASK_DONE } TaskPhase;
typedef struct {
 TaskPhase phase;
 unsigned int available_actions;
 int selected_action;
 bool top_world_visible;
 bool top_has_hud;
 bool bottom_has_actions;
 bool bottom_has_tutorial_text;
 bool bottom_has_continue;
} TaskMenu;
void task_menu_init(TaskMenu *m);
bool task_menu_open(TaskMenu *m, unsigned int count);
bool task_menu_choose(TaskMenu *m, unsigned int action_index);
void task_menu_finish(TaskMenu *m);
bool task_menu_continue(TaskMenu *m);
void task_menu_cancel(TaskMenu *m);
#endif
