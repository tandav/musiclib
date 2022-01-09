import pytest

from musictool.chord import SpecificChord
from musictool.note import SpecificNote
from musictool.noteset import note_range
from musictool.scale import NoteSet
from musictool.scale import Scale
from musictool.voice_leading import checks
from musictool.voice_leading import progression


@pytest.mark.xfail(reason='deprecated')
def test_count_all_triads():
    assert len(progression.all_triads()) == 972


def test_have_parallel_interval():
    # fifths
    a = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)}))
    b = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('C', 6)}))
    c = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('F', 5), SpecificNote('A', 5)}))
    d = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('B', 5)}))
    h = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('A', 5)}))
    i = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 6)}))
    j = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('C', 7)}))

    assert checks.have_parallel_interval(a, b, 7)
    assert checks.have_parallel_interval(a, h, 7)
    assert checks.have_parallel_interval(i, j, 7)
    assert not checks.have_parallel_interval(a, c, 7)
    assert not checks.have_parallel_interval(a, d, 7)

    # octaves
    e = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('C', 6)}))
    f = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('D', 6)}))
    g = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('E', 6)}))
    assert checks.have_parallel_interval(e, f, 0)
    assert not checks.have_parallel_interval(g, f, 0)


def test_have_hidden_parallel():
    a = SpecificChord(frozenset({SpecificNote('E', 5), SpecificNote('G', 5), SpecificNote('C', 6)}))
    b = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('F', 6)}))
    c = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('G', 5), SpecificNote('C', 6)}))
    d = SpecificChord(frozenset({SpecificNote('F', 5), SpecificNote('A', 5), SpecificNote('C', 6)}))
    e = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('B', 5)}))
    f = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('D', 7)}))
    g = SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('F', 5)}))
    h = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('A', 5)}))
    i = SpecificChord(frozenset({SpecificNote('D', 5), SpecificNote('F', 5), SpecificNote('A', 6)}))
    assert checks.have_hidden_parallel(a, b, 0)
    assert checks.have_hidden_parallel(e, f, 0)
    assert checks.have_hidden_parallel(g, h, 7)
    assert checks.have_hidden_parallel(g, i, 7)
    assert not checks.have_hidden_parallel(c, b, 0)
    assert not checks.have_hidden_parallel(c, d, 0)


def test_have_voice_overlap():
    a = SpecificChord(frozenset({SpecificNote('E', 3), SpecificNote('E', 5), SpecificNote('G', 5), SpecificNote('B', 5)}))
    b = SpecificChord(frozenset({SpecificNote('A', 3), SpecificNote('C', 4), SpecificNote('E', 4), SpecificNote('A', 4)}))
    assert checks.have_voice_overlap(a, b)


@pytest.mark.parametrize('noteset, chord_str, transitions, unique_abstract', (
    (Scale.from_name('C', 'major'), 'C1_E1_G1', {'B0_E1_G1', 'C1_D1_G1', 'C1_E1_A1', 'C1_E1_F1', 'C1_F1_G1', 'D1_E1_G1'}, False),
    (NoteSet(frozenset('CDEFGAB')), 'C1_E1_G1', {'B0_E1_G1', 'C1_D1_G1', 'C1_E1_A1', 'C1_E1_F1', 'C1_F1_G1', 'D1_E1_G1'}, False),
    (NoteSet(frozenset('CDEFGAB')), 'C1_D1_E1', {'B0_D1_E1', 'C1_D1_F1'}, False),
    (NoteSet(frozenset('CDEFGAB')), 'B0_C1_D1', {'B0_C1_E1'}, False),
    (NoteSet(frozenset('CDEFGAB')), 'F1_G1_A1', {'E1_G1_A1', 'F1_G1_B1'}, False),
    (NoteSet(frozenset('CDEFGAB')), 'D1_E1_C2', {'C1_E1_C2', 'D1_E1_B1', 'D1_E1_D2', 'D1_F1_C2'}, False),
    (NoteSet(frozenset('CDEFGAB')), 'D1_E1_C2', {'D1_E1_B1', 'D1_F1_C2'}, True),
))
def test_chord_transitons(noteset, chord_str, transitions, unique_abstract):
    chord = SpecificChord.from_str(chord_str)
    note_range_ = note_range(SpecificNote('A', 0), SpecificNote('D', 2), noteset)
    assert set(map(str, progression.chord_transitons(chord, note_range_, unique_abstract))) == transitions


def test_transition_graph():
    note_range_ = note_range(SpecificNote('A', 0), SpecificNote('D', 2), NoteSet(frozenset('CDEFGAB')))
    graph = progression.transition_graph(SpecificChord.from_str('C1_E1_G1'), note_range_)
    assert len(graph) == 80
    assert sum(map(len, graph.values())) == 300


def test_transpose_uniqiue_key():
    a = SpecificChord.random()
    b = SpecificChord.random()
    c = SpecificChord.random()
    d = SpecificChord.random()

    d_ = SpecificChord(frozenset((d.notes_ascending[0] + 12,) + d.notes_ascending[1:]))

    p0 = a, b, c, d
    p1 = a, b, c, d_
    p2 = tuple(SpecificChord(frozenset(n + 12 for n in chord.notes)) for chord in p0)
    p3 = tuple(SpecificChord(frozenset(n + 1 for n in chord.notes)) for chord in p0)

    assert progression.transpose_uniqiue_key(p0) != progression.transpose_uniqiue_key(p1)
    assert progression.transpose_uniqiue_key(p0) == progression.transpose_uniqiue_key(p2)
    assert progression.transpose_uniqiue_key(p0) != progression.transpose_uniqiue_key(p3)
