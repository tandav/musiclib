import pickle

import pytest

from musictool.chord import Chord
from musictool.chord import SpecificChord
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.scale import Scale


@pytest.mark.parametrize('note', (Note('C'), SpecificNote('C', 3)))
def test_note(note):
    pickle.dumps(note)


@pytest.mark.parametrize('chord', (
    Chord(frozenset({Note('C'), Note('E'), Note('G')}), root=Note('C')),
    SpecificChord(frozenset({SpecificNote('C', 5), SpecificNote('E', 5), SpecificNote('G', 5)})),
))
def test_chord(chord):
    pickle.dumps(chord)


@pytest.mark.parametrize('scale', (
    Scale.from_name('C', 'major'),
))
def test_scale(scale):
    pickle.dumps(scale)
