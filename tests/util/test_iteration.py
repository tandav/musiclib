import itertools
from collections import Counter

import pytest

from musictool.util.iteration import sequence_builder


@pytest.fixture
def is_even():
    return lambda x: x % 2 == 0


@pytest.fixture
def even_odd_interchange(is_even):
    return lambda prev, curr: is_even(prev) ^ is_even(curr)


@pytest.fixture
def options():
    return 0, 1, 2, 3


def test_length(options, is_even):
    assert all(len(cycle) == 5 for cycle in sequence_builder(5, options, i_constraints={0: is_even}))


def test_first_constraint(options, is_even):
    assert all(is_even(cycle[0]) for cycle in sequence_builder(5, options, i_constraints={0: is_even}))


def test_prev_curr(options, even_odd_interchange):
    for cycle in sequence_builder(5, options, curr_prev_constraint=even_odd_interchange, loop=True):
        assert even_odd_interchange(cycle[-1], cycle[0])
        for prev, curr in itertools.pairwise(cycle):
            assert even_odd_interchange(prev, curr)


def test_prefix(options):
    prefix = options[:2]
    for cycle in sequence_builder(5, options, prefix=prefix):
        assert all(a == b for a, b in zip(prefix, cycle))


def test_unique(options):
    assert all(len(cycle) == len(set(cycle)) for cycle in sequence_builder(5, options, unique_key=lambda x: x))
    assert any(len(cycle) != len(set(cycle)) for cycle in sequence_builder(5, options))


def test_candidate_constraint():
    def candidate_constraint(c): return Counter(c)['A'] < 3
    for seq in sequence_builder(
        n=4,
        options='AB',
        candidate_constraint=candidate_constraint,
    ):
        assert candidate_constraint(seq)


def test_options_kind_callable():
    assert list(sequence_builder(3, options=lambda x: [x + 1], options_kind='callable_from_curr', prefix=[0])) == [(0, 1, 2)]
    assert list(sequence_builder(3, options=lambda x: [x + 1, x * 10], options_kind='callable_from_curr', prefix=[0])) == [(0, 1, 2), (0, 1, 10), (0, 0, 1), (0, 0, 0)]
