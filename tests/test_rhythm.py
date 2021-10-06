import pytest

from piano_scales import rhythm


@pytest.mark.parametrize('n_notes', range(1, rhythm.bar_notes + 1))
def test_n_notes(n_notes):
    assert sum(rhythm.random_rhythm(n_notes)) == n_notes


@pytest.mark.parametrize('n_notes', (-1, rhythm.bar_notes + 1))
def test_n_notes_validation(n_notes):
    with pytest.raises(ValueError):
        rhythm.random_rhythm(n_notes)
