#include "tutorial.h"
#include <stddef.h>
void tutorial_init(TutorialState *t) {
 if(t==NULL) return;
 t->step=TUT_INTRO; t->completed_events=0; t->interaction_seen=false;
}
unsigned int tutorial_layers(const TutorialState *t) {
 unsigned int base=TUT_TOP_WORLD|TUT_TOP_CURSOR;
 if(t==NULL || t->step==TUT_FINISHED) return base;
 /* Bottom 3D preview and bottom instructional overlay share a touch display;
    game integration must paginate them, never draw instructional HUD on top. */
 if(t->step==TUT_BUILD_VIEW) return base|TUT_BOTTOM_3D_EDIT|TUT_BOTTOM_ACTIONS;
 return base|TUT_BOTTOM_TEXT|TUT_BOTTOM_ACTIONS;
}
const char *tutorial_instruction(const TutorialState *t) {
 static const char *const lines[]={
  "The 3D world is above. Touch Continue below to begin.",
  "Move the blue 3D cursor with the D-Pad.",
  "Find a green target and press A. Actions appear below.",
  "Use camera buttons while watching the top 3D view.",
  "Touch the arrows below to browse your Sim information.",
  "At home, use the lower 3D view to place furniture.",
  ""
 };
 return t != NULL && t->step<=TUT_FINISHED ? lines[t->step] : "";
}
bool tutorial_event(TutorialState *t, TutorialEvent e, const UIState *ui) {
 if(!t || !ui || t->step==TUT_FINISHED) return false;
 bool advance=false;
 switch(t->step) {
 case TUT_INTRO: advance=e==TUTE_CONTINUE; break;
 case TUT_MOVE_CURSOR: advance=e==TUTE_CURSOR_MOVED && ui->mode==MODE_LIVE; break;
 case TUT_TARGET:
  if(e==TUTE_TARGET_GREEN && ui->target==TARGET_INTERACTIVE) t->interaction_seen=true;
  advance=e==TUTE_INTERACT_A && t->interaction_seen && ui->target==TARGET_INTERACTIVE;
  break;
 case TUT_CAMERA: advance=e==TUTE_CAMERA_CHANGED && ui->mode==MODE_LIVE; break;
 case TUT_SIM_PANEL: advance=e==TUTE_PANEL_ARROW && ui->mode==MODE_LIVE; break;
 case TUT_BUILD_VIEW:
  if(ui->location!=LOC_HOME || (ui->mode!=MODE_BUILD && ui->mode!=MODE_BUY)) return false;
  if(e==TUTE_TOUCH_PLACEMENT) t->completed_events|=1u;
  advance=(t->completed_events&1u)!=0 && e==TUTE_CONTINUE;
  break;
 case TUT_FINISHED: break;
 }
 if(advance) {t->step=(TutorialStep)((int)t->step+1);t->completed_events=0;}
 return advance;
}
