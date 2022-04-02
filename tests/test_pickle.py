import pickle

import pytest

from musictool.chord import Chord
from musictool.chord import SpecificChord
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.noteset import NoteSet
from musictool.progression import Progression
from musictool.scale import Scale


@pytest.mark.parametrize('note', (Note('C'), SpecificNote('C', 3)))
def test_note(note):
    assert note == pickle.loads(pickle.dumps(note))


def iter_containers(a, b):
    yield from (
        (a, b),
        [a, b],
        {a, b},
        frozenset({a, b}),
        {a: 1, b: 1},
        {1: a, 2: b},
    )


@pytest.mark.parametrize('container', (
    {1: Note('C')},
    *iter_containers(Note('C'), Note('D')),
    *iter_containers(SpecificNote('C', 3), SpecificNote('D', 3)),
    *iter_containers(SpecificNote('C', 3), SpecificNote('C', 4)),
    *iter_containers(SpecificNote('C', 3), SpecificNote('D', 4)),
))
def test_note_container(container):
    assert container == pickle.loads(pickle.dumps(container))


a = NoteSet(frozenset('fa'), root='a')
b = NoteSet(frozenset('fa'), root='f')


@pytest.mark.parametrize('noteset', (
    NoteSet(frozenset('CDEFGAB'), root='C'),
    NoteSet(frozenset('CDEFGAB')),
    NoteSet(frozenset('CdeFGab'), root='e'),
    NoteSet(frozenset('CEG'), root='C'),
    a,
    *iter_containers(a, b),
))
def test_noteset(noteset):
    assert noteset == pickle.loads(pickle.dumps(noteset))


a = Chord(frozenset({Note('C'), Note('E'), Note('G')}), root='C')
b = Chord(frozenset({Note('C'), Note('E'), Note('G')}), root='E')
c = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)}), root=Note('C'))
d = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)}), root='E')


@pytest.mark.parametrize('chord', (
    Chord(frozenset({Note('C'), Note('E'), Note('G')}), root=Note('C')),
    a,
    SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)})),
    c,
    d,
    *iter_containers(a, b),
    *iter_containers(c, d),
))
def test_chord(chord):
    assert chord == pickle.loads(pickle.dumps(chord))


@pytest.mark.parametrize('scale', (
    Scale.from_name('C', 'major'),
    Scale(frozenset('DEFGAbC'), root='D'),
    *iter_containers(Scale.from_name('C', 'major'), Scale.from_name('D', 'major')),
))
def test_scale(scale):
    assert scale == pickle.loads(pickle.dumps(scale))


a = SpecificChord.random()
b = SpecificChord.random()
c = SpecificChord.random()
d = SpecificChord.random()
e = SpecificChord.random()


@pytest.mark.parametrize('progression', (
    Progression((a, b, c, d)),
    *iter_containers(Progression((a, b, c, d)), Progression((a, b, c, e)))
))
def test_progression(progression):
    assert progression == pickle.loads(pickle.dumps(progression))
