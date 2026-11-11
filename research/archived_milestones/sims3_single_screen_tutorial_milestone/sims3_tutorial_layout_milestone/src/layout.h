#ifndef SIMS3_LAYOUT_H
#define SIMS3_LAYOUT_H
#include <stdbool.h>
#include <stddef.h>
#include "tutorial.h"
#include "task_menu.h"
#define DS_WIDTH 256
#define DS_HEIGHT 192
#define LAYOUT_MAX_ITEMS 12
/* All rectangles are bottom-LCD pixel coordinates. No ROM drawing is performed here. */
typedef enum {L_HEADER,L_TEXT,L_CHOICES,L_STATUS,L_PREVIEW_3D,L_NAV_LEFT,L_NAV_RIGHT,L_CONTINUE,L_CANCEL} LayoutKind;
typedef struct {LayoutKind kind; short x,y,w,h; bool enabled;} LayoutItem;
typedef struct {LayoutItem items[LAYOUT_MAX_ITEMS]; unsigned int count; bool top_world_only;} TutorialLayout;
/* Return false on inconsistent states, invalid action counts or overflow. */
bool tutorial_make_layout(const TutorialState *t,const TaskMenu *menu,TutorialLayout *out);
bool tutorial_layout_valid(const TutorialLayout *layout);
/* In-display hit testing; ignores disabled buttons. -1 indicates no hit. */
int tutorial_layout_hit(const TutorialLayout *layout,int x,int y);
#endif
