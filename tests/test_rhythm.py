from collections import deque

import pytest

from musiclib.rhythm import Rhythm


@pytest.fixture
def example_notes():
    return 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0


@pytest.mark.parametrize('n_notes', range(1, 16 + 1))
def test_n_notes(n_notes):
    assert sum(Rhythm.random_rhythm(n_notes).notes) == n_notes


@pytest.mark.parametrize('n_notes', (-1, 16 + 1))
def test_n_notes_validation(n_notes):
    with pytest.raises(ValueError):
        Rhythm.random_rhythm(n_notes)


@pytest.mark.parametrize(
    'notes, score', [
        ((0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1), 0.3),
        ((1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1), 0.5),
        ((0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0), 12.5),
        ((1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0), 1.5833333333333333),
        ((1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0), 3),
        ((1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0), 18),
        ((0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0), 2.3333333333333335),
        ((0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1), 6.333333333333333),
        ((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1), float('inf')),
    ],
)
def test_score(notes, score):
    assert Rhythm(notes, bar_notes=16).score == score


def test_rhythm_score(example_notes):
    more_notes = 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    assert Rhythm(example_notes).score < Rhythm(more_notes).score


def test_score_rotation(example_notes):
    original_score = Rhythm(example_notes).score
    rotated_notes = deque(example_notes)
    for _ in range(len(rotated_notes)):
        rotated_notes.rotate(1)
        assert Rhythm(tuple(rotated_notes)).score == original_score


def test_has_contiguous_ones(example_notes):
    assert Rhythm(example_notes).has_contiguous_ones
    assert Rhythm((1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1)).has_contiguous_ones
    assert not Rhythm((1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)).has_contiguous_ones


def test_all_rhythms():
    assert Rhythm.all_rhythms(
        n_notes=3,
        bar_notes=6,
    ) == (
        Rhythm((0, 1, 0, 1, 0, 1), bar_notes=6),
        Rhythm((1, 0, 0, 1, 0, 1), bar_notes=6),
        Rhythm((1, 0, 1, 0, 0, 1), bar_notes=6),
        Rhythm((1, 0, 1, 0, 1, 0), bar_notes=6),
    )
