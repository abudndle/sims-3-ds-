"""Decode ARM7-to-ARM9 touchscreen word without inventing pixel calibration.

Bits 0..11 and 12..23 carry filtered ADC X/Y; bit 24 is pen contact,
bits 25..26 sample/retry status, bits 27..31 preserved opaque state.
"""
from dataclasses import dataclass

X_MASK = 0xFFF
Y_SHIFT = 12
PEN_BIT = 1 << 24
STATUS_SHIFT = 25
OPAQUE_SHIFT = 27


@dataclass(frozen=True)
class TouchSample:
    raw_x: int
    raw_y: int
    pen_down: bool
    sample_status: int
    opaque_high: int

    @property
    def x_fallback(self) -> bool:
        return bool(self.sample_status & 1)

    @property
    def y_fallback(self) -> bool:
        return bool(self.sample_status & 2)


def unpack(word: int) -> TouchSample:
    """Unpack unsigned word without assigning screen coordinates."""
    if type(word) is not int or not 0 <= word <= 0xFFFFFFFF:
        raise ValueError('word must be an unsigned 32-bit integer')
    return TouchSample(
        raw_x=word & X_MASK,
        raw_y=(word >> Y_SHIFT) & X_MASK,
        pen_down=bool(word & PEN_BIT),
        sample_status=(word >> STATUS_SHIFT) & 3,
        opaque_high=(word >> OPAQUE_SHIFT) & 31,
    )


def pack(sample: TouchSample) -> int:
    """Reassemble word while retaining undefined upper five bits."""
    if not isinstance(sample, TouchSample):
        raise TypeError('expected TouchSample')
    fields = (sample.raw_x, sample.raw_y, sample.sample_status, sample.opaque_high)
    if any(type(value) is not int for value in fields):
        raise ValueError('all numeric fields must be plain integers')
    if not (0 <= sample.raw_x <= 4095 and 0 <= sample.raw_y <= 4095):
        raise ValueError('raw ADC coordinates must be 12-bit values')
    if not 0 <= sample.sample_status <= 3:
        raise ValueError('sample status must be 0..3')
    if not 0 <= sample.opaque_high <= 31:
        raise ValueError('opaque bits must be 0..31')
    if type(sample.pen_down) is not bool:
        raise ValueError('pen_down must be boolean')
    return (sample.raw_x | (sample.raw_y << Y_SHIFT)
            | (int(sample.pen_down) << 24)
            | (sample.sample_status << STATUS_SHIFT)
            | (sample.opaque_high << OPAQUE_SHIFT))


def requires_recheck(sample: TouchSample) -> bool:
    """Conservative flag: pen-up or ambiguous status=3 requires recheck.

    Status=3 may mean both-axis fallback or contact-probe retry.
    Other statuses are not guaranteed valid gameplay input.
    """
    if not isinstance(sample, TouchSample):
        raise TypeError('expected TouchSample')
    return not sample.pen_down or sample.sample_status == 3
