import io

import numpy as np
import pytest

from musictools.daw import render
from musictools.daw import vst as vst_
from musictools.daw.midi.parse import ParsedMidi


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
def test_chunks(midi_file, vst):
    if (
        (midi_file == 'drumloop.mid' and not isinstance(vst, vst_.Sampler)) or
        (midi_file != 'drumloop.mid' and isinstance(vst, vst_.Sampler))
    ):
        pytest.skip('Invalid case')

    track = ParsedMidi.from_file(midi_file, vst)

    single = io.BytesIO()
    chunked = io.BytesIO()

    render.single(single, track)
    render.chunked(chunked, track)

    single = np.frombuffer(single.getvalue(), dtype='float32')
    chunked = np.frombuffer(chunked.getvalue(), dtype='float32')

    assert np.allclose(single, chunked, atol=1e-7)
