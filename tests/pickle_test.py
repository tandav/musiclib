import pickle

import pytest

from musiclib.interval import AbstractInterval
from musiclib.intervalset import IntervalSet
from musiclib.note import Note
from musiclib.note import SpecificNote
from musiclib.noteset import NoteSet
from musiclib.noteset import SpecificNoteSet
from musiclib.progression import Progression
from musiclib.scale import Scale


@pytest.mark.parametrize('note', [Note('C'), SpecificNote('C', 3)])
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
    'container', [
        {1: Note('C')},
        *iter_containers(Note('C'), Note('D')),
        *iter_containers(SpecificNote('C', 3), SpecificNote('D', 3)),
        *iter_containers(SpecificNote('C', 3), SpecificNote('C', 4)),
        *iter_containers(SpecificNote('C', 3), SpecificNote('D', 4)),
    ],
)
def test_note_container(container):
    assert container == pickle.loads(pickle.dumps(container))


a = NoteSet.from_str('fa')
b = NoteSet.from_str('Ba')


@pytest.mark.parametrize(
    'noteset', [
        NoteSet.from_str('CDEFGAB'),
        NoteSet.from_str('CdeFGab'),
        NoteSet.from_str('CEG'),
        a,
        *iter_containers(a, b),
    ],
)
def test_noteset(noteset):
    assert noteset == pickle.loads(pickle.dumps(noteset))


e = SpecificNoteSet(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)}))
f = SpecificNoteSet(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)}))


@pytest.mark.parametrize(
    'sns', [
        SpecificNoteSet(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)})),
        e,
        f,
        *iter_containers(e, f),
    ],
)
def test_sns(sns):
    assert sns == pickle.loads(pickle.dumps(sns))


@pytest.mark.parametrize(
    'abstractinterval', [
        AbstractInterval(0),
        AbstractInterval(10),
        AbstractInterval.from_str('A'),
        *iter_containers(AbstractInterval(0), AbstractInterval(10)),
    ],
)
def test_abstract_interval(abstractinterval):
    assert abstractinterval == pickle.loads(pickle.dumps(abstractinterval))


@pytest.mark.parametrize(
    'intervalset', [
        IntervalSet.from_name('major'),
        *iter_containers(IntervalSet.from_name('major'), IntervalSet.from_name('minor')),
    ],
)
def test_intervalset(intervalset):
    assert intervalset == pickle.loads(pickle.dumps(intervalset))


@pytest.mark.parametrize(
    'scale', [
        Scale.from_name('C', 'major'),
        Scale.from_str('DEFGAbC/D'),
        *iter_containers(Scale.from_name('C', 'major'), Scale.from_name('D', 'major')),
    ],
)
def test_scale(scale):
    assert scale == pickle.loads(pickle.dumps(scale))


g = SpecificNoteSet.random()
h = SpecificNoteSet.random()
i = SpecificNoteSet.random()
j = SpecificNoteSet.random()
k = SpecificNoteSet.random()


@pytest.mark.parametrize(
    'progression', [
        Progression((g, h, i, j)),
        *iter_containers(Progression((g, h, i, j)), Progression((g, h, i, k))),
    ],
)
def test_progression(progression):
    assert progression == pickle.loads(pickle.dumps(progression))
