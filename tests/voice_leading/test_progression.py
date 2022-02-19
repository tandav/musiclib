import pytest

from musictool.chord import SpecificChord
from musictool.progression import Progression


@pytest.fixture
def four_chords():
    a = SpecificChord.random()
    b = SpecificChord.random()
    c = SpecificChord.random()
    d = SpecificChord.random()
    return a, b, c, d


@pytest.fixture
def progression4():
    a = SpecificChord.from_str('C1_E1_G1')
    b = SpecificChord.from_str('D1_F1_A1')
    c = SpecificChord.from_str('E1_G1_B1')
    d = SpecificChord.from_str('F1_A1_C2')
    return Progression([a, b, c, d])


def test_validation():
    with pytest.raises(TypeError):
        Progression([0, 1, 2])
    Progression([SpecificChord.random(), SpecificChord.random()])


def test_list_like(four_chords):
    a, b, c, d = four_chords
    p = Progression([a, b, c])
    assert len(p) == 3
    assert p[0] == a
    assert p == [a, b, c]
    e = [a, b, c, d]
    assert p + [d] == e
    p.append(d)
    assert p == e
    assert Progression(x for x in [a, b, c, d]) == [a, b, c, d]


def test_all(progression4):
    def check(x, y): return x[0] < y[0]
    assert progression4.all([check])
    assert progression4.all_not([lambda x, y: not check(x, y)])


def test_distance(progression4):
    assert progression4.distance == 30


def test_transpose_unique_key(four_chords):
    a, b, c, d = four_chords
    d_ = SpecificChord(frozenset((d.notes_ascending[0] + 12,) + d.notes_ascending[1:]))
    p0 = Progression([a, b, c, d])
    p1 = Progression([a, b, c, d_])
    p2 = Progression(SpecificChord(frozenset(n + 12 for n in chord.notes)) for chord in p0)
    p3 = Progression(SpecificChord(frozenset(n + 1 for n in chord.notes)) for chord in p0)
    assert p0.transpose_unique_key() != p1.transpose_unique_key()
    assert p0.transpose_unique_key() == p2.transpose_unique_key()
    assert p0.transpose_unique_key() != p3.transpose_unique_key()
    assert p0.transpose_unique_key(origin_name=False) == p3.transpose_unique_key(origin_name=False)


def test_transpose_to_origin(progression4):
    p = Progression([
        SpecificChord.from_str('C0_E0_G0'),
        SpecificChord.from_str('C0_e0_G0'),
        SpecificChord.from_str('C0_e0_G0'),
        SpecificChord.from_str('C0_E0_G0'),
    ])
    assert progression4.transpose() == p
