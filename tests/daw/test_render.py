import subprocess
import sys

import numpy as np
import pytest

from musictools.daw.midi.parse import ParsedMidi
from musictools.daw.streams.bytes import Bytes
from musictools.daw.vst.sampler import Sampler


@pytest.mark.parametrize('midi_file', (
    'overlap.mid',
    'bassline.mid',
    '4-4-8.mid',
    '3-4-16.mid',
    '4-4-16.mid',
    'chord.mid',
    'weird.mid',
    'drumloop.mid',
))
def test_n_samples(midi_file, vst):
    """
    render 1 bar and check number of samples in the output
    """
    if (
        (midi_file == 'drumloop.mid' and not isinstance(vst, Sampler)) or
        (midi_file != 'drumloop.mid' and isinstance(vst, Sampler))
    ):
        pytest.skip('Invalid case')
    track = ParsedMidi.from_file(midi_file, vst)

    with Bytes() as stream:
        stream.render_chunked(track)
    assert len(np.frombuffer(stream.buffer.getvalue(), dtype='float32')) == track.n_samples


def test_main():
    cmd = sys.executable, '-m', 'musictools.daw', 'video_test'
    subprocess.check_call(cmd)
