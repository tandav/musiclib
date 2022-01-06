import random


def hex_to_rgb(color):
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(color):
    return '#{:02x}{:02x}{:02x}'.format(*color)


def rgba_to_rgb(rgb_background, rgba_color):
    '''https://stackoverflow.com/a/21576659/4204843'''

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
