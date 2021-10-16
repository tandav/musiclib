import abc
import io

import numpy as np
import pyaudio
from scipy.io import wavfile

from .. import config


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


class Stream(abc.ABC):
    @abc.abstractmethod
    def write(self, data: np.ndarray):
        """data.dtype must be float32"""
        ...


class Bytes(Stream):
    def __enter__(self):
        return io.BytesIO()


class WavFile(Stream):
    def __init__(self, path, dtype='int16'):
        if dtype not in {'float32', 'int16'}:
            raise ValueError('unsupported wave format')
        self.path = path
        self.dtype = dtype

    def __enter__(self):
        # kinda workarounds, maybe there are a better ways
        # self.arrays = []
        self.stream = io.BytesIO()
        return self

    def write(self, data: np.ndarray):
        # self.arrays.append(data)
        self.stream.write(data.tobytes())

    def __exit__(self, type, value, traceback):
        # data = np.concatenate(self.arrays) # TODO: not works, fix it
        # assert data.dtype == 'float32'
        data = np.frombuffer(self.stream.getvalue(), dtype='float32')
        if self.dtype == 'int16':
            data = float32_to_int16(data)
        wavfile.write(self.path, config.sample_rate, data)


class Speakers(Stream):
    def __enter__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=pyaudio.paFloat32, channels=1, rate=config.sample_rate, output=True)
        return self
        # return self.stream

    def __exit__(self, type, value, traceback):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    def write(self, data: np.ndarray):
        self.stream.write(data.tobytes())


class YouTube(Stream): pass
