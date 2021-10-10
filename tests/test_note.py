import hypothesis.strategies as st
import pytest
from hypothesis import given

from musictools.note import SpecificNote


@given(st.integers())
def test_specific_note_from_absolute_i(absolute_i):
    assert SpecificNote.from_absolute_i(absolute_i).absolute_i == absolute_i


@pytest.mark.asyncio
async def test_play(capsys):
    note = SpecificNote.from_absolute_i(60)
    await note.play(seconds=0.0001)
    stdout, stderr = capsys.readouterr()
    assert stdout == f'note_on note={note.absolute_i}, channel=0\nnote_off note={note.absolute_i}, channel=0\n'
