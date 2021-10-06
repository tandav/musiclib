import pytest

from piano_scales import rhythm


@pytest.mark.parametrize('n_notes', range(1, rhythm.bar_notes + 1))
def test_n_notes(n_notes):
    assert sum(rhythm.random_rhythm(n_notes)) == n_notes


@pytest.mark.parametrize('n_notes', (-1, rhythm.bar_notes + 1))
def test_n_notes_validation(n_notes):
    with pytest.raises(ValueError):
        rhythm.random_rhythm(n_notes)


def test_rhythm_score():
    a = 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0
    b = 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    c = 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0
    assert rhythm.score(a) < rhythm.score(b)
    assert rhythm.score(c) == rhythm.score(b)
