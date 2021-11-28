import subprocess
import sys

import numpy as np
import pytest

from musictools.chord import SpecificChord
from musictools.daw.midi.parse.sounds import ParsedMidi
from musictools.daw.streams.bytes import Bytes
from musictools.daw.vst.adsr import ADSR
from musictools.daw.vst.sampler import Sampler
from musictools.daw.vst.sine import Sine


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

    def is_invalid(self, midi_file, vst):
        if (
            (midi_file == 'drumloop.mid' and not isinstance(vst, Sampler)) or
            (midi_file != 'drumloop.mid' and isinstance(vst, Sampler))
        ):
            pytest.skip('Invalid case')

    def test_n_samples(self, midi_file, vst):
        """
        render 1 bar and check number of samples in the output
        """
        if self.is_invalid(midi_file, vst):
            pytest.skip('Invalid case')
        track = ParsedMidi.from_file(midi_file, vst)

        with Bytes() as stream:
            stream.render_chunked(track)
        assert len(stream.to_numpy()) == track.n_samples

    def test_chunks(self, midi_file, vst):
        if self.is_invalid(midi_file, vst):
            pytest.skip('Invalid case')

        track = ParsedMidi.from_file(midi_file, vst)

        with Bytes() as single:
            single.render_single(track)

        with Bytes() as chunked:
            chunked.render_chunked(track)

        single = single.to_numpy()
        chunked = chunked.to_numpy()

        # assert np.allclose(single, chunked, atol=1e-7)
        # assert np.allclose(single, chunked, atol=4e-8)
        # assert np.allclose(single, chunked, atol=5e-8)
        assert np.allclose(single, chunked, atol=6e-8)

    # def test_no_overlapping_notes(self, midi_file, vst):
    #     if self.is_invalid(midi_file, vst):
    #         pytest.skip('Invalid case')


def test_main():
    cmd = sys.executable, '-m', 'musictools.daw', 'video_test'
    subprocess.check_call(cmd)
    # TODO: test result with ffprobe/ffplay


def test_concat():
    a = SpecificChord.random().to_midi(n_bars=1)
    b = SpecificChord.random().to_midi(n_bars=1)
    c = SpecificChord.random().to_midi(n_bars=1)
    d = SpecificChord.random().to_midi(n_bars=1)
    vst_short_decay = Sine(adsr=ADSR(attack=0.05, decay=0.2, sustain=0, release=1e-3), amplitude=0.02)
    vst_long_decay = Sine(adsr=ADSR(attack=0.05, decay=2, sustain=0, release=1e-3), amplitude=0.02)

    with Bytes() as stream_concat:
        stream_concat.render_chunked(ParsedMidi(ParsedMidi.hstack((a, b, c, d)), vst_short_decay))
    z = stream_concat.to_numpy()

    with Bytes() as stream:
        stream.render_chunked(ParsedMidi(a, vst_short_decay))
        stream.render_chunked(ParsedMidi(b, vst_short_decay))
        stream.render_chunked(ParsedMidi(c, vst_short_decay))
        stream.render_chunked(ParsedMidi(d, vst_short_decay))
    assert np.allclose(z, stream.to_numpy())

    with Bytes() as stream:
        stream.render_chunked(ParsedMidi(a, vst_long_decay))
        stream.render_chunked(ParsedMidi(b, vst_long_decay))
        stream.render_chunked(ParsedMidi(c, vst_long_decay))
        stream.render_chunked(ParsedMidi(d, vst_long_decay))
    assert not np.allclose(z, stream.to_numpy())

    with Bytes() as sa: sa.render_chunked(ParsedMidi(a, vst_short_decay))
    with Bytes() as sb: sb.render_chunked(ParsedMidi(b, vst_short_decay))
    with Bytes() as sc: sc.render_chunked(ParsedMidi(c, vst_short_decay))
    with Bytes() as sd: sd.render_chunked(ParsedMidi(d, vst_short_decay))
    assert np.allclose(z, np.concatenate((sa.to_numpy(), sb.to_numpy(), sc.to_numpy(), sd.to_numpy())))

    with Bytes() as sa: sa.render_chunked(ParsedMidi(a, vst_long_decay))
    with Bytes() as sb: sb.render_chunked(ParsedMidi(b, vst_long_decay))
    with Bytes() as sc: sc.render_chunked(ParsedMidi(c, vst_long_decay))
    with Bytes() as sd: sd.render_chunked(ParsedMidi(d, vst_long_decay))
    assert not np.allclose(z, np.concatenate((sa.to_numpy(), sb.to_numpy(), sc.to_numpy(), sd.to_numpy())))
