from __future__ import annotations

import itertools

from musictool import config
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.util.color import RGBColor
from musictool.util.color import hex_to_rgb

WHITE_COLOR = (170,) * 3
BLACK_COLOR = (80,) * 3
RED_COLOR = 255, 0, 0
GREEN_COLOR = 0, 255, 0
BLUE_COLOR = 0, 0, 255


def note_color(note: Note | SpecificNote) -> RGBColor:
    _colors = {
        Note('C'): WHITE_COLOR,
        Note('d'): BLACK_COLOR,
        Note('D'): WHITE_COLOR,
        Note('e'): BLACK_COLOR,
        Note('E'): WHITE_COLOR,
        Note('F'): WHITE_COLOR,
        Note('f'): BLACK_COLOR,
        Note('G'): WHITE_COLOR,
        Note('a'): BLACK_COLOR,
        Note('A'): WHITE_COLOR,
        Note('b'): BLACK_COLOR,
        Note('B'): WHITE_COLOR,
    }
    if isinstance(note, SpecificNote):
        return _colors[note.abstract]
    elif isinstance(note, Note):
        return _colors[note]
    else:
        raise TypeError


class Piano:
    def __init__(
        self,
        notes: frozenset[Note],
        red_notes: frozenset[Note] = frozenset(),
        green_notes: frozenset[Note] = frozenset(),
        blue_notes: frozenset[Note] = frozenset(),
        notes_squares: dict[Note, tuple[RGBColor, RGBColor, RGBColor, str]] | None = None,
        note_scales: dict[Note, str] | None = None,
        size: tuple[int, int] = config.piano_img_size,
        small_rect_height: int = 5,
        small_square_size: int = 12,
    ):
        if notes_squares is None:
            notes_squares = {}
        self.size = size
        ww = self.size[0] // 14  # white key width
        bw = int(ww * 0.6)  # black key width
        bh = int(self.size[1] * 0.6)  # black key height
        do = config.default_octave
        white_notes = tuple(SpecificNote(config.chromatic_notes[i], octave) for octave, i in itertools.product((do, do + 1), (0, 2, 4, 5, 7, 9, 11)))
        black_notes = tuple(SpecificNote(config.chromatic_notes[i], octave) for octave, i in itertools.product((do, do + 1), (1, 3, 6, 8, 10)))

        self.rects = []

        # todo: merge white keys and black keys logic into single loop to deduplicate logic

        # white keys
        for note, x in zip(white_notes, range(0, self.size[0], ww)):
            color = note_color(note)
            if note_scales is not None and note.abstract in notes:
                color = hex_to_rgb(config.scale_colors[note_scales[note.abstract]])
            self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{self.size[1]}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_COLOR}' onclick="play_note('{note.abstract.name}', '{note.octave}')"/>""")

            if note.abstract in red_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{small_rect_height}' style='fill:rgb{RED_COLOR};'/>""")
            if note.abstract in green_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{small_rect_height}' style='fill:rgb{GREEN_COLOR};'/>""")
            if note.abstract in blue_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{small_rect_height}' style='fill:rgb{BLUE_COLOR};'/>""")

            if (fill_border_color := notes_squares.get(note.abstract)):
                fill, border, text_color, str_chord = fill_border_color
                self.rects.append(f"""
                    <g onclick=play_chord('{str_chord}')>
                        <rect x='{(x + x + ww) // 2 - small_square_size // 2}' y='{self.size[1] - small_square_size - 5}' width='{small_square_size}' height='{small_square_size}' style='fill:rgb{fill};stroke-width:1;stroke:rgb{border}'/>
                        <text x='{(x + x + ww) // 2 - small_square_size // 2}' y='{self.size[1] - small_square_size - 5 + small_square_size}' font-family="Menlo" font-size='15' style='fill:rgb{text_color}'>{note.name}</text>
                    </g>
                """)

        # black notes
        it = (x for i, x in enumerate(range(0 + ww, self.size[0], ww)) if i not in {2, 6, 9, 13})
        for note, x in zip(black_notes, it):
            color = note_color(note)
            if note_scales is not None and note.abstract in notes:
                color = hex_to_rgb(config.scale_colors[note_scales[note.abstract]])
            self.rects.append(f"""<rect x='{x - bw // 2}', y='0' width='{bw}' height='{bh}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_COLOR}' onclick="play_note('{note.name}', '{note.octave}')"/>""")

            if note.abstract in red_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{small_rect_height}' style='fill:rgb{RED_COLOR};'/>""")
            if note.abstract in green_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{small_rect_height}' style='fill:rgb{GREEN_COLOR};'/>""")
            if note.abstract in blue_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{small_rect_height}' style='fill:rgb{BLUE_COLOR};'/>""")

            if (fill_border_color := notes_squares.get(note.abstract)):
                fill, border, text_color, str_chord = fill_border_color
                self.rects.append(f"""
                    <g onclick=play_chord('{str_chord}')>
                        <rect x='{x - small_square_size // 2}' y='{bh - 15}' width='{small_square_size}' height='{small_square_size}' style='fill:rgb{fill};stroke-width:1;stroke:rgb{border}'/>
                        <text x='{x - small_square_size // 2}' y='{bh - 15 + small_square_size}' font-family="Menlo" font-size='15' style='fill:rgb{text_color}'>{note.name}</text>
                    </g>
                """)

        # border around whole svg
        self.rects.append(f"<rect x='0', y='0' width='{self.size[0] - 1}' height='{self.size[1] - 1}' style='fill:none;stroke-width:1;stroke:rgb{BLACK_COLOR}'/>")

    def add_rect(self, x, y, w, h, fill, border_color):
        pass

    def __repr__(self):
        return 'Piano'

    def _repr_svg_(self):
        rects = '\n'.join(self.rects)
        return f"""
        <svg width='{self.size[0]}' height='{self.size[1]}'>
        {rects}
        </svg>
        """
