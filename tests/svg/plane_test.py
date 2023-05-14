import pytest
from musiclib.note import SpecificNote
from musiclib.scale import Scale
from musiclib.svg.plane import JankoSquare


@pytest.mark.parametrize('scale', [None, Scale.from_name('f', 'dorian')])
@pytest.mark.parametrize('origin_note', [None, SpecificNote('a', 2)])
def test_smoke(scale, origin_note):
    kwargs = {}
    if scale is not None:
        kwargs['scale'] = scale
    if origin_note is not None:
        kwargs['origin_note'] = origin_note
    JankoSquare(**kwargs)
