from __future__ import annotations

from typing import TypedDict
from xml.etree import ElementTree

import colortool

from musictool.config import BLACK_BRIGHT
from musictool.config import BLACK_PALE
from musictool.config import WHITE_BRIGHT
from musictool.config import WHITE_PALE
from musictool.note import BLACK_NOTES
from musictool.note import WHITE_NOTES
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.noterange import CHROMATIC_NOTESET
from musictool.noterange import NoteRange


def note_color(note: Note | SpecificNote) -> int:
    def _note_color(note: Note) -> int:
        return WHITE_PALE if note in WHITE_NOTES else BLACK_PALE
    if isinstance(note, SpecificNote):
        return _note_color(note.abstract)
    elif isinstance(note, Note):
        return _note_color(note)
    else:
        raise TypeError


class SquaresPayload(TypedDict, total=False):
    fill_color: int
    border_color: int
    text_color: int
    text_size: str
    text: str
    onclick: str


class Piano:
    def __init__(
        self,
        note_colors: dict[Note | SpecificNote, int] | None = None,
        note_hrefs: dict[Note | SpecificNote, str] | None = None,
        note_onclicks: dict[Note | SpecificNote, str] | None = None,
        top_rect_colors: dict[Note, int] | dict[SpecificNote, int] | None = None,
        # top_rect_colors: TopRectDict | None = None,
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

        self.top_rect_colors: dict[Note, int] | dict[SpecificNote, int]
        if top_rect_colors is None:
            self.top_rect_colors = {}  # type: ignore
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
        self.rects = []

        notes = self.white_notes + self.black_notes if black_small else self.noterange
        for note in notes:
            x, w, h, c, sx, sy = self.coord_helper(note)

            # draw key
            if note_onclick := self.note_onclicks.get(note, self.note_onclicks.get(note.abstract)):
                note_onclick = f' onclick="{note_onclick}"'
            else:
                note_onclick = ''

            note_rect = f"""<rect class='note' note='{note}' x='{x}' y='0' width='{w}' height='{h}' style='fill:{colortool.css_hex(c)};stroke-width:1;stroke:{colortool.css_hex(BLACK_PALE)}'{note_onclick}/>"""
            if note_href := self.note_hrefs.get(note, self.note_hrefs.get(note.abstract)):
                note_rect = f"<a href='{note_href}'>{note_rect}</a>"
            self.rects.append(note_rect)

            # draw rectangle on top of note
            if rect_color := self.top_rect_colors.get(note, self.top_rect_colors.get(note.abstract)):
                self.rects.append(f"""<rect class='top_rect' note='{note}' x='{x}' y='0' width='{w}' height='{top_rect_height}' style='fill:{colortool.css_hex(rect_color)};'/>""")

            # draw squares on notes
            if payload := self.squares.get(note, self.squares.get(note.abstract)):
                fill_color = colortool.css_hex(payload.get('fill_color', WHITE_BRIGHT))
                border_color = colortool.css_hex(payload.get('border_color', BLACK_BRIGHT))

                onclick = payload.get('onclick')
                onclick = f" onclick='{onclick}'" if onclick else ''

                rect = f"<rect class='square' note='{note}' x='{sx}' y='{sy}' width='{square_size}' height='{square_size}' style='fill:{fill_color};stroke-width:1;stroke:{border_color}'/>"

                if text := payload.get('text'):
                    text_color = colortool.css_hex(payload.get('text_color', BLACK_BRIGHT))
                    text_size = payload.get('text_size', '15')
                    rect += f"<text class='square' note='{note}' x='{sx}' y='{sy + square_size}' font-family=\"Menlo\" font-size='{text_size}' style='fill:{text_color}'>{text}</text>"

                self.rects.append(f"""
                    <g class='square' note='{note}'{onclick}>
                        {rect}
                    </g>
                """)

        # border around whole svg
        self.rects.append(f"<rect x='0' y='0' width='{self.size[0] - 1}' height='{self.size[1] - 1}' style='fill:none;stroke-width:1;stroke:{colortool.css_hex(BLACK_PALE)}'/>")

    def coord_helper(self, note: SpecificNote) -> tuple[int, int, int, int, int, int]:
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

    def __repr__(self):
        return 'Piano'

    @staticmethod
    def pretty_print(svg: str) -> str:
        tree = ElementTree.fromstring(svg)
        ElementTree.indent(tree, level=0)
        return ElementTree.tostring(tree, encoding='unicode')

    def _repr_svg_(self, pretty: bool = True) -> str:
        rects = '\n'.join(self.rects)
        svg = f"""
        <svg width='{self.size[0]}' height='{self.size[1]}'>
        {rects}
        </svg>
        """
        return Piano.pretty_print(svg) if pretty else svg
