#ifndef SIMS3_CONTROL_UI_H
#define SIMS3_CONTROL_UI_H
#include <stdint.h>
#include <stdbool.h>
/* Platform-independent UI transition logic. NOT YET PATCHED INTO GAME. */
typedef enum { LOC_HOME, LOC_OVERWORLD, LOC_OTHER_LOT } Location;
typedef enum { MODE_LIVE, MODE_BUILD, MODE_BUY } Mode;
typedef enum { PANEL_SIM, PANEL_NEEDS, PANEL_MOODLETS, PANEL_WISHES,
 PANEL_INVENTORY, PANEL_PHONE, PANEL_JOBS, PANEL_RELATIONSHIPS,
 PANEL_SKILLS, PANEL_OVERWORLD } Panel;
typedef enum { TARGET_NONE, TARGET_INTERACTIVE } Target;
typedef enum { CURSOR_BLUE, CURSOR_GREEN } CursorColor;
typedef struct { Location location; Mode mode; Panel panel; Target target;
 bool highlights_sims, highlights_lots, highlights_known;
 bool birds_eye; int cursor_x, cursor_y; } UIState;
enum { KEY_A=1<<0, KEY_B=1<<1, KEY_SELECT=1<<2, KEY_START=1<<3,
 KEY_RIGHT=1<<4, KEY_LEFT=1<<5, KEY_UP=1<<6, KEY_DOWN=1<<7,
 KEY_R=1<<8, KEY_L=1<<9, KEY_X=1<<10, KEY_Y=1<<11 };
void ui_init(UIState *s);
bool ui_set_location(UIState *s, Location location);
bool ui_enter_mode(UIState *s, Mode mode);
void ui_exit_mode(UIState *s);
void ui_next_panel(UIState *s, int direction);
void ui_press(UIState *s, uint16_t held, uint16_t pressed);
CursorColor ui_cursor_color(const UIState *s);
bool ui_show_build_buy(const UIState *s);
bool ui_show_go_home(const UIState *s);
bool ui_show_go_out(const UIState *s);
#endif
