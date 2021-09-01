import functools
import itertools
from typing import Optional
from . import config, util
from .note import Note, SpecificNote
# from .chord import Chord
# from .scale import Scale

class Piano:
    def __init__(
        self,
        size: tuple[int, int] = config.piano_img_size,
        scale: Optional['Scale'] = None,
        chord: Optional['Chord'] = None,
        red_notes: frozenset[Note] = frozenset(),
        green_notes: frozenset[Note] = frozenset(),
        blue_notes: frozenset[Note] = frozenset(),
    ):
        self.size = size
        ww = self.size[0] // 14  # white key width
        bw = int(ww * 0.6)  # black key width
        do = config.default_octave
        white_notes = tuple(SpecificNote(Note(config.chromatic_notes[i]), octave) for octave, i in itertools.product((do, do + 1), (0, 2, 4, 5, 7, 9, 11)))
        black_notes = tuple(SpecificNote(Note(config.chromatic_notes[i]), octave) for octave, i in itertools.product((do, do + 1), (1, 3, 6, 8, 10)))

        WHITE_COLOR = (170,) * 3
        BLACK_COLOR = (80,) * 3
        RED_COLOR = 255, 0, 0
        GREEN_COLOR = 0, 255, 0
        BLUE_COLOR = 0, 0, 255

        for note in white_notes: note.color = WHITE_COLOR
        for note in black_notes: note.color = BLACK_COLOR

        SMALL_RECT_HEIGHT = 5

        self.rects = []

        # white keys
        for note, x in zip(white_notes, range(0, self.size[0], ww)):
            color = note.color
            if scale is not None and note.abstract in scale.notes:
                color = scale.note_colors[note.abstract]
            self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{self.size[1]}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_COLOR}' onclick="play_note('{note.abstract.name}', '{note.octave}')"/>""")

            if note.abstract in red_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{RED_COLOR};'/>""")
            if note.abstract in green_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{GREEN_COLOR};'/>""")
            if note.abstract in blue_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{BLUE_COLOR};'/>""")


        # black notes
        it = (x for i, x in enumerate(range(0 + ww, self.size[0], ww)) if i not in {2, 6, 9, 13})
        for note, x in zip(black_notes, it):
            color = note.color
            if scale is not None and note.abstract in scale.notes:
                color = scale.note_colors[note.abstract]
            self.rects.append(f"""<rect x='{x - bw // 2}', y='0' width='{bw}' height='{int(self.size[1] * 0.6)}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_COLOR}' onclick="play_note('{note.name}', '{note.octave}')"/>""")

            if note.abstract in red_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{RED_COLOR};'/>""")
            if note.abstract in green_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{GREEN_COLOR};'/>""")
            if note.abstract in blue_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{BLUE_COLOR};'/>""")


        # border around whole svg
        self.rects.append(f"<rect x='0', y='0' width='{self.size[0] - 1}' height='{self.size[1] - 1}' style='fill:none;stroke-width:1;stroke:rgb{BLACK_COLOR}'/>")

    def add_rect(self, x, y, w, h, fill, border_color):
        pass


    def __repr__(self):
        return 'Piano'

    def _repr_svg_(self):
        rects = '\n'.join(self.rects)
        return f'''
        <svg width='{self.size[0]}' height='{self.size[1]}'>
        {rects}
        </svg>
        '''

