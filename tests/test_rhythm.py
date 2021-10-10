from collections import deque

import pytest

from piano_scales import rhythm


@pytest.fixture
def example():
    return 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0


@pytest.mark.parametrize('n_notes', range(1, rhythm.bar_notes + 1))
def test_n_notes(n_notes):
    assert sum(rhythm.random_rhythm(n_notes)) == n_notes


@pytest.mark.parametrize('n_notes', (-1, rhythm.bar_notes + 1))
def test_n_notes_validation(n_notes):
    with pytest.raises(ValueError):
        rhythm.random_rhythm(n_notes)


def test_rhythm_score(example):
    b = 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    assert rhythm.score(example) < rhythm.score(b)


def test_score_rotation(example):
    score = rhythm.score(example)
    example = deque(example)
    for _ in range(len(example)):
        example.rotate(1)
        assert rhythm.score(example) == score


def test_has_contiguous_ones():
    assert rhythm.has_contiguous_ones((1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0))
    assert rhythm.has_contiguous_ones((1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1))
    assert not rhythm.has_contiguous_ones((1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0))
