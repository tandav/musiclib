from __future__ import annotations

import itertools

from musictool import config
from musictool.config import BLACK_PALE
from musictool.config import BLUE
from musictool.config import GREEN
from musictool.config import RED
from musictool.config import WHITE_PALE
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.util.color import RGBColor
from musictool.util.color import hex_to_rgb


def note_color(note: Note | SpecificNote) -> RGBColor:
    _colors = {
        Note('C'): WHITE_PALE,
        Note('d'): BLACK_PALE,
        Note('D'): WHITE_PALE,
        Note('e'): BLACK_PALE,
        Note('E'): WHITE_PALE,
        Note('F'): WHITE_PALE,
        Note('f'): BLACK_PALE,
        Note('G'): WHITE_PALE,
        Note('a'): BLACK_PALE,
        Note('A'): WHITE_PALE,
        Note('b'): BLACK_PALE,
        Note('B'): WHITE_PALE,
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
        ww = self.size[0] // 14  # WHITE_PALE key width
        bw = int(ww * 0.6)  # BLACK_PALE key width
        bh = int(self.size[1] * 0.6)  # BLACK_PALE key height
        do = config.default_octave
        white_notes = tuple(SpecificNote(config.chromatic_notes[i], octave) for octave, i in itertools.product((do, do + 1), (0, 2, 4, 5, 7, 9, 11)))
        black_notes = tuple(SpecificNote(config.chromatic_notes[i], octave) for octave, i in itertools.product((do, do + 1), (1, 3, 6, 8, 10)))

        self.rects = []

        # todo: merge WHITE_PALE keys and BLACK_PALE keys logic into single loop to deduplicate logic

        # white keys
        for note, x in zip(white_notes, range(0, self.size[0], ww), strict=True):
            if note.abstract in notes:
                if note_scales is not None:
                    color = hex_to_rgb(config.scale_colors[note_scales[note.abstract]])
                else:
                    color = RED
            else:
                color = note_color(note)
            self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{self.size[1]}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_PALE}' onclick="play_note('{note.abstract.name}', '{note.octave}')"/>""")

            if note.abstract in red_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{small_rect_height}' style='fill:rgb{RED};'/>""")
            if note.abstract in green_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{small_rect_height}' style='fill:rgb{GREEN};'/>""")
            if note.abstract in blue_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{small_rect_height}' style='fill:rgb{BLUE};'/>""")

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
        for note, x in zip(black_notes, it, strict=True):
            if note.abstract in notes:
                if note_scales is not None:
                    color = hex_to_rgb(config.scale_colors[note_scales[note.abstract]])
                else:
                    color = RED
            else:
                color = note_color(note)
            self.rects.append(f"""<rect x='{x - bw // 2}', y='0' width='{bw}' height='{bh}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_PALE}' onclick="play_note('{note.name}', '{note.octave}')"/>""")

            if note.abstract in red_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{small_rect_height}' style='fill:rgb{RED};'/>""")
            if note.abstract in green_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{small_rect_height}' style='fill:rgb{GREEN};'/>""")
            if note.abstract in blue_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{small_rect_height}' style='fill:rgb{BLUE};'/>""")

            if (fill_border_color := notes_squares.get(note.abstract)):
                fill, border, text_color, str_chord = fill_border_color
                self.rects.append(f"""
                    <g onclick=play_chord('{str_chord}')>
                        <rect x='{x - small_square_size // 2}' y='{bh - 15}' width='{small_square_size}' height='{small_square_size}' style='fill:rgb{fill};stroke-width:1;stroke:rgb{border}'/>
                        <text x='{x - small_square_size // 2}' y='{bh - 15 + small_square_size}' font-family="Menlo" font-size='15' style='fill:rgb{text_color}'>{note.name}</text>
                    </g>
                """)

        # border around whole svg
        self.rects.append(f"<rect x='0', y='0' width='{self.size[0] - 1}' height='{self.size[1] - 1}' style='fill:none;stroke-width:1;stroke:rgb{BLACK_PALE}'/>")

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
