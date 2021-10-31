import numpy as np

from musictools import config
from musictools.daw.streams.base import Stream


class Speakers(Stream):
    def __enter__(self):
        import pyaudio
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
