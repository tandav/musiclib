import contextlib
import io

import pyaudio

from .. import config
from ..midi.parse import MidiTrack
from . import render


@contextlib.contextmanager
def audio_stream(fake=False):
    if fake:
        yield io.BytesIO()
        return
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=config.sample_rate, output=True)
    yield stream
    stream.stop_stream()
    stream.close()
    p.terminate()


def main() -> int:
    track = MidiTrack.from_file(config.midi_file)

    with audio_stream(fake=False) as stream:
        render.single(stream, track)
        # render.chunked(stream, track)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
