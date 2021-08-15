import functools
import io
import base64
import sys
from PIL import Image, ImageDraw, ImageFont
import util
import config

# font = ImageFont.truetype('static/fonts/SFMono-Bold.otf', 40)
font = ImageFont.truetype('static/fonts/SFMono-Semibold.otf', 40)
piano_template = Image.open("static/piano_template-grey2.png").convert("RGBA")


white_x0, white_dx, white_y = 24, 73, 351
black_x0, black_dx, black_y = 61, 73, 225

note_xy = {
    (config.chromatic_notes[ 0], 0): (white_x0 + white_dx *  0, white_y),
    (config.chromatic_notes[ 1], 0): (black_x0 + black_dx *  0, black_y),
    (config.chromatic_notes[ 2], 0): (white_x0 + white_dx *  1, white_y),
    (config.chromatic_notes[ 3], 0): (black_x0 + black_dx *  1, black_y),
    (config.chromatic_notes[ 4], 0): (white_x0 + white_dx *  2, white_y),
    (config.chromatic_notes[ 5], 0): (white_x0 + white_dx *  3, white_y),
    (config.chromatic_notes[ 6], 0): (black_x0 + black_dx *  3, black_y),
    (config.chromatic_notes[ 7], 0): (white_x0 + white_dx *  4, white_y),
    (config.chromatic_notes[ 8], 0): (black_x0 + black_dx *  4, black_y),
    (config.chromatic_notes[ 9], 0): (white_x0 + white_dx *  5, white_y),
    (config.chromatic_notes[10], 0): (black_x0 + black_dx *  5, black_y),
    (config.chromatic_notes[11], 0): (white_x0 + white_dx *  6, white_y),
    (config.chromatic_notes[ 0], 1): (white_x0 + white_dx *  7, white_y),
    (config.chromatic_notes[ 1], 1): (black_x0 + black_dx *  7, black_y),
    (config.chromatic_notes[ 2], 1): (white_x0 + white_dx *  8, white_y),
    (config.chromatic_notes[ 3], 1): (black_x0 + black_dx *  8, black_y),
    (config.chromatic_notes[ 4], 1): (white_x0 + white_dx *  9, white_y),
    (config.chromatic_notes[ 5], 1): (white_x0 + white_dx * 10, white_y),
    (config.chromatic_notes[ 6], 1): (black_x0 + black_dx * 10, black_y),
    (config.chromatic_notes[ 7], 1): (white_x0 + white_dx * 11, white_y),
    (config.chromatic_notes[ 8], 1): (black_x0 + black_dx * 11, black_y),
    (config.chromatic_notes[ 9], 1): (white_x0 + white_dx * 12, white_y),
    (config.chromatic_notes[10], 1): (black_x0 + black_dx * 12, black_y),
    (config.chromatic_notes[11], 1): (white_x0 + white_dx * 13, white_y),
}


r = 50
padding_x = 12
padding_y = 1
red_bigger = -2
number_dy = 50


def red_square(d, xy):
    x, y = xy
    red_x = x - red_bigger
    red_y = y - red_bigger
    red_r = r + red_bigger * 2
    d.rectangle((red_x - padding_x, red_y - padding_y, red_x - padding_x + red_r, red_y - padding_y + red_r), fill=(255, 0, 0))

def color_rect(d, xy, color):
    x, y = xy
    red_x = x - red_bigger
    red_y = y - red_bigger + r
    red_r = r + red_bigger * 2
    x0, y0 = red_x - padding_x, red_y - padding_y
    x1, y1 = red_x - padding_x + red_r, red_y - padding_y + red_r/3
    d.rectangle((x0, y0, x1, y1), fill=color)


def add_square(d, xy, note, color=(255, 255, 255), number=None, number_color=(215, 215, 215)):
    x, y = xy
    red_x = x - red_bigger
    red_y = y - red_bigger
    red_r = r + red_bigger * 2

    d.rectangle((red_x - padding_x, red_y - padding_y, red_x - padding_x + red_r, red_y - padding_y + red_r), fill=color)
    d.text((x, y), note, font=font, fill=(0, 0, 0, 255))

    if number:
        d.rectangle((red_x - padding_x, red_y - padding_y - number_dy, red_x - padding_x + red_r, red_y - padding_y - number_dy + red_r), fill=number_color)
        d.text((x, y - number_dy), str(number), font=font, fill=(0, 0, 0, 255))


# def small_dot(d, xy):
#     x, y = xy
#     red_x = x - red_bigger
#     red_y = y - red_bigger
#     red_r = r + red_bigger * 2
#     x0, y0 = red_x - padding_x, red_y - padding_y - number_dy * 1.5
#     x1, y1 = red_x - padding_x + red_r, red_y - padding_y - number_dy * 2 + red_r/3
#     d.rectangle((x0, y0, x1, y1), fill=(255, 255, 255))


@functools.lru_cache(maxsize=2048)
def scale_to_piano(scale, as_base64=False):
    print('cold run')
    notes_scale_colors = scale.notes_scale_colors
    green_notes = getattr(scale, 'new_notes', frozenset())
    red_notes = getattr(scale, 'del_notes', frozenset())
    shared_chords = getattr(scale, 'shared_chords', frozenset())
    shared_chords_roots = frozenset(chord[0] for chord in shared_chords)

    layer = Image.new("RGBA", piano_template.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(layer)

    i = 0
    scale_finished = False
    for (note, octave), xy in note_xy.items():
        if i > 0:
            if note in red_notes:
                red_square(d, xy)
            if note == scale.notes[0]:
                break

        if not scale_finished and note == scale.notes[i]:
            if scale.kind == 'diatonic' and scale.chords[i] in shared_chords:
                number_color = (255, 255, 255)
            else:
                number_color = (215, 215, 215)

            if note in green_notes:
                add_square(d, xy, note, number=i+1, color=(0, 255, 0), number_color=number_color)
            else:
                add_square(d, xy, note, number=i+1, number_color=number_color)

            color_rect(d, xy, notes_scale_colors[i])
            i += 1
            if i == len(scale.notes):
                scale_finished = True


    out = Image.alpha_composite(piano_template, layer)
    out.thumbnail((sys.maxsize, 120), Image.ANTIALIAS)
    out = out.crop((0, 22, out.size[0], 98))

    if as_base64:
        b = io.BytesIO()
        out.save(b, format='PNG')
        return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
    return out


@functools.lru_cache(maxsize=2048)
def chord_to_piano(chord, as_base64=False):
    layer = Image.new("RGBA", piano_template.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(layer)

    i = 0
    for (note, octave), xy in note_xy.items():
        if note == chord[i]:
            add_square(d, xy, note)
            i += 1
            if i == len(chord):
                break


    out = Image.alpha_composite(piano_template, layer)
    out.thumbnail((sys.maxsize, 120), Image.ANTIALIAS)
    out = out.crop((0, 22, out.size[0], 98))
    if as_base64:
        b = io.BytesIO()
        out.save(b, format='PNG')
        return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
    return out