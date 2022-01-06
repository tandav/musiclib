from __future__ import annotations

import itertools
import typing

from musictool import config
from musictool.note import Note
from musictool.note import SpecificNote

if typing.TYPE_CHECKING:
    from musictool.scale import ComparedScales
    from musictool.scale import Scale


class Piano:
    def __init__(
        self,
        size: tuple[int, int] = config.piano_img_size,
        scale: Scale | ComparedScales | None = None,
        red_notes: frozenset[Note] = frozenset(),
        green_notes: frozenset[Note] = frozenset(),
        blue_notes: frozenset[Note] = frozenset(),
        notes_squares: dict[Note: str] | None = None,
    ):
        if notes_squares is None:
            notes_squares = dict()
        self.size = size
        ww = self.size[0] // 14  # white key width
        bw = int(ww * 0.6)  # black key width
        bh = int(self.size[1] * 0.6)  # black key height
        do = config.default_octave
        white_notes = tuple(SpecificNote(config.chromatic_notes[i], octave) for octave, i in itertools.product((do, do + 1), (0, 2, 4, 5, 7, 9, 11)))
        black_notes = tuple(SpecificNote(config.chromatic_notes[i], octave) for octave, i in itertools.product((do, do + 1), (1, 3, 6, 8, 10)))

        WHITE_COLOR = (170,) * 3
        BLACK_COLOR = (80,) * 3
        RED_COLOR = 255, 0, 0
        GREEN_COLOR = 0, 255, 0
        BLUE_COLOR = 0, 0, 255

        for note in white_notes: note.color = WHITE_COLOR
        for note in black_notes: note.color = BLACK_COLOR

        SMALL_RECT_HEIGHT = 5
        SMALL_SQUARE_SIZE = 12

        self.rects = []

        # todo: merge white keys and black keys logic into single loop to deduplicate logic

        # white keys
        for note, x in zip(white_notes, range(0, self.size[0], ww)):
            color = note.color
            if scale is not None and note.abstract in scale.notes:
                color = scale.note_colors[note.abstract]
            self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{self.size[1]}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_COLOR}' onclick="play_note('{note.abstract.name}', '{note.octave}')"/>""")

            if note.abstract in red_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{RED_COLOR};'/>""")
            if note.abstract in green_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{GREEN_COLOR};'/>""")
            if note.abstract in blue_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{BLUE_COLOR};'/>""")

            if (fill_border_color := notes_squares.get(note.abstract)):
                fill, border, text_color, str_chord = fill_border_color
                self.rects.append(f"""
                    <g onclick=play_chord('{str_chord}')>
                        <rect x='{(x + x + ww) // 2 - SMALL_SQUARE_SIZE // 2}' y='{self.size[1] - SMALL_SQUARE_SIZE - 5}' width='{SMALL_SQUARE_SIZE}' height='{SMALL_SQUARE_SIZE}' style='fill:rgb{fill};stroke-width:1;stroke:rgb{border}'/>
                        <text x='{(x + x + ww) // 2 - SMALL_SQUARE_SIZE // 2}' y='{self.size[1] - SMALL_SQUARE_SIZE - 5 + SMALL_SQUARE_SIZE}' font-family="Menlo" font-size='15' style='fill:rgb{text_color}'>{note.name}</text>
                    </g>
                """)

        # black notes
        it = (x for i, x in enumerate(range(0 + ww, self.size[0], ww)) if i not in {2, 6, 9, 13})
        for note, x in zip(black_notes, it):
            color = note.color
            if scale is not None and note.abstract in scale.notes:
                color = scale.note_colors[note.abstract]
            self.rects.append(f"""<rect x='{x - bw // 2}', y='0' width='{bw}' height='{bh}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_COLOR}' onclick="play_note('{note.name}', '{note.octave}')"/>""")

            if note.abstract in red_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{RED_COLOR};'/>""")
            if note.abstract in green_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{GREEN_COLOR};'/>""")
            if note.abstract in blue_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{SMALL_RECT_HEIGHT}' style='fill:rgb{BLUE_COLOR};'/>""")

            if (fill_border_color := notes_squares.get(note.abstract)):
                fill, border, text_color, str_chord = fill_border_color
                self.rects.append(f"""
                    <g onclick=play_chord('{str_chord}')>
                        <rect x='{x - SMALL_SQUARE_SIZE // 2}' y='{bh - 15}' width='{SMALL_SQUARE_SIZE}' height='{SMALL_SQUARE_SIZE}' style='fill:rgb{fill};stroke-width:1;stroke:rgb{border}'/>
                        <text x='{x - SMALL_SQUARE_SIZE // 2}' y='{bh - 15 + SMALL_SQUARE_SIZE}' font-family="Menlo" font-size='15' style='fill:rgb{text_color}'>{note.name}</text>
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
        return f'''
        <svg width='{self.size[0]}' height='{self.size[1]}'>
        {rects}
        </svg>
        '''
