import hypothesis.strategies as st
import pytest
from hypothesis import given

from musictools.note import Note
from musictools.note import SpecificNote


@pytest.mark.parametrize('i, expected', (
    (0, 'C'),
    (12, 'C'),
    (1, 'd'),
    (13, 'd'),
    (-1, 'B'),
    (-28, 'a'),
))
def test_from_i(i, expected):
    assert Note.from_i(i) == expected


@given(st.integers())
def test_specific_note_from_absolute_i(absolute_i):
    assert SpecificNote.from_absolute_i(absolute_i).absolute_i == absolute_i


@pytest.mark.parametrize('string, expected', (
    ('F1', SpecificNote('F', 1)),
    ('C4', SpecificNote('C', 4)),
    ('C10', SpecificNote('C', 10)),
    ('d456', SpecificNote('d', 456)),
    ('d-456', SpecificNote('d', -456)),
))
def test_from_str(string, expected):
    assert SpecificNote.from_str(string) == expected


@pytest.mark.asyncio
async def test_play(capsys):
    note = SpecificNote.from_absolute_i(60)
    await note.play(seconds=0.0001)
    stdout, stderr = capsys.readouterr()
    assert stdout == f'note_on note={note.absolute_i}, channel=0\nnote_off note={note.absolute_i}, channel=0\n'


@pytest.mark.parametrize('note, steps, expected', (
    (Note('C'), 4, Note('E')),
    (Note('C'), 15, Note('e')),
    (Note('B'), 2, Note('d')),
    (Note('D'), -2, Note('C')),
    (Note('d'), -2, Note('B')),
))
def test_note_add(note, steps, expected):
    assert note + steps == expected


@given(st.integers(), st.integers())
def test_specific_note_add(absolute_i, to_add):
    note = SpecificNote.from_absolute_i(absolute_i)
    assert (note + to_add).absolute_i == note.absolute_i + to_add


@pytest.mark.xfail
@given(st.integers(), st.integers())
def test_sub(absolute_i, to_sub):
    note = SpecificNote.from_absolute_i(absolute_i)
    assert (note - to_sub).absolute_i == note.absolute_i - to_sub


def test_color():
    assert not Note('C').is_black
    assert Note('d').is_black
    assert not SpecificNote('D', 1).is_black
    assert SpecificNote('f', -35).is_black
