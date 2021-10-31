import subprocess
import sys

import numpy as np
import pytest

from musictools.daw.midi.parse import ParsedMidi
from musictools.daw.streams.bytes import Bytes
from musictools.daw.vst.sampler import Sampler
from musictools.chord import SpecificChord
from musictools.note import SpecificNote
from musictools.daw.vst.sine import Sine
from musictools.daw.vst.adsr import ADSR


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
class TestRender:
    """
    sharing common parameters/arguments
    https://stackoverflow.com/a/51747430/4204843
    """


    def test_n_samples(self, midi_file, vst):
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
        assert len(stream.to_numpy()) == track.n_samples


    def test_chunks(self, midi_file, vst):
        if (
            (midi_file == 'drumloop.mid' and not isinstance(vst, Sampler)) or
            (midi_file != 'drumloop.mid' and isinstance(vst, Sampler))
        ):
            pytest.skip('Invalid case')

        track = ParsedMidi.from_file(midi_file, vst)

        with Bytes() as single:
            single.render_single(track)

        with Bytes() as chunked:
            chunked.render_chunked(track)

        single = single.to_numpy()
        chunked = chunked.to_numpy()

        assert np.allclose(single, chunked, atol=1e-7)


def test_main():
    cmd = sys.executable, '-m', 'musictools.daw', 'video_test'
    subprocess.check_call(cmd)
    # TODO: test result with ffprobe/ffplay


def test_concat():
    # todo: use smallest possible release values on all synths to make this work
    # maybe turn off sustain and small decay
    a = SpecificChord.random().to_midi()
    b = SpecificChord.random().to_midi()
    c = SpecificChord.random().to_midi()
    d = SpecificChord.random().to_midi()
    synth = Sine(adsr=ADSR(attack=0.05, decay=0.2, sustain=0, release=1e-3), amplitude=0.02)

    with Bytes() as stream:
        stream.render_chunked(ParsedMidi(a, synth))
        stream.render_chunked(ParsedMidi(b, synth))
        stream.render_chunked(ParsedMidi(c, synth))
        stream.render_chunked(ParsedMidi(d, synth))

    z = stream.to_numpy()

    with Bytes() as sa: sa.render_chunked(ParsedMidi(a, synth))
    with Bytes() as sb: sb.render_chunked(ParsedMidi(b, synth))
    with Bytes() as sc: sc.render_chunked(ParsedMidi(c, synth))
    with Bytes() as sd: sd.render_chunked(ParsedMidi(d, synth))
    x = np.concatenate((sa.to_numpy(), sb.to_numpy(), sc.to_numpy(), sd.to_numpy()))
    assert np.allclose(x, z, atol=1e-7)

    with Bytes() as stream_concat:
        stream_concat.render_chunked(ParsedMidi(ParsedMidi.concat((a, b, c, d)), synth))

    y = stream_concat.to_numpy()
    print(x, x.shape)
    print(y, y.shape)
    assert np.allclose(x, y, atol=1e-7)
