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


def test_parse(mido_midifile, midi):
    assert parse.parse_midi(mido_midifile) == midi
