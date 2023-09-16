import pytest
from musiclib.util.etc import increment_duplicates


@pytest.mark.parametrize(
    ('a', 'expected'), [
        ([0, 0, 0, 0, 0], [0, 1, 2, 3, 4]),
        ([0, 0, 0, 1, 2], [0, 1, 2, 3, 4]),
        ([0, 0, 0, 3, 4], [0, 1, 2, 3, 4]),
        ([0, 0, 0, 5, 6], [0, 1, 2, 5, 6]),
        ([0, 0, 0, 1, 2, 5, 6], [0, 1, 2, 3, 4, 5, 6]),
        ([0, 1, 2, 3, 4], [0, 1, 2, 3, 4]),
        ([0, 0, 1, 1, 2], [0, 1, 2, 3, 4]),
        ([0, 1, 1, 2, 2], [0, 1, 2, 3, 4]),
    ],
)
def test_increment_duplicates(a, expected):
    assert increment_duplicates(a) == expected
