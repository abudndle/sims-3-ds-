#include "control_ui.h"
#include <string.h>
void ui_init(UIState *s) { memset(s, 0, sizeof(*s)); s->location=LOC_HOME;
 s->panel=PANEL_SIM; s->highlights_sims=true; s->highlights_lots=true;
 s->highlights_known=true; s->cursor_x=128; s->cursor_y=96; }
bool ui_set_location(UIState *s, Location location) {
 if(location>LOC_OTHER_LOT) return false;
 s->location=location;
 if(location!=LOC_HOME) { s->mode=MODE_LIVE; s->birds_eye=false; }
 if(location==LOC_OVERWORLD) s->panel=PANEL_OVERWORLD;
 else if(s->panel==PANEL_OVERWORLD) s->panel=PANEL_SIM;
 return true;
}
bool ui_enter_mode(UIState *s, Mode mode) {
 if(mode>MODE_BUY) return false;
 if(mode!=MODE_LIVE && s->location!=LOC_HOME) return false;
 s->mode=mode; return true;
}
void ui_exit_mode(UIState *s) { s->mode=MODE_LIVE; s->birds_eye=false; }
void ui_next_panel(UIState *s, int direction) {
 /* Actual UI uses touchscreen arrow icons; this is only panel state logic. */
 if(s->mode!=MODE_LIVE) return;
 if(s->location==LOC_OVERWORLD) { s->panel=PANEL_OVERWORLD; return; }
 int n=(int)PANEL_OVERWORLD, p=((int)s->panel + n)%n;
 s->panel=(Panel)((p+(direction>=0?1:n-1))%n);
}
void ui_press(UIState *s, uint16_t held, uint16_t pressed) {
 /* Physical buttons control the selector, never game speed. */
 if(s->mode!=MODE_LIVE) return;
 s->cursor_x+=!!(held&KEY_RIGHT)-!!(held&KEY_LEFT);
 s->cursor_y+=!!(held&KEY_DOWN)-!!(held&KEY_UP);
 if(s->cursor_x<0)s->cursor_x=0;
 if(s->cursor_x>255)s->cursor_x=255;
 if(s->cursor_y<0)s->cursor_y=0;
 if(s->cursor_y>191)s->cursor_y=191;
 (void)pressed; /* A/B action wiring requires original game function hooks. */
}
CursorColor ui_cursor_color(const UIState *s) {
 return s->target==TARGET_INTERACTIVE ? CURSOR_GREEN : CURSOR_BLUE;
}
bool ui_show_build_buy(const UIState *s) { return s->location==LOC_HOME; }
bool ui_show_go_home(const UIState *s) { return s->location==LOC_OVERWORLD; }
bool ui_show_go_out(const UIState *s) { return s->location==LOC_HOME && s->mode==MODE_LIVE; }
