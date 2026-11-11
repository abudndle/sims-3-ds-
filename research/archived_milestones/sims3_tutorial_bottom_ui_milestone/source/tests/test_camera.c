#include "../src/control_ui.h"
#include <assert.h>
#include <stdio.h>
int main(void) {
    CameraSettings c; camera_defaults(&c);
    assert(c.pan_step==3 && c.cursor_step==3);
    assert(!camera_set_preset(&c,0) && !camera_set_preset(&c,4));
    CameraInput in=camera_get_input(&c,KEY_RIGHT|KEY_UP|KEY_R|KEY_X);
    assert(in.pan_x==3 && in.pan_y==-3 && in.yaw==3 && in.zoom==2);
    assert(camera_cursor_step(&c,KEY_RIGHT)==3);
    for(int i=0;i<11;i++) (void)camera_cursor_step(&c,KEY_RIGHT);
    assert(camera_cursor_step(&c,KEY_RIGHT)==5);
    assert(camera_cursor_step(&c,0)==0);
    assert(camera_cursor_step(&c,KEY_LEFT)==3);
    assert(camera_set_preset(&c,1)); assert(c.pan_step==1);
    assert(camera_set_preset(&c,3)); assert(c.pan_step==5 && c.cursor_fast_step==8);
    UIState s; ui_init(&s);
    ui_press(&s,KEY_LEFT,0); assert(s.cursor_x==125);
    ui_set_location(&s,LOC_OVERWORLD);
    assert(s.mode==MODE_LIVE);
    puts("PASS: camera speed presets, directional requests, acceleration and UI movement");
    return 0;
}
