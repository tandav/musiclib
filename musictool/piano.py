from __future__ import annotations

import itertools
import typing

from musictool import config
from musictool.config import BLACK_PALE
from musictool.config import BLUE
from musictool.config import GREEN
from musictool.config import RED
from musictool.config import WHITE_PALE
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.note import BLACK_NOTES
from musictool.note import WHITE_NOTES
from musictool.util.color import RGBColor
from musictool.util.color import hex_to_rgb

# if typing.TYPE_CHECKING:
    # from musictool.noterange import NoteRange

from musictool.noterange import NoteRange
from musictool.noterange import CHROMATIC_NOTESET

default_octave = 5
# do = config.default_octave
# do = 5


def note_color(note: Note | SpecificNote) -> RGBColor:
    def _note_color(note: Note) -> RGBColor:
        return WHITE_PALE if note in WHITE_NOTES else BLACK_PALE
    if isinstance(note, SpecificNote):
        return _note_color(note.abstract)
    elif isinstance(note, Note):
        return _note_color(note)
    else:
        raise TypeError



class Piano:
    def __init__(
        self,
        notes: frozenset[Note | SpecificNote],
        red_notes: frozenset[Note] = frozenset(),
        green_notes: frozenset[Note] = frozenset(),
        blue_notes: frozenset[Note] = frozenset(),
        notes_squares: dict[Note, tuple[RGBColor, RGBColor, RGBColor, str]] | None = None,
        note_scales: dict[Note, str] | None = None,
        small_rect_height: int = 5,
        small_square_size: int = 12,
        ww: int = 18,  # white_key_width
        wh: int = 85,  # white_key_width
        bw: int = 10,  # black_key_width
        # bw_frac: float = 0.6,
        # bh_frac: float = 0.6,
        noterange: NoteRange | None = None,
        black_between: bool = False,
    ):

        # if bw_frac is not None:
        #     bw = int(ww * 0.6)
        # if bh_frac is not None:
        #     bh = int(wh * bh_frac)

        self.ww = ww
        self.wh = wh
        self.bw = int(ww * 0.6)
        self.bh = int(wh * 0.6)

        self.notes = notes
        self.note_scales = note_scales
        self.notes_squares = {} if notes_squares is None else notes_squares

        if noterange is not None:
            if noterange.noteset is not CHROMATIC_NOTESET:
                raise ValueError  # maybe this is not necessary

            # ensure that start and stop are white keys
            self.noterange = NoteRange(
                start = noterange.start + -1 if noterange.start.abstract in BLACK_NOTES else noterange.start,
                stop = noterange.stop + 1 if noterange.stop.abstract in BLACK_NOTES else noterange.stop,
            )
        else:
            # render 2 octaves by default
            self.noterange = NoteRange(SpecificNote('C', 0), SpecificNote('B', 1))

            # ww = white_key_width or self.size[0] // 14
            # bw = black_key_width or int(ww * 0.6)
            # black_key_height_frac = black_key_height_frac or 0.6
            # bh = int(self.size[1] * black_key_height_frac)


        self.white_notes = tuple(note for note in self.noterange if note.abstract in WHITE_NOTES)
        self.black_notes = tuple(note for note in self.noterange if note.abstract in BLACK_NOTES)
        # white_notes = tuple(SpecificNote(config.chromatic_notes[i], octave) for octave, i in itertools.product((do, do + 1), (0, 2, 4, 5, 7, 9, 11)))
        # black_notes = tuple(SpecificNote(config.chromatic_notes[i], octave) for octave, i in itertools.product((do, do + 1), (1, 3, 6, 8, 10)))

        self.size = ww * len(self.white_notes), wh

        self.rects = []

        # todo: merge WHITE_PALE keys and BLACK_PALE keys logic into single loop to deduplicate logic
        # x = 0
        for note in self.white_notes + self.black_notes:
            x, w, h = self.xwh(note)



            self.rects.append(f"""<rect x='{x}' y='0' width='{w}' height='{h}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_PALE}' onclick="play_note('{note.abstract.name}', '{note.octave}')"/>""")

        #     ...
        #     if note.abstract in WHITE_NOTES:
        #         x += ww
        #     else:
        #         x

            # if note.abstract in BLACK_NOTES:


        # for note, x in zip(white_notes, range(0, self.size[0], ww), strict=True):
        #     if note.abstract in notes:
        #         if note_scales is not None:
        #             color = hex_to_rgb(config.scale_colors[note_scales[note.abstract]])
        #         else:
        #             color = RED
        #     else:
        #         color = note_color(note)
        #     self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{self.size[1]}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_PALE}' onclick="play_note('{note.abstract.name}', '{note.octave}')"/>""")
        #
        #     if note.abstract in red_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{small_rect_height}' style='fill:rgb{RED};'/>""")
        #     if note.abstract in green_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{small_rect_height}' style='fill:rgb{GREEN};'/>""")
        #     if note.abstract in blue_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{small_rect_height}' style='fill:rgb{BLUE};'/>""")
        #
        #     if (fill_border_color := notes_squares.get(note.abstract)):
        #         fill, border, text_color, str_chord = fill_border_color
        #         self.rects.append(f"""
        #             <g onclick=play_chord('{str_chord}')>
        #                 <rect x='{(x + x + ww) // 2 - small_square_size // 2}' y='{self.size[1] - small_square_size - 5}' width='{small_square_size}' height='{small_square_size}' style='fill:rgb{fill};stroke-width:1;stroke:rgb{border}'/>
        #                 <text x='{(x + x + ww) // 2 - small_square_size // 2}' y='{self.size[1] - small_square_size - 5 + small_square_size}' font-family="Menlo" font-size='15' style='fill:rgb{text_color}'>{note.name}</text>
        #             </g>
        #         """)
        #
        # # black notes
        # it = (x for i, x in enumerate(range(0 + ww, self.size[0], ww)) if i not in {2, 6, 9, 13})
        # for note, x in zip(black_notes, it, strict=True):
        #     if note.abstract in notes:
        #         if note_scales is not None:
        #             color = hex_to_rgb(config.scale_colors[note_scales[note.abstract]])
        #         else:
        #             color = RED
        #     else:
        #         color = note_color(note)
        #     self.rects.append(f"""<rect x='{x - bw // 2}', y='0' width='{bw}' height='{bh}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_PALE}' onclick="play_note('{note.name}', '{note.octave}')"/>""")
        #
        #     if note.abstract in red_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{small_rect_height}' style='fill:rgb{RED};'/>""")
        #     if note.abstract in green_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{small_rect_height}' style='fill:rgb{GREEN};'/>""")
        #     if note.abstract in blue_notes: self.rects.append(f"""<rect x='{x - bw // 2}' y='0' width='{bw}' height='{small_rect_height}' style='fill:rgb{BLUE};'/>""")
        #
        #     if (fill_border_color := notes_squares.get(note.abstract)):
        #         fill, border, text_color, str_chord = fill_border_color
        #         self.rects.append(f"""
        #             <g onclick=play_chord('{str_chord}')>
        #                 <rect x='{x - small_square_size // 2}' y='{bh - 15}' width='{small_square_size}' height='{small_square_size}' style='fill:rgb{fill};stroke-width:1;stroke:rgb{border}'/>
        #                 <text x='{x - small_square_size // 2}' y='{bh - 15 + small_square_size}' font-family="Menlo" font-size='15' style='fill:rgb{text_color}'>{note.name}</text>
        #             </g>
        #         """)

        # border around whole svg
        self.rects.append(f"<rect x='0', y='0' width='{self.size[0] - 1}' height='{self.size[1] - 1}' style='fill:none;stroke-width:1;stroke:rgb{BLACK_PALE}'/>")

    def xywhc(self, note: SpecificNote) -> tuple[int, int, int]:
        """
        helper function which computes values for a given note

        Returns
        -------
        x: x coordinate of note rect
        w: width of note rect
        h: height of note rect
        rx: x coordinate of square
        ry: y coordinate of square
        c: color of note
        """
        if note.abstract in self.notes:
            if self.note_scales is not None:
                c = hex_to_rgb(config.scale_colors[self.note_scales[note.abstract]])
            else:
                c = RED
        else:
            c = note_color(note)

        if note in self.white_notes:
            return self.ww * self.white_notes.index(note), self.ww, self.wh, c
        elif note in self.black_notes:
            return self.ww * self.white_notes.index(note + 1) - self.bw // 2, self.bw, self.bh, c
        else:
            raise KeyError('unknown note')

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
