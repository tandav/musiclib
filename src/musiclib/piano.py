from __future__ import annotations

from typing import TypedDict

import svg
from colortool import Color

from musiclib.config import BLACK_BRIGHT
from musiclib.config import BLACK_PALE
from musiclib.config import WHITE_BRIGHT
from musiclib.config import WHITE_PALE
from musiclib.note import BLACK_NOTES
from musiclib.note import WHITE_NOTES
from musiclib.note import Note
from musiclib.note import SpecificNote
from musiclib.noterange import CHROMATIC_NOTESET
from musiclib.noterange import NoteRange


def note_color(note: Note | SpecificNote) -> Color:
    def _note_color(note: Note) -> Color:
        return WHITE_PALE if note in WHITE_NOTES else BLACK_PALE
    if isinstance(note, SpecificNote):
        return _note_color(note.abstract)
    elif isinstance(note, Note):
        return _note_color(note)
    else:
        raise TypeError


class SquaresPayload(TypedDict, total=False):
    fill_color: Color
    border_color: Color
    text_color: Color
    text_size: Color
    text: str
    onclick: str


class Piano:
    def __init__(  # noqa: C901
        self,
        note_colors: dict[Note | SpecificNote, Color] | None = None,
        note_hrefs: dict[Note | SpecificNote, Color] | None = None,
        note_onclicks: dict[Note | SpecificNote, Color] | None = None,
        top_rect_colors: dict[Note | SpecificNote, Color] | None = None,
        squares: dict[Note | SpecificNote, SquaresPayload] | None = None,
        top_rect_height: int = 5,
        square_size: int = 12,
        ww: int = 18,  # white key width
        wh: int = 85,  # white key height
        noterange: NoteRange | None = None,
        black_small: bool = True,
    ):
        self.ww = ww
        self.wh = wh
        if black_small:
            self.bw = int(ww * 0.6)
            self.bh = int(wh * 0.6)
        else:
            self.bw = ww
            self.bh = wh

        self.top_rect_height = top_rect_height
        self.square_size = square_size
        self.black_small = black_small

        self.note_colors = note_colors or {}

        self.top_rect_colors: dict[Note | SpecificNote, Color]
        if top_rect_colors is None:
            self.top_rect_colors = {}
        else:
            self.top_rect_colors = top_rect_colors

        self.squares = squares or {}
        self.note_hrefs = note_hrefs or {}
        self.note_onclicks = note_onclicks or {}

        if noterange is not None:
            if noterange.noteset is not CHROMATIC_NOTESET:
                raise ValueError  # maybe this is not necessary

            if black_small:
                # ensure that start and stop are white keys
                self.noterange = NoteRange(
                    start=noterange.start + -1 if noterange.start.abstract in BLACK_NOTES else noterange.start,
                    stop=noterange.stop + 1 if noterange.stop.abstract in BLACK_NOTES else noterange.stop,
                )
            else:
                self.noterange = noterange
        else:
            # render 2 octaves by default
            self.noterange = NoteRange(SpecificNote('C', 0), SpecificNote('B', 1))

        self.white_notes = tuple(note for note in self.noterange if note.abstract in WHITE_NOTES)
        self.black_notes = tuple(note for note in self.noterange if note.abstract in BLACK_NOTES)
        width = ww * len(self.white_notes) if self.black_small else ww * len(self.noterange)
        self.size = width, wh
        self.elements: list[svg.Element] = []

        notes = self.white_notes + self.black_notes if black_small else self.noterange
        for note in notes:
            x, w, h, c, sx, sy = self.coord_helper(note)

            note_rect = svg.Rect(
                class_=['note', str(note)],
                x=x,
                y=0,
                width=w,
                height=h,
                fill=c.css_hex,
                stroke_width=1,
                stroke=BLACK_PALE.css_hex,
                onclick=self.note_onclicks.get(note, self.note_onclicks.get(note.abstract)),
            )
            # draw key

            if note_href := self.note_hrefs.get(note, self.note_hrefs.get(note.abstract)):
                self.elements.append(svg.A(href=note_href, elements=[note_rect]))
            else:
                self.elements.append(note_rect)

            # draw rectangle on top of note
            if rect_color := self.top_rect_colors.get(note, self.top_rect_colors.get(note.abstract)):
                self.elements.append(
                    svg.Rect(
                        class_=['top_rect', str(note)],
                        x=x,
                        y=0,
                        width=w,
                        height=top_rect_height,
                        fill=rect_color.css_hex,
                    ),
                )

            # draw squares on notes
            if payload := self.squares.get(note, self.squares.get(note.abstract)):
                sq_elements: list[svg.Element] = []
                sq_rect = svg.Rect(
                    class_=['square', str(note)],
                    x=sx,
                    y=sy,
                    width=square_size,
                    height=square_size,
                    fill=payload.get('fill_color', WHITE_BRIGHT).css_hex,
                    stroke_width=1,
                    stroke=payload.get('border_color', BLACK_BRIGHT).css_hex,
                )
                sq_elements.append(sq_rect)

                if text := payload.get('text'):
                    sq_text = svg.Text(
                        class_=['square', str(note)],
                        x=sx,
                        y=sy + square_size,
                        font_family='Menlo',
                        font_size=payload.get('text_size', 15),
                        fill=payload.get('text_color', BLACK_BRIGHT).css_hex,
                        text=text,
                    )
                    sq_elements.append(sq_text)
                self.elements.append(
                    svg.G(
                        class_=['square', str(note)],
                        onclick=payload.get('onclick'),
                        elements=sq_elements,
                    ),
                )

        # border around whole svg
        self.elements.append(svg.Rect(x=0, y=0, width=self.size[0] - 1, height=self.size[1] - 1, fill='none', stroke_width=1, stroke=BLACK_PALE.css_hex))

    def coord_helper(self, note: SpecificNote) -> tuple[int, int, int, Color, int, int]:
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
        c = self.note_colors.get(note, self.note_colors.get(note.abstract, note_color(note)))

        # def big_note():
        #     ...
        #
        # def small(note):
        #     ...

        if self.black_small:
            if note in self.white_notes:
                x = self.ww * self.white_notes.index(note)
                return x, self.ww, self.wh, c, (x + x + self.ww) // 2 - self.square_size // 2, self.wh - self.square_size - 5
            elif note in self.black_notes:
                x = self.ww * self.white_notes.index(note + 1) - self.bw // 2
                sx = self.ww * self.white_notes.index(note + 1) - self.square_size // 2
                return x, self.bw, self.bh, c, sx, self.bh - self.square_size - 3
            else:
                raise KeyError('unknown note')

        x = self.ww * self.noterange.index(note)
        return x, self.ww, self.wh, c, (x + x + self.ww) // 2 - self.square_size // 2, self.wh - self.square_size - 5

    # @functools.cache
    def _repr_svg_(self) -> str:
        _svg = svg.SVG(
            xmlns=None,
            width=self.size[0],
            height=self.size[1],
            elements=self.elements,
        )
        return str(_svg)
