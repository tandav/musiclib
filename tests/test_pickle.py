import pickle

import pytest

from musiclib.chord import Chord
from musiclib.chord import SpecificChord
from musiclib.note import Note
from musiclib.note import SpecificNote
from musiclib.noteset import NoteSet
from musiclib.progression import Progression
from musiclib.scale import Scale


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


@pytest.mark.parametrize(
    'container', (
        {1: Note('C')},
        *iter_containers(Note('C'), Note('D')),
        *iter_containers(SpecificNote('C', 3), SpecificNote('D', 3)),
        *iter_containers(SpecificNote('C', 3), SpecificNote('C', 4)),
        *iter_containers(SpecificNote('C', 3), SpecificNote('D', 4)),
    ),
)
def test_note_container(container):
    assert container == pickle.loads(pickle.dumps(container))


a = NoteSet.from_str('fa/a')
b = NoteSet.from_str('fa/f')


@pytest.mark.parametrize(
    'noteset', (
        NoteSet.from_str('CDEFGAB/C'),
        NoteSet.from_str('CDEFGAB'),
        NoteSet.from_str('CdeFGab/e'),
        NoteSet.from_str('CEG/C'),
        a,
        *iter_containers(a, b),
    ),
)
def test_noteset(noteset):
    assert noteset == pickle.loads(pickle.dumps(noteset))


c = Chord(frozenset({Note('C'), Note('E'), Note('G')}), root=Note('C'))
d = Chord(frozenset({Note('C'), Note('E'), Note('G')}), root=Note('E'))
e = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)}), root=Note('C'))
f = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)}), root=Note('E'))


@pytest.mark.parametrize(
    'chord', (
        Chord(frozenset({Note('C'), Note('E'), Note('G')}), root=Note('C')),
        c,
        SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)})),
        e,
        f,
        *iter_containers(c, d),
        *iter_containers(e, f),
    ),
)
def test_chord(chord):
    assert chord == pickle.loads(pickle.dumps(chord))


@pytest.mark.parametrize(
    'scale', (
        Scale.from_name('C', 'major'),
        Scale.from_str('DEFGAbC/D'),
        *iter_containers(Scale.from_name('C', 'major'), Scale.from_name('D', 'major')),
    ),
)
def test_scale(scale):
    assert scale == pickle.loads(pickle.dumps(scale))


g = SpecificChord.random()
h = SpecificChord.random()
i = SpecificChord.random()
j = SpecificChord.random()
k = SpecificChord.random()


@pytest.mark.parametrize(
    'progression', (
        Progression((g, h, i, j)),
        *iter_containers(Progression((g, h, i, j)), Progression((g, h, i, k))),
    ),
)
def test_progression(progression):
    assert progression == pickle.loads(pickle.dumps(progression))
