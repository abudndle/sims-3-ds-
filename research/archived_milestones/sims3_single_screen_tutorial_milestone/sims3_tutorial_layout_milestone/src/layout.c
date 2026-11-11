#include "layout.h"
#include <string.h>
static bool add(TutorialLayout *l,LayoutKind k,int x,int y,int w,int h,bool on){
 if(l->count>=LAYOUT_MAX_ITEMS || x<0 || y<0 || w<=0 || h<=0 || x+w>DS_WIDTH || y+h>DS_HEIGHT) return false;
 LayoutItem *p=&l->items[l->count++];
 p->kind=k;p->x=(short)x;p->y=(short)y;p->w=(short)w;p->h=(short)h;p->enabled=on;
 return true;
}
bool tutorial_layout_valid(const TutorialLayout *l){
 if(!l || l->count>LAYOUT_MAX_ITEMS || !l->top_world_only) return false;
 for(unsigned int i=0;i<l->count;i++){
  const LayoutItem *a=&l->items[i];
  if(a->x<0 || a->y<0 || a->w<=0 || a->h<=0 || a->x+a->w>DS_WIDTH || a->y+a->h>DS_HEIGHT) return false;
  for(unsigned int j=i+1;j<l->count;j++){
   const LayoutItem *b=&l->items[j];
   if(a->x<b->x+b->w && a->x+a->w>b->x && a->y<b->y+b->h && a->y+a->h>b->y) return false;
  }
 }
 return true;
}
bool tutorial_make_layout(const TutorialState *t,const TaskMenu *m,TutorialLayout *out){
 if(!t || !m || !out || t->step>TUT_FINISHED || m->phase>TASK_DONE) return false;
 if(m->phase==TASK_CHOOSING && (m->available_actions==0 || m->available_actions>4)) return false;
 memset(out,0,sizeof(*out));out->top_world_only=true;
 if(t->step==TUT_FINISHED) return true;
 /* Compact original-style top border and title, always on BOTTOM LCD. */
 if(!add(out,L_HEADER,4,4,248,24,true)) return false;
 if(t->step==TUT_BUILD_VIEW){
  /* Bottom-screen touch 3D editing view: text is paginated away, not overlaid. */
  if(!add(out,L_PREVIEW_3D,4,32,248,112,true) || !add(out,L_STATUS,4,148,248,12,true))return false;
  if(!add(out,L_CANCEL,4,164,92,24,true) || !add(out,L_CONTINUE,140,164,112,24,tutorial_bottom_continue_enabled(t)))return false;
 } else if(m->phase==TASK_CHOOSING){
  if(!add(out,L_TEXT,8,32,240,32,true))return false;
  /* At most four actions, rows remain >=24 px high and fully visible. */
  for(unsigned int i=0;i<m->available_actions;i++)if(!add(out,L_CHOICES,8,65+(int)i*25,240,24,true))return false;
  if(!add(out,L_CANCEL,8,168,88,20,true))return false;
 } else {
  if(!add(out,L_TEXT,8,32,240,84,true) || !add(out,L_STATUS,8,122,240,16,true))return false;
  if(t->step==TUT_SIM_PANEL){
   if(!add(out,L_NAV_LEFT,8,146,48,20,true) || !add(out,L_NAV_RIGHT,64,146,48,20,true))return false;
  }
  if(!add(out,L_CANCEL,8,168,88,20,true) || !add(out,L_CONTINUE,136,164,112,24,tutorial_bottom_continue_enabled(t) && m->phase!=TASK_RUNNING))return false;
 }
 return tutorial_layout_valid(out);
}
int tutorial_layout_hit(const TutorialLayout *l,int x,int y){
 if(!l || x<0 || y<0 || x>=DS_WIDTH || y>=DS_HEIGHT)return -1;
 for(unsigned int i=0;i<l->count;i++){
  const LayoutItem *p=&l->items[i];
  if(p->enabled && x>=p->x && x<p->x+p->w && y>=p->y && y<p->y+p->h)return (int)i;
 }
 return -1;
}
