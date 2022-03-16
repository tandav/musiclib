import pytest

from musictool import chromatic
from musictool.note import Note
from musictool.note import SpecificNote


def test_sort():
    assert ''.join(chromatic.sort_notes('bAGDCfFedBaE')) == 'CdDeEFfGaAbB'
    assert ''.join(chromatic.sort_notes(set('bAGDCfFedBaE'))) == 'CdDeEFfGaAbB'
    assert ''.join(chromatic.sort_notes('BCfGFFBDDGfbAEBeeEEf')) == 'CDDeeEEEFFfffGGAbBBB'
    assert chromatic.sort_notes((Note('A'), Note('C'), Note('b'))) == (Note('C'), Note('A'), Note('b'))
    assert chromatic.sort_notes((SpecificNote('A', 5), SpecificNote('C', 2), SpecificNote('b', 9))) == (SpecificNote('C', octave=2), SpecificNote('A', 5), SpecificNote('b', 9))

    # with start note
    assert ''.join(chromatic.sort_notes('CDEFGAB', start='G')) == 'GABCDEF'
    assert ''.join(chromatic.sort_notes('DGBFCEA', start='B')) == 'BCDEFGA'
    with pytest.raises(ValueError):
        chromatic.sort_notes('CDEFGAB', start='d')
