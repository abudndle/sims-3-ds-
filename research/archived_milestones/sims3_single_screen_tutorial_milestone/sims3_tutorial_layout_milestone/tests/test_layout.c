#include "../src/layout.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 TutorialState t; TaskMenu m; TutorialLayout l; UIState ui;
 ui_init(&ui);task_menu_init(&m);tutorial_init(&t);
 for(int s=TUT_INTRO;s<TUT_FINISHED;s++){
  t.step=(TutorialStep)s;t.task_finished=false;t.completed_events=0;
  assert(tutorial_make_layout(&t,&m,&l));assert(tutorial_layout_valid(&l));
  assert(l.top_world_only);assert(tutorial_layout_hit(&l,255,191)==-1);
  bool got_3d=false;bool got_text=false;bool got_continue=false;
  for(unsigned i=0;i<l.count;i++){
   LayoutItem *p=&l.items[i];
   if(p->kind==L_PREVIEW_3D)got_3d=true;
   if(p->kind==L_TEXT)got_text=true;
   if(p->kind==L_CONTINUE){got_continue=true;assert(!p->enabled || s==TUT_INTRO);}
  }
  assert(got_3d==(s==TUT_BUILD_VIEW));assert(got_text==(s!=TUT_BUILD_VIEW));assert(got_continue);
 }
 t.step=TUT_TASK_PROGRESS;t.task_finished=true;
 assert(tutorial_make_layout(&t,&m,&l));
 int enabled_continue=0;
 for(unsigned i=0;i<l.count;i++)if(l.items[i].kind==L_CONTINUE)enabled_continue=l.items[i].enabled;
 assert(enabled_continue);
 t.step=TUT_BUILD_VIEW;t.completed_events=1;
 assert(tutorial_make_layout(&t,&m,&l));
 enabled_continue=0;
 for(unsigned i=0;i<l.count;i++)if(l.items[i].kind==L_CONTINUE)enabled_continue=l.items[i].enabled;
 assert(enabled_continue);
 t.step=TUT_TASK_PROGRESS; t.task_finished=false;
 for(unsigned actions=1;actions<=4;actions++){
  task_menu_init(&m);assert(task_menu_open(&m,actions));assert(tutorial_make_layout(&t,&m,&l));
  unsigned n=0;for(unsigned i=0;i<l.count;i++)if(l.items[i].kind==L_CHOICES)n++;
  assert(n==actions);
 }
 task_menu_init(&m);assert(task_menu_open(&m,5));assert(!tutorial_make_layout(&t,&m,&l));
 task_menu_init(&m);t.step=TUT_FINISHED;
 assert(tutorial_make_layout(&t,&m,&l));assert(l.count==0);
 puts("PASS: 256x192 bounds, nonoverlap, bottom-only tutorial widgets, all steps, 3D edit mode, completion gate, choice limits");
 return 0;
}
