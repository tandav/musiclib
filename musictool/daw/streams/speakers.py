import numpy as np

from musictool import config
from musictool.daw.streams.base import Stream


class Speakers(Stream):
    def __enter__(self):
        raise DeprecationWarning('''
        Speakers requires pyaudio which is not updated to python3.10
        pyaudio -> ffplay is in backlog and not implemented
        ''')
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
