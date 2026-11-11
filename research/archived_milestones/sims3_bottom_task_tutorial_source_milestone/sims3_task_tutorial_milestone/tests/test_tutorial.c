#include "../src/tutorial.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void){
 TutorialState t; UIState ui; ui_init(&ui);tutorial_init(&t);
 assert(t.step==TUT_INTRO);
 assert((tutorial_layers(&t)&(TUT_TOP_WORLD|TUT_BOTTOM_TEXT))==(TUT_TOP_WORLD|TUT_BOTTOM_TEXT));
 assert((tutorial_layers(&t)&TUT_BOTTOM_3D_EDIT)==0);
 assert(strstr(tutorial_instruction(&t),"above")!=NULL);
 assert(!tutorial_event(&t,TUTE_INTERACT_A,&ui));
 assert(tutorial_event(&t,TUTE_CONTINUE,&ui));
 assert(t.step==TUT_MOVE_CURSOR);
 assert(!tutorial_event(&t,TUTE_CONTINUE,&ui));
 assert(tutorial_event(&t,TUTE_CURSOR_MOVED,&ui));
 assert(!tutorial_event(&t,TUTE_INTERACT_A,&ui));
 ui.target=TARGET_INTERACTIVE;
 assert(!tutorial_event(&t,TUTE_TARGET_GREEN,&ui));
 assert(tutorial_event(&t,TUTE_INTERACT_A,&ui));
 assert(t.step==TUT_TASK_PROGRESS);
 assert(!tutorial_bottom_continue_enabled(&t));
 assert(!tutorial_event(&t,TUTE_CONTINUE,&ui));
 assert((tutorial_layers(&t)&TUT_TOP_WORLD)!=0);
 assert((tutorial_layers(&t)&TUT_BOTTOM_TEXT)!=0);
 assert(tutorial_event(&t,TUTE_TASK_COMPLETED,&ui)==false);
 assert(tutorial_bottom_continue_enabled(&t));
 assert(tutorial_event(&t,TUTE_CONTINUE,&ui));
 assert(t.step==TUT_CAMERA);
 assert(tutorial_event(&t,TUTE_CAMERA_CHANGED,&ui));
 assert(tutorial_event(&t,TUTE_PANEL_ARROW,&ui));
 assert(t.step==TUT_BUILD_VIEW);
 assert((tutorial_layers(&t)&TUT_BOTTOM_3D_EDIT)!=0);
 assert((tutorial_layers(&t)&TUT_BOTTOM_TEXT)==0);
 assert(!tutorial_event(&t,TUTE_TOUCH_PLACEMENT,&ui));
 assert(ui_enter_mode(&ui,MODE_BUILD));
 assert(!tutorial_event(&t,TUTE_CONTINUE,&ui));
 assert(!tutorial_event(&t,TUTE_TOUCH_PLACEMENT,&ui));
 assert(tutorial_bottom_continue_enabled(&t));
 assert(tutorial_event(&t,TUTE_CONTINUE,&ui));
 assert(t.step==TUT_FINISHED);
 assert((tutorial_layers(&t)&TUT_BOTTOM_ACTIONS)==0);
 tutorial_init(&t);t.step=TUT_BUILD_VIEW;
 ui_set_location(&ui,LOC_OVERWORLD);
 assert(!tutorial_event(&t,TUTE_TOUCH_PLACEMENT,&ui));
 assert(!tutorial_event(&t,TUTE_CONTINUE,&ui));
 puts("PASS: tutorial bottom-UI, 3D-edit gating, cursor, sequence and home restrictions");
 return 0;
}
