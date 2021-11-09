import numpy as np


def float32_to_int16(signal: np.ndarray, dtype='int16'):
    """Convert floating point signal with a range from -1 to 1 to PCM.
    Any signal values outside the interval [-1.0, 1.0) are clipped.
    No dithering is used.
    Note that there are different possibilities for scaling floating
    point numbers to PCM numbers, this function implements just one of
    them.  For an overview of alternatives see
    http://blog.bjornroche.com/2009/12/int-float-int-its-jungle-out-there.html
    """
    if signal.dtype.kind != 'f':
        raise TypeError("'signal' must be a float array")
    dtype = np.dtype(dtype)
    if dtype.kind not in 'iu':
        raise TypeError("'dtype' must be an integer type")

    i = np.iinfo(dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (signal * abs_max + offset).clip(i.min, i.max).astype(dtype)


def normalize(signal: np.ndarray, a: float = -1, b: float = 1):
    # solving system of linear equations one can find the coefficients
    A = np.min(signal)
    B = np.max(signal)
    C = (a - b) / (A - B)
    k = (C * A - a) / C
    return (signal - k) * C
