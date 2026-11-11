#include "camera.h"
#include "control_ui.h"
#include <string.h>
void camera_defaults(CameraSettings *cfg) { memset(cfg,0,sizeof(*cfg)); (void)camera_set_preset(cfg,2); }
bool camera_set_preset(CameraSettings *cfg, unsigned preset) {
    if (preset<1 || preset>3) return false;
    static const uint8_t pan[]={0,1,3,5};
    static const uint8_t turn[]={0,1,3,5};
    static const uint8_t zoom[]={0,1,2,3};
    static const uint8_t cursor[]={0,1,3,5};
    static const uint8_t fast[]={0,2,5,8};
    cfg->pan_step=pan[preset]; cfg->rotation_step=turn[preset]; cfg->zoom_step=zoom[preset];
    cfg->cursor_step=cursor[preset]; cfg->cursor_fast_step=fast[preset];
    cfg->acceleration_frames=12; cfg->held_frames=0; cfg->previous_dpad=0;
    return true;
}
CameraInput camera_get_input(const CameraSettings *cfg, uint16_t held) {
    CameraInput req={0,0,0,0};
    /* Camera navigation intent for original game's mapper; not yet hooked. */
    req.pan_x=(int16_t)(!!(held&KEY_RIGHT)-!!(held&KEY_LEFT))*cfg->pan_step;
    req.pan_y=(int16_t)(!!(held&KEY_DOWN)-!!(held&KEY_UP))*cfg->pan_step;
    req.yaw=(int16_t)(!!(held&KEY_R)-!!(held&KEY_L))*cfg->rotation_step;
    req.zoom=(int16_t)(!!(held&KEY_X)-!!(held&KEY_Y))*cfg->zoom_step;
    return req;
}
int camera_cursor_step(CameraSettings *cfg, uint16_t held) {
    uint16_t direction=held&(KEY_UP|KEY_DOWN|KEY_LEFT|KEY_RIGHT);
    if (!direction) { cfg->held_frames=0; cfg->previous_dpad=0; return 0; }
    if (direction==cfg->previous_dpad) {
        if (cfg->held_frames<255) cfg->held_frames++;
    } else { cfg->held_frames=1; cfg->previous_dpad=direction; }
    return cfg->held_frames>=cfg->acceleration_frames?cfg->cursor_fast_step:cfg->cursor_step;
}
