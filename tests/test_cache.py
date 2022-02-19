from musictool.chord import Chord
from musictool.chord import SpecificChord
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.noteset import NoteSet
from musictool.scale import Scale


def test_note():
    assert Note('A') is Note('A')
    assert Note('A') is not Note('B')


def test_specific_note():
    assert SpecificNote('C', 1) is SpecificNote('C', 1)
    assert SpecificNote('C', 1) is not SpecificNote('C', 2)
    assert SpecificNote('C', 1) is SpecificNote(Note('C'), 1)


def test_noteset():
    assert NoteSet(frozenset('CDe')) is NoteSet(frozenset('CDe'))
    assert NoteSet(frozenset('CDe'), root='C') is NoteSet(frozenset('CDe'), root='C')
    assert NoteSet(frozenset('CDe'), root='C') is NoteSet(frozenset('CDe'), root=Note('C'))
    assert NoteSet(frozenset('CDe'), root='C') is not NoteSet(frozenset('CDe'), root='D')


def test_scale():
    assert Scale(frozenset('Cde'), root='C') is Scale(frozenset('Cde'), root='C')
    assert Scale(frozenset('Cde'), root='C') is Scale(frozenset('Cde'), root=Note('C'))
    assert Scale(frozenset('Cde'), root='C') is not Scale(frozenset('CDe'), root=Note('C'))
    assert Scale(frozenset('Cde'), root='C') is not Scale(frozenset('Cde'), root=Note('d'))
    assert Scale.from_name('C', 'major') is Scale.from_name('C', 'major')
    assert Scale.from_name('C', 'major') is not Scale.from_name('D', 'major')
    assert Scale.from_name('C', 'major') is Scale.from_name(Note('C'), 'major')


def test_chord():
    assert Chord(frozenset('CEG')) is Chord(frozenset('CEG'))
    assert Chord(frozenset('CEG'), root='C') is Chord(frozenset('CEG'), root='C')
    assert Chord(frozenset('CEG'), root='C') is not Chord(frozenset('CeG'), root=Note('C'))
    assert Chord(frozenset('CEG'), root='C') is not Chord(frozenset('CEG'), root=Note('E'))
    assert Chord.from_name('C', 'major') is Chord.from_name('C', 'major')
    assert Chord.from_name('C', 'major') is not Chord.from_name('D', 'major')
    assert Chord.from_name('C', 'major') is Chord.from_name(Note('C'), 'major')


def test_specific_chord():
    a = SpecificNote('C', 5)
    b = SpecificNote('E', 5)
    c = SpecificNote('G', 5)
    d = SpecificNote('C', 6)
    assert SpecificChord(frozenset({a, b, c})) is SpecificChord(frozenset({a, b, c}))
    assert SpecificChord(frozenset({a, b, c}), root='C') is SpecificChord(frozenset({a, b, c}), root=Note('C'))
    assert SpecificChord(frozenset({a, b, c}), root='C') is not SpecificChord(frozenset({a, b, d}), root=Note('C'))
    assert SpecificChord(frozenset({a, b, c}), root='C') is not SpecificChord(frozenset({a, b, c}), root=Note('E'))
    assert SpecificChord.from_str('C1_E1_G1/C') is SpecificChord.from_str('C1_E1_G1/C')
    assert SpecificChord.from_str('C1_E1_G1/C') is not SpecificChord.from_str('C1_E1_G1/E')
    assert SpecificChord.from_str('C1_E1_G1/C') is not SpecificChord.from_str('C1_e1_G1/C')
