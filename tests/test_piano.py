import pytest

from musictool.note import Note
from musictool.note import SpecificNote
from musictool.piano import BLACK_COLOR
from musictool.piano import WHITE_COLOR
from musictool.piano import note_color


@pytest.mark.parametrize('note, color', [
    (Note('C'), WHITE_COLOR),
    (Note('d'), BLACK_COLOR),
    (SpecificNote('C', 1), WHITE_COLOR),
    (SpecificNote('d', 1), BLACK_COLOR),
])
def test_note_color(note, color):
    assert note_color(note) == color
