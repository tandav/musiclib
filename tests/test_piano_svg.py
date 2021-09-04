from piano_scales.scale import Scale
from piano_scales.scale import ComparedScale


a = Scale('C', 'major')


def test_svg_scale():
    a.to_piano_image()


def test_svg_compared_scale():
    b = Scale('f', 'phrygian')
    ComparedScale(a, b).to_piano_image()
