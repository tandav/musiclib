from __future__ import annotations

from musictool import config
from musictool.config import BLACK_PALE
from musictool.config import BLUE
from musictool.config import GREEN
from musictool.config import RED
from musictool.config import WHITE_PALE
from musictool.note import BLACK_NOTES
from musictool.note import WHITE_NOTES
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.noterange import CHROMATIC_NOTESET
from musictool.noterange import NoteRange
from musictool.util.color import RGBColor
from musictool.util.color import hex_to_rgb


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
        top_rect_height: int = 5,
        square_size: int = 12,
        ww: int = 18,  # white key width
        wh: int = 85,  # white key height
        noterange: NoteRange | None = None,
        black_between: bool = False,
    ):
        self.ww = ww
        self.wh = wh
        self.bw = int(ww * 0.6)
        self.bh = int(wh * 0.6)

        self.top_rect_height = top_rect_height
        self.square_size = square_size

        self.notes = notes
        self.note_scales = note_scales
        self.notes_squares = {} if notes_squares is None else notes_squares

        if noterange is not None:
            if noterange.noteset is not CHROMATIC_NOTESET:
                raise ValueError  # maybe this is not necessary

            # ensure that start and stop are white keys
            self.noterange = NoteRange(
                start=noterange.start + -1 if noterange.start.abstract in BLACK_NOTES else noterange.start,
                stop=noterange.stop + 1 if noterange.stop.abstract in BLACK_NOTES else noterange.stop,
            )
        else:
            # render 2 octaves by default
            self.noterange = NoteRange(SpecificNote('C', 0), SpecificNote('B', 1))

        self.white_notes = tuple(note for note in self.noterange if note.abstract in WHITE_NOTES)
        self.black_notes = tuple(note for note in self.noterange if note.abstract in BLACK_NOTES)
        self.size = ww * len(self.white_notes), wh
        self.rects = []

        for note in self.white_notes + self.black_notes:
            x, w, h, c, sx, sy = self.coord_helper(note)

            self.rects.append(f"""<rect x='{x}' y='0' width='{w}' height='{h}' style='fill:rgb{c};stroke-width:1;stroke:rgb{BLACK_PALE}' onclick="play_note('{note.abstract.name}', '{note.octave}')"/>""")

            for color_notes, color in zip([red_notes, green_notes, blue_notes], [RED, GREEN, BLUE]):
                if note.abstract in color_notes: self.rects.append(f"""<rect x='{x}' y='0' width='{w}' height='{top_rect_height}' style='fill:rgb{color};'/>""")

            if (fill_border_color := self.notes_squares.get(note.abstract)):
                fill, border, text_color, str_chord = fill_border_color
                self.rects.append(f"""
                    <g onclick=play_chord('{str_chord}')>
                        <rect x='{sx}' y='{sy}' width='{square_size}' height='{square_size}' style='fill:rgb{fill};stroke-width:1;stroke:rgb{border}'/>
                        <text x='{sx}' y='{sy + square_size}' font-family="Menlo" font-size='15' style='fill:rgb{text_color}'>{note.name}</text>
                    </g>
                """)

        # border around whole svg
        self.rects.append(f"<rect x='0', y='0' width='{self.size[0] - 1}' height='{self.size[1] - 1}' style='fill:none;stroke-width:1;stroke:rgb{BLACK_PALE}'/>")

    def coord_helper(self, note: SpecificNote) -> tuple[int, int, int, RGBColor, int, int]:
        """
        helper function which computes values for a given note

        Returns
        -------
        x: x coordinate of note rect
        w: width of note rect
        h: height of note rect
        c: color of note
        sx: x coordinate of square
        sy: x coordinate of square
        """
        if note.abstract in self.notes:
            if self.note_scales is not None:
                c = hex_to_rgb(config.scale_colors[self.note_scales[note.abstract]])
            else:
                c = RED
        else:
            c = note_color(note)

        if note in self.white_notes:
            x = self.ww * self.white_notes.index(note)
            return x, self.ww, self.wh, c, (x + x + self.ww) // 2 - self.square_size // 2, self.wh - self.square_size - 5
        elif note in self.black_notes:
            x = self.ww * self.white_notes.index(note + 1) - self.bw // 2
            return x, self.bw, self.bh, c, x - self.square_size // 2, self.bh - self.square_size - 3
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
