import mido
import pytest

from musictools.daw.vst import ADSR
from musictools.daw.vst import Sine
from musictools.midi.parse import MidiTrack

# @pytest.fixture
# def vst():
#     return


@pytest.mark.parametrize('vst', (
    Sine(adsr=ADSR(attack=0.05, decay=0.3, sustain=0.1, release=0.001)),
    Sine(adsr=ADSR(attack=0.001, decay=0.3, sustain=1, release=1))
))
@pytest.mark.parametrize('midi_file', (
    'static/midi/4-4.mid',  # 1 bar
    'static/midi/3-4.mid',  # 1 bar
    'static/midi/4-4-kick.mid',  # 1 bar
))
def test_time_signature(midi_file, vst):
    m = mido.MidiFile(midi_file)
    track = MidiTrack.from_file(midi_file, vst)
    ticks_per_bar = track.numerator * m.ticks_per_beat
    sample_rate = 44100
    beats_per_minute = 120
    seconds = mido.tick2second(ticks_per_bar, m.ticks_per_beat, mido.bpm2tempo(beats_per_minute))
    assert track.n_samples == int(sample_rate * seconds)


@pytest.mark.parametrize('vst', (
    Sine(adsr=ADSR(attack=0.05, decay=0.3, sustain=0.1, release=0.001)),
    Sine(adsr=ADSR(attack=0.001, decay=0.3, sustain=1, release=1))
))
@pytest.mark.parametrize('midi_file', (
    'static/midi/4-4.mid',
    'static/midi/3-4.mid',
    'static/midi/weird.mid',
))
def test_note_samples(midi_file, vst):
    track = MidiTrack.from_file(midi_file, vst)
    for note in track.notes:
        assert note.sample_on <= note.sample_off < track.n_samples
        # assert note.sample_on <= note.stop_release < track.n_samples
