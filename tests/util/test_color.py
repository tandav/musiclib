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
