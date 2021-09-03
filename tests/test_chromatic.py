from piano_scales import chromatic
from piano_scales.note import Note
from piano_scales.note import SpecificNote


def test_abstract_take():
    assert ''.join(note.name for note in chromatic.iterate(start_note='C', take_n=28)) == 'CdDeEFfGaAbBCdDeEFfGaAbBCdDe'
    assert ''.join(note.name for note in chromatic.iterate(start_note='A', take_n=28)) == 'AbBCdDeEFfGaAbBCdDeEFfGaAbBC'
    assert tuple(chromatic.iterate(start_note=Note('C'), take_n=2)) == (Note('C'), Note('d'))
    assert tuple(chromatic.iterate(start_note=Note('B'), take_n=2)) == (Note('B'), Note('C'))


def test_specific_take():
    assert tuple(chromatic.iterate(start_note=SpecificNote('B', octave=8), take_n=2)) == (SpecificNote('B', octave=8), SpecificNote('C', octave=9))


def test_nth():
    assert chromatic.nth('C', 7) == Note('G')
    assert chromatic.nth(SpecificNote('G', octave=8), 7) == SpecificNote('D', octave=9)


def test_sort():
    assert ''.join(chromatic.sort_notes('bAGDCfFedBaE')) == 'CdDeEFfGaAbB'
    assert ''.join(chromatic.sort_notes('BCfGFFBDDGfbAEBeeEEf')) == 'CDDeeEEEFFfffGGAbBBB'
    assert chromatic.sort_notes((Note('A'), Note('C'), Note('b'))) == [Note('C'), Note('A'), Note('b')]
    assert chromatic.sort_notes((SpecificNote('A', 5), SpecificNote('C', 2), SpecificNote('b', 9))) == [SpecificNote('C', octave=2), SpecificNote('A', 5), SpecificNote('b', 9)]
