import itertools
from PIL import Image, ImageDraw, ImageFont
import config

white_x0, white_dx, white_y = 24, 73, 351
black_x0, black_dx, black_y = 61, 73, 255

note_loc = {
    ('C', 0): (white_x0 + white_dx *  0, white_y),
    ('D', 0): (white_x0 + white_dx *  1, white_y),
    ('E', 0): (white_x0 + white_dx *  2, white_y),
    ('F', 0): (white_x0 + white_dx *  3, white_y),
    ('G', 0): (white_x0 + white_dx *  4, white_y),
    ('A', 0): (white_x0 + white_dx *  5, white_y),
    ('B', 0): (white_x0 + white_dx *  6, white_y),
    ('C', 1): (white_x0 + white_dx *  7, white_y),
    ('D', 1): (white_x0 + white_dx *  8, white_y),
    ('E', 1): (white_x0 + white_dx *  9, white_y),
    ('F', 1): (white_x0 + white_dx * 10, white_y),
    ('G', 1): (white_x0 + white_dx * 11, white_y),
    ('A', 1): (white_x0 + white_dx * 12, white_y),
    ('B', 1): (white_x0 + white_dx * 13, white_y),
    ('d', 0): (black_x0 + black_dx *  0, black_y),
    ('e', 0): (black_x0 + black_dx *  1, black_y),
    ('f', 0): (black_x0 + black_dx *  3, black_y),
    ('a', 0): (black_x0 + black_dx *  4, black_y),
    ('b', 0): (black_x0 + black_dx *  5, black_y),
    ('d', 1): (black_x0 + black_dx *  7, black_y),
    ('e', 1): (black_x0 + black_dx *  8, black_y),
    ('f', 1): (black_x0 + black_dx * 10, black_y),
    ('a', 1): (black_x0 + black_dx * 11, black_y),
    ('b', 1): (black_x0 + black_dx * 12, black_y),
}

font = ImageFont.truetype('res/SFNSMono.ttf', 40)

piano_template = Image.open("res/piano_template-grey.png").convert("RGBA")
layer = Image.new("RGBA", piano_template.size, (255,255,255,0))
d = ImageDraw.Draw(layer)


def add_square(xy, text):
    x, y = xy
    r = 50
    padding_x = 12
    padding_y = 1
    red_bigger = -2
    red_x = x - red_bigger
    red_y = y - red_bigger
    red_r = r + red_bigger * 2

    # d.rectangle((x - padding_x, y - padding_y, x - padding_x + r , y - padding_y + r), fill=(0,0,0,0), outline=(0,0,0), width=4)
    # d.rectangle((red_x - padding_x, red_y - padding_y, red_x - padding_x + red_r , red_y - padding_y + red_r), fill=(255,255,255,255), outline=(255,0,0), width=5)
    d.rectangle((red_x - padding_x, red_y - padding_y, red_x - padding_x + red_r, red_y - padding_y + red_r), fill=(255, 255, 255, 255))
    d.text((x, y), text, font=font, fill=(0, 0, 0, 255))


def scale_to_piano():
    for octave, note in itertools.product((0, 1), config.chromatic_notes):
        add_square(note_loc[(note, octave)], note)
    out = Image.alpha_composite(piano_template, layer)
    return  out