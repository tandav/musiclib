import contextlib
import io

import numpy as np
import pyaudio
from scipy.io import wavfile

from .. import config
from . import render
from . import vst
from .midi.parse import ParsedMidi


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
    # synth = vst.Sampler(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
    # synth = vst.Sine(adsr=vst.ADSR(attack=0.05, decay=0.3, sustain=0.1, release=0.1))
    # synth = vst.Sine(adsr=vst.ADSR(attack=0.001, decay=0.05, sustain=1, release=1))
    # synth = vst.Organ(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
    # midi = ParsedMidi.from_file(config.midi_file, vst=synth)
    # midi = ParsedMidi.from_file('drumloop.mid', vst=synth)
    # midi = ParsedMidi.from_file('bassline.mid', vst=synth)
    # midi = ParsedMidi.from_file('4-4-8.mid', vst=synth)
    # midi = ParsedMidi.from_files(['4-4-8.mid', '4-4-8-offbeat.mid'], vst=(
    midi = ParsedMidi.from_files(['drumloop.mid', 'bassline.mid'], vst=(
        vst.Sampler(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1)),
        vst.Organ(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1)),
    ))

    with audio_stream(output='speakers') as stream:
        for _ in range(4):
            # render.single(stream, midi)
            render.chunked(stream, midi)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
