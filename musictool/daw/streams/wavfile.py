import io

import numpy as np

from musictool import config
from musictool.daw.streams.base import Stream
from musictool.util import wavfile
from musictool.util.signal import float32_to_int16


class WavFile(Stream):
    def __init__(self, path, dtype='int16'):
        super().__init__()

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
