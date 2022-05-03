import pytest

from musictool.util import color


@pytest.mark.parametrize('hex_, rgb', [
    (0x000000, (0, 0, 0)),
    (0xFFFFFF, (255, 255, 255)),
    (0x8FED6C, (143, 237, 108)),
])
def test_hex_rgb(hex_, rgb):
    assert color.hex_to_rgb(hex_) == rgb
    assert color.rgb_to_hex(rgb) == hex_


@pytest.mark.parametrize('color_, expected', [
    (0x7CCB11, '#7CCB11'),
    (0x000000, '#000000'),
    (0x0000FF, '#0000FF'),
    (0x0000FE, '#0000FE'),
    (0xFF0000, '#FF0000'),
])
def test_css_hex(color_, expected):
    assert color.css_hex(color_) == expected
