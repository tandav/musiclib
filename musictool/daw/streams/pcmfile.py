import numpy as np

from musictool.daw.streams.base import Stream
from musictool.util.signal import float32_to_int16


class PCM16File(Stream):
    """
    pcm_s16le PCM signed 16-bit little-endian
    """

    def __init__(self, path):
        super().__init__()
        self.path = open(path, 'wb')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.path.close()

    def write(self, data: np.ndarray):
        self.path.write(float32_to_int16(data).tobytes())
        # float32_to_int16(data).tofile(self.path)
