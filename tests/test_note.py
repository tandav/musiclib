import hypothesis.strategies as st
from hypothesis import given

from piano_scales.note import SpecificNote


@given(st.integers())
def test_specific_note_from_absolute_i(absolute_i):
    assert SpecificNote.from_absolute_i(absolute_i).absolute_i == absolute_i
