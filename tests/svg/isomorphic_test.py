import pytest
from musiclib.note import SpecificNote
from musiclib.scale import Scale
from musiclib.svg.isomorphic import Square
from musiclib.svg.isomorphic import Hex


@pytest.mark.parametrize('scale', [None, Scale.from_name('f', 'dorian')])
@pytest.mark.parametrize('origin_note', [None, SpecificNote('a', 2)])
@pytest.mark.parametrize('cls', [Square, Hex])
def test_isomorphic_plane(scale, origin_note, cls):
    kwargs = {}
    if scale is not None:
        kwargs['scale'] = scale
    if origin_note is not None:
        kwargs['origin_note'] = origin_note
    cls(**kwargs)
