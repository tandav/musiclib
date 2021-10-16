import mido
import pytest

from musictools import config
from musictools.daw.midi.parse import ParsedMidi


@pytest.mark.parametrize('midi_file', (
    '4-4-16.mid',  # 1 bar
    '3-4-16.mid',  # 1 bar
    '4-4-kick.mid',  # 1 bar
))
def test_time_signature(midi_file, vst):
    m = mido.MidiFile(config.midi_folder + midi_file)
    track = ParsedMidi.from_file(midi_file, vst)
    ticks_per_bar = track.numerator * m.ticks_per_beat
    sample_rate = 44100
    beats_per_minute = 120
    seconds = mido.tick2second(ticks_per_bar, m.ticks_per_beat, mido.bpm2tempo(beats_per_minute))
    assert track.n_samples == int(sample_rate * seconds)


@pytest.mark.parametrize('midi_file', (
    '4-4-16.mid',
    '3-4-16.mid',
    'weird.mid',
))
def test_note_samples(midi_file, vst):
    track = ParsedMidi.from_file(midi_file, vst)
    for note in track.notes:
        assert note.sample_on <= note.sample_off < track.n_samples
        # assert note.sample_on <= note.stop_release < track.n_samples
