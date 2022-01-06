import io

import numpy as np

from musictool.daw.streams.base import Stream


class Bytes(Stream):
    def __enter__(self):
        self.buffer = io.BytesIO()
        return self

    def __exit__(self, type, value, traceback):
        ...

    def write(self, data: np.ndarray):
        self.buffer.write(data.tobytes())

    def to_numpy(self) -> np.ndarray:
        return np.frombuffer(self.buffer.getvalue(), dtype='float32')
