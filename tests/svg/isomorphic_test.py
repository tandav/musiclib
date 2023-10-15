import pytest
from musiclib.note import SpecificNote
from musiclib.scale import Scale
from musiclib.svg.isomorphic import Square
from musiclib.svg.isomorphic import Hex


@pytest.mark.parametrize('cls', [Square, Hex])
def test_isomorphic_plane(cls):
    kwargs = {}
    cls(**kwargs)
