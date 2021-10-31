import io

import numpy as np

from musictools.daw.streams.base import Stream


class Bytes(Stream):
    def __enter__(self):
        self.buffer = io.BytesIO()
        return self

    def __exit__(self, type, value, traceback):
        ...

    def write(self, data: np.ndarray):
        self.buffer.write(data.tobytes())
