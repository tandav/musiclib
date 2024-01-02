import pytest
from musiclib.util import etc


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
    assert etc.increment_duplicates(a) == expected


@pytest.mark.parametrize(
    ('intervals', 'expected'), [
        (frozenset({0, 4, 7}), (frozenset({0, 4, 7}), frozenset({0, 3, 8}), frozenset({0, 5, 9}))),
        (
            frozenset({0, 3, 6, 9}), (
                frozenset({0, 3, 6, 9}),
                frozenset({0, 3, 6, 9}),
                frozenset({0, 3, 6, 9}),
                frozenset({0, 3, 6, 9}),
            ),
        ),
        (
            frozenset({0, 2, 4, 5, 7, 9, 11}), (
                frozenset({0, 2, 4, 5, 7, 9, 11}),
                frozenset({0, 2, 3, 5, 7, 9, 10}),
                frozenset({0, 1, 3, 5, 7, 8, 10}),
                frozenset({0, 2, 4, 6, 7, 9, 11}),
                frozenset({0, 2, 4, 5, 7, 9, 10}),
                frozenset({0, 2, 3, 5, 7, 8, 10}),
                frozenset({0, 1, 3, 5, 6, 8, 10}),
            ),
        ),
    ],
)
def test_intervals_rotations(intervals, expected):
    assert etc.intervals_rotations(intervals) == expected


@pytest.mark.parametrize(
    ('mapping', 'path', 'value', 'expected'), [
        ({'a': 0}, 'a', 1, {'a': 0}),
        ({'a': 0}, 'b', 1, {'a': 0, 'b': 1}),
        ({'a': {'b': 1}}, 'a.b', 2, {'a': {'b': 1}}),
        ({'a': {'c': 2}}, 'a.b', 1, {'a': {'b': 1, 'c': 2}}),
        ({'a': {'b': 1}}, 'a.b.c', 2, KeyError),
        ({'a': {'b': {'c': 2}}}, 'a.b', 1, {'a': {'b': {'c': 2}}}),
        ({'a': {'b': {'c': 2}}}, 'a.b.c', 3, {'a': {'b': {'c': 2}}}),
        ({'a': {'b': {'c': 2}}}, 'a.b.d', 3, {'a': {'b': {'c': 2, 'd': 3}}}),
        ({'a': {'b': {'c': {'d': 3}}}}, 'a.b.c.d', 4, {'a': {'b': {'c': {'d': 3}}}}),
        ({'a': {'b': {'c': {'d': 3}}}}, 'a.b.c', 4, {'a': {'b': {'c': {'d': 3}}}}),
        ({'a': {'b': {'c': {'d': 3}}}}, 'a.b.e', 4, {'a': {'b': {'c': {'d': 3}, 'e': 4}}}),
        ({'a': {'b': {'c': {'d': 3}}}}, 'a.b.e.f', 4, {'a': {'b': {'c': {'d': 3}, 'e': {'f': 4}}}}),
        ({'a': {'b': {'c': {'d': 3}}}}, 'a.b.e.f.g', 4, {'a': {'b': {'c': {'d': 3}, 'e': {'f': {'g': 4}}}}}),
    ],
)
def test_setdefault_path(mapping, path, value, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            etc.setdefault_path(mapping, path, value)
        return
    assert etc.setdefault_path(mapping, path, value) == expected
