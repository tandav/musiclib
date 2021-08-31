import functools
import itertools
import io
import base64
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from . import config, util
from .note import Note


class Piano:
    def __init__(self, size=None, scale=None):
        if size is None:
            size = config.piano_img_size
        ww = size[0] // 14  # white key width
        bw = int(ww * 0.6)  # black key width

        white_notes = tuple(Note(config.chromatic_notes[i]) for i in (0, 2, 4, 5, 7, 9, 11))
        black_notes = tuple(Note(config.chromatic_notes[i]) for i in (1, 3, 6, 8, 10))
        wo = tuple(itertools.product((0, 1), white_notes))  # white with octave: (octave, note)
        bo = tuple(itertools.product((0, 1), black_notes))  # black with octave: (octave, note)
        WHITE_COLOR = (170,) * 3
        BLACK_COLOR = (80,) * 3

        self.colors = {(octave, note): WHITE_COLOR for octave, note in wo}
        self.colors |= {(octave, note): BLACK_COLOR for octave, note in bo}

        self.img = Image.new('RGBA', size, (0, 0, 0, 0))
        d = ImageDraw.Draw(self.img)

        for (octave, note), x in zip(wo, range(0, size[0], ww)):
            color = self.colors[octave, note]
            if scale is not None and note in scale.notes:
                color = scale.note_colors[note]

            d.rectangle((x, 0, x + ww, size[1]), fill=color, outline=BLACK_COLOR, width=1)

        it = (x for i, x in enumerate(range(0 + ww, size[0], ww)) if i not in {2, 6, 9, 13})
        for (octave, note), x in zip(bo, it):
            color = self.colors[octave, note]

            if scale is not None and note in scale.notes:
                color = scale.note_colors[note]
            d.rectangle((x - bw // 2, 0, x + bw // 2, int(size[1] * 0.6)), fill=color, outline=BLACK_COLOR, width=1)

        d.rectangle((0, 0, size[0] - 1, size[1] - 1), outline=BLACK_COLOR, width=1)

    def __repr__(self):
        return 'Piano'

    def _repr_png_(self):
        b = io.BytesIO()
        self.img.save(b, 'PNG')
        return b.getvalue()

    def _repr_html_(self):
        return f"<img src='data:image/png;base64,{base64.b64encode(self._repr_png_()).decode()}'/>"