import mido
import pytest
from musiclib.midi import parse


@pytest.mark.parametrize(
    ('type_', 'message', 'expected'), [
        ('on', mido.Message('note_on', note=60, velocity=1), True),
        ('on', mido.Message('note_on', note=60, velocity=0), False),
        ('on', mido.Message('note_off', note=60, velocity=1), False),
    ],
)
def test_is_note(type_, message, expected):
    assert parse.is_note(type_, message) == expected


def test_parse(midi):
    midi0 = mido.MidiFile(
        type=0, ticks_per_beat=96, tracks=[
            mido.MidiTrack([
                mido.Message('note_on', note=60, time=0),
                mido.Message('note_off', note=60, time=24),
                mido.Message('pitchwheel', pitch=0, time=69),
                mido.Message('note_on', note=64, time=3),
                mido.Message('note_on', note=67, time=96),
                mido.Message('pitchwheel', pitch=8191, time=5),
                mido.Message('note_off', note=64, time=5),
                mido.Message('pitchwheel', pitch=0, time=14),
                mido.Message('note_off', note=67, time=0),
            ]),
        ],
    )
    assert parse.parse_midi(midi0) == midi
