import pytest

from piano_scales.scale import ComparedScale
from piano_scales.scale import Scale


@pytest.fixture
def scale():
    yield Scale('C', 'major')


def test_svg_scale(scale):
    scale.to_piano_image()


def test_svg_compared_scale(scale):
    ComparedScale(scale, Scale('f', 'phrygian')).to_piano_image()
