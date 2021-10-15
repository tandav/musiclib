import contextlib
import io

import numpy as np
import pyaudio
from scipy.io import wavfile

from .. import config
from . import render
from . import vst
from .midi.parse import MidiTrack


@contextlib.contextmanager
def audio_stream(output):
    if output == 'buffer' or output == 'file':
        stream = io.BytesIO()
        yield stream
        if output == 'file':
            data = np.frombuffer(stream.getvalue(), dtype='float32')
            wavfile.write('out.wav', config.sample_rate, data)
    elif output == 'speakers':
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=config.sample_rate, output=True)
        yield stream
        stream.stop_stream()
        stream.close()
        p.terminate()
    else:
        raise ValueError('unknown output kind, pass one of (speakers, buffer, file)')


def main() -> int:
    # synth = vst.Sine(adsr=vst.ADSR(attack=0.05, decay=0.3, sustain=0.1, release=0.1))
    # synth = vst.Sine(adsr=vst.ADSR(attack=0.001, decay=0.05, sustain=1, release=1))
    # synth = vst.Organ(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
    synth = vst.Sampler(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
    track = MidiTrack.from_file(config.midi_file, vst=synth)

    with audio_stream(output='speakers') as stream:
        for _ in range(4):
            # render.single(stream, track)
            render.chunked(stream, track)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
