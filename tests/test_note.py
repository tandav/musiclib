import os

import hypothesis.strategies as st
import pytest
from hypothesis import given

from musictool.note import Note
from musictool.note import SpecificNote
from musictool.note import str_to_note


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


def test_note_exists():
    with pytest.raises(KeyError):
        Note('Q')
    with pytest.raises(KeyError):
        Note('1')


def test_str_equals():
    assert Note('C') == 'C'
    assert SpecificNote.from_str('C1') == 'C1'


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

    lines = [
        f'note_on note={note.absolute_i}, channel=0\n',
        f'note_off note={note.absolute_i}, channel=0\n',
    ]

    if 'MIDI_DEVICE' not in os.environ:
        lines = ['MIDI_DEVICE not found | ' + line for line in lines]

    assert stdout == ''.join(lines)


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


def test_str_to_note():
    assert str_to_note('C') == Note('C')
    assert str_to_note('C1') == SpecificNote('C', 1)
    assert str_to_note('C13') == SpecificNote('C', 13)
    assert str_to_note('C-13') == SpecificNote('C', -13)
    assert str_to_note('C1334') == SpecificNote('C', 1334)

    with pytest.raises(KeyError):
        str_to_note('Q')

    with pytest.raises(ValueError):
        str_to_note('CQ')
