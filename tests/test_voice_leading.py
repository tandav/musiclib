import pytest

from piano_scales import voice_leading
from piano_scales.chord import SpecificChord
from piano_scales.note import SpecificNote


@pytest.mark.xfail(reason='deprecated')
def test_count_all_triads():
    assert len(voice_leading.all_triads()) == 972


def test_have_parallel_interval():
    # fifths
    a = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)}))
    b = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('C', 6)}))
    c = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('F', 5), SpecificNote('A', 5)}))
    d = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('B', 5)}))
    assert voice_leading.have_parallel_interval(a, b, 7)
    assert not voice_leading.have_parallel_interval(a, c, 7)
    assert not voice_leading.have_parallel_interval(a, d, 7)

    # octaves
    e = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('C', 6)}))
    f = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('D', 6)}))
    g = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('E', 6)}))
    assert voice_leading.have_parallel_interval(e, f, 12)
    assert not voice_leading.have_parallel_interval(g, f, 12)
