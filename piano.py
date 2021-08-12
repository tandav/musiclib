from PIL import Image, ImageDraw, ImageFont
import config
import io
import base64
import sys

font = ImageFont.truetype('res/SFNSMono.ttf', 40)
piano_template = Image.open("res/piano_template-grey.png").convert("RGBA")


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

def scale_to_piano(scale, as_base64=False):
    layer = Image.new("RGBA", piano_template.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(layer)

    def add_square(xy, note, number):
        x, y = xy
        r = 50
        padding_x = 12
        padding_y = 1
        red_bigger = -2
        red_x = x - red_bigger
        red_y = y - red_bigger
        red_r = r + red_bigger * 2

        number_dy = 50

        # d.rectangle((x - padding_x, y - padding_y, x - padding_x + r , y - padding_y + r), fill=(0,0,0,0), outline=(0,0,0), width=4)
        # d.rectangle((red_x - padding_x, red_y - padding_y, red_x - padding_x + red_r , red_y - padding_y + red_r), fill=(255,255,255,255), outline=(255,0,0), width=5)
        d.rectangle((red_x - padding_x, red_y - padding_y, red_x - padding_x + red_r, red_y - padding_y + red_r), fill=(255, 255, 255, 255))
        d.rectangle((red_x - padding_x, red_y - padding_y - number_dy, red_x - padding_x + red_r, red_y - padding_y - number_dy + red_r), fill=(215, 215, 215))
        d.text((x, y), note, font=font, fill=(0, 0, 0, 255))
        d.text((x, y - number_dy), str(number), font=font, fill=(0, 0, 0, 255))

    i = 0
    for (note, octave), xy in note_xy.items():
        if note == scale[i]:
            add_square(xy, note, i + 1)
            i += 1
            if i == len(scale):
                break
    # for octave, note in itertools.product((0, 1), config.chromatic_notes):
    #     add_square(note_xy[(note, octave)], note)
    out = Image.alpha_composite(piano_template, layer)
    out.thumbnail((sys.maxsize, 170), Image.ANTIALIAS)
    if as_base64:
        b = io.BytesIO()
        out.save(b, format='PNG')
        return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
    return out