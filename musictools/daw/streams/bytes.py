import io

import numpy as np

from musictools.daw.streams.base import Stream


class Bytes(Stream):
    def __enter__(self):
        self.stream = io.BytesIO()
        return self

    def write(self, data: np.ndarray):
        self.stream.write(data.tobytes())
