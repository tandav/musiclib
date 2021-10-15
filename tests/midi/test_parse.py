import mido
import pytest

from musictools.midi.parse import MidiTrack


@pytest.mark.parametrize('midi_file', (
    'static/midi/4-4.mid',  # 1 bar
    'static/midi/3-4.mid',  # 1 bar
))
def test_time_signature(midi_file):
    m = mido.MidiFile(midi_file)
    track = MidiTrack.from_file(midi_file)
    ticks_per_bar = track.numerator * m.ticks_per_beat
    sample_rate = 44100
    beats_per_minute = 120
    seconds = mido.tick2second(ticks_per_bar, m.ticks_per_beat, mido.bpm2tempo(beats_per_minute))
    assert track.n_samples == int(sample_rate * seconds)


@pytest.mark.parametrize('midi_file', (
    'static/midi/4-4.mid',
    'static/midi/3-4.mid',
    'static/midi/weird.mid',
))
def test_note_samples(midi_file):
    track = MidiTrack.from_file(midi_file)
    for note in track.notes:
        assert note.sample_on <= note.sample_off < track.n_samples
