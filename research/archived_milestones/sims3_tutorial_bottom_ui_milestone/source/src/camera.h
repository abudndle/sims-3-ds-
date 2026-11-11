#ifndef SIMS3_CAMERA_H
#define SIMS3_CAMERA_H
#include <stdint.h>
#include <stdbool.h>
/* Requests for the original game camera, NOT direct hardware registers. */
typedef struct {
    int16_t pan_x, pan_y;   /* signed camera translation request */
    int16_t yaw;            /* signed rotation request */
    int16_t zoom;           /* signed zoom request */
} CameraInput;
typedef struct {
    uint8_t pan_step;       /* arbitrary units/frame, default 3 */
    uint8_t rotation_step;  /* arbitrary units/frame, default 3 */
    uint8_t zoom_step;      /* arbitrary units/frame, default 2 */
    uint8_t cursor_step;    /* screen pixels/frame, default 3 */
    uint8_t cursor_fast_step; /* screen pixels/frame after held >= 12 frames */
    uint8_t acceleration_frames;
    uint8_t held_frames;
    uint16_t previous_dpad;
} CameraSettings;
void camera_defaults(CameraSettings *cfg);
/* 1=normal, 2=faster default, 3=fastest. Affects intent, not sim time. */
bool camera_set_preset(CameraSettings *cfg, unsigned preset);
CameraInput camera_get_input(const CameraSettings *cfg, uint16_t held);
int camera_cursor_step(CameraSettings *cfg, uint16_t held);
#endif
