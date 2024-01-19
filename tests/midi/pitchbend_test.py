import pytest
from musiclib.midi import pitchbend
from musiclib.midi.parse import Midi
from musiclib.midi.parse import MidiNote
from musiclib.midi.parse import MidiPitch
from musiclib.note import SpecificNote


@pytest.fixture
def pattern():
    return pitchbend.PitchPattern(time_bars=[0, 1 / 16, 1 / 16], pitch_st=[0, 2, 0])


@pytest.mark.parametrize(
    ('n_interp_points', 'expected'), [
        (0, ValueError),
        (3, ValueError),
        (
            4,
            pitchbend.PitchPattern(
                time_bars=[0.020833333333333332, 0, 0.0625, 0.0625],
                pitch_st=[0.6666666666666666, 0, 2, 0],
            ),
        ),
        (
            5,
            pitchbend.PitchPattern(
                time_bars=[0.015625, 0.03125, 0, 0.0625, 0.0625],
                pitch_st=[0.5, 1.0, 0, 2, 0],
            ),
        ),
        (
            9,
            pitchbend.PitchPattern(
                time_bars=[0.0078125, 0.015625, 0.0234375, 0.03125, 0.0390625, 0.046875, 0, 0.0625, 0.0625],
                pitch_st=[0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 0, 2, 0],
            ),
        ),
    ],
)
def test_interpolate_pattern(pattern, n_interp_points, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            pitchbend.interpolate_pattern(pattern, n_interp_points)
        return
    assert pitchbend.interpolate_pattern(pattern, n_interp_points) == expected


def test_insert_pitch_pattern(midi, pattern):
    midi.pitchbend = []
    assert pitchbend.insert_pitch_pattern(
        midi,
        time_ticks=midi.notes[1].on,
        pattern=pattern,
    ) == Midi(
        notes=[
            MidiNote(note=SpecificNote('C', 4), on=0, off=24),
            MidiNote(note=SpecificNote('E', 4), on=96, off=202),
            MidiNote(note=SpecificNote('G', 4), on=192, off=216),
        ],
        pitchbend=[
            MidiPitch(time=96, pitch=0),
            MidiPitch(time=120, pitch=8191),
            MidiPitch(time=121, pitch=0),
        ],
        ticks_per_beat=96,
    )


def test_make_notes_pitchbends(midi):
    assert pitchbend.make_notes_pitchbends(midi) == {
        MidiNote(note=SpecificNote('C', 4), on=0, off=24): [
            MidiPitch(time=0, pitch=0),
            MidiPitch(time=24, pitch=0),
        ],
        MidiNote(note=SpecificNote('E', 4), on=96, off=202): [
            MidiPitch(time=96, pitch=236),
            MidiPitch(time=192, pitch=7797),
            MidiPitch(time=197, pitch=8191),
            MidiPitch(time=202, pitch=6035),
        ],
        MidiNote(note=SpecificNote('G', 4), on=192, off=216): [
            MidiPitch(time=192, pitch=7797),
            MidiPitch(time=197, pitch=8191),
            MidiPitch(time=202, pitch=6035),
            MidiPitch(time=216, pitch=0),
        ],
    }


def test_add_pitchbend_from_overlapping_notes(midi):
    assert pitchbend.add_pitchbend_from_overlapping_notes(
        midi,
        pitchbend_semitones=3,
    ) == Midi(
        notes=[
            MidiNote(note=SpecificNote('C', 4), on=0, off=24),
            MidiNote(note=SpecificNote('G', 4), on=96, off=216),
            MidiNote(note=SpecificNote('G', 4), on=192, off=216),
        ],
        pitchbend=[
            MidiPitch(time=96, pitch=-8191),
            MidiPitch(time=192, pitch=0),
            MidiPitch(time=216, pitch=0),
        ],
        ticks_per_beat=96,
    )
