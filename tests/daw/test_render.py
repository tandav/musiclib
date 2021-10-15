import io

import numpy as np
import pytest

from musictools.daw import render
from musictools.daw import vst as vst_
from musictools.daw.midi.parse import MidiTrack


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
        (midi_file == 'drumloop.mid' and not isinstance(vst, vst_.Sampler)) or
        (midi_file != 'drumloop.mid' and isinstance(vst, vst_.Sampler))
    ):
        pytest.skip('Invalid case')
    track = MidiTrack.from_file(midi_file, vst)
    stream = io.BytesIO()
    render.single(stream, track)
    assert len(np.frombuffer(stream.getvalue(), dtype='float32')) == track.n_samples
