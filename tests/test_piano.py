import pytest

from musictool import config
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.piano import note_color


@pytest.mark.parametrize('note, color', [
    (Note('C'), config.WHITE_PALE),
    (Note('d'), config.BLACK_PALE),
    (SpecificNote('C', 1), config.WHITE_PALE),
    (SpecificNote('d', 1), config.BLACK_PALE),
])
def test_note_color(note, color):
    assert note_color(note) == color
