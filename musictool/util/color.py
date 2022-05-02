import random

RGBColor = tuple[int, int, int]
HexColor = int


def hex_to_rgb(color: HexColor) -> RGBColor:
    if not (0 <= color <= 0xFFFFFF):
        raise ValueError('color must be in range [0, 0xFFFFFF]')
    a, b, c = color.to_bytes(3, byteorder='big')
    return a, b, c


def rgb_to_hex(color: RGBColor) -> HexColor:
    return int.from_bytes(bytes(color), byteorder='big')


def rgba_to_rgb(rgb_background, rgba_color):
    """https://stackoverflow.com/a/21576659/4204843"""

    alpha = rgba_color[3]

    return (
        int((1 - alpha) * rgb_background[0] + alpha * rgba_color[0]),
        int((1 - alpha) * rgb_background[1] + alpha * rgba_color[1]),
        int((1 - alpha) * rgb_background[2] + alpha * rgba_color[2]),
    )


def random_rgb():
    return random.randrange(255), random.randrange(255), random.randrange(255)


def random_rgba():
    return random.randrange(255), random.randrange(255), random.randrange(255), 255


def css_hex(color: int) -> str:
    return f'#{color:06X}'
