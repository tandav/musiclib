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
        card: bool = False,
        title: str | None = None,
        subtitle: str | None = None,
        title_href: str | None = None,
        subtitle_href: str | None = None,
        background_color: str | None = None,
        classes: tuple[str, ...] = (),
        card_padding: tuple[int, int, int, int] = (30, 0, 0, 0),
        shadow_offset=2,
        border_radius=3,
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
        self.card = card
        if not card:
            self.card_padding = (0, 0, 0, 0)
        else:
            self.card_padding = card_padding
        self.shadow_offset = shadow_offset
        self.border_radius = border_radius

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
        height = wh
        width += self.card_padding[1] + self.card_padding[3]
        height += self.card_padding[0] + self.card_padding[2]
        self.size = width, height
        self.elements: list[svg.Element] = []

        notes = self.white_notes + self.black_notes if black_small else self.noterange

        if self.card:
            if title:
                text_title = svg.Text(
                    x=2,
                    y=0,
                    font_family='sans-serif',
                    font_size=15,
                    font_weight='bold',
                    fill=BLACK_BRIGHT.css_hex,
                    text=title,
                    dominant_baseline='text-before-edge',
                )
                if title_href:
                    self.elements.append(svg.A(href=title_href, elements=[text_title]))
                else:
                    self.elements.append(text_title)

            if subtitle:
                text_subtitle = svg.Text(
                    x=2,
                    y=30,
                    font_family='sans-serif',
                    font_size=12,
                    fill=BLACK_BRIGHT.css_hex,
                    text=subtitle,
                    dominant_baseline='text-after-edge',
                )
                if subtitle_href:
                    self.elements.append(svg.A(href=subtitle_href, elements=[text_subtitle]))
                else:
                    self.elements.append(text_subtitle)

        for note in notes:
            x, y, w, h, c, sx, sy = self.coord_helper(note)

            note_rect = svg.Rect(
                class_=['note', str(note)],
                x=x,
                y=y,
                width=w,
                height=h,
                fill=c.css_hex,
                stroke_width=1,
                stroke=BLACK_PALE.css_hex,
                onclick=self.note_onclicks.get(note, self.note_onclicks.get(note.abstract)),
                # stroke_linejoin='round', rx=3, ry=3,
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
                        y=y,
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

    def coord_helper(self, note: SpecificNote) -> tuple[int, int, int, int, Color, int, int]:
        """
        helper function which computes values for a given note

        Returns
        -------
        x: x coordinate of note rect
        y: y coordinate of note rect
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

        x0 = self.card_padding[3]
        y = self.card_padding[0]
        if self.black_small:
            if note in self.white_notes:
                x = x0 + self.ww * self.white_notes.index(note)
                return x, y, self.ww, self.wh, c, (x + x + self.ww) // 2 - self.square_size // 2, self.wh - self.square_size - 5
            elif note in self.black_notes:
                x = x0 + self.ww * self.white_notes.index(note + 1) - self.bw // 2
                sx = self.ww * self.white_notes.index(note + 1) - self.square_size // 2
                return x, y, self.bw, self.bh, c, sx, self.bh - self.square_size - 3
            else:
                raise KeyError('unknown note')

        x = x0 + self.ww * self.noterange.index(note)
        return x, y, self.ww, self.wh, c, (x + x + self.ww) // 2 - self.square_size // 2, self.wh - self.square_size - 5

    # @functools.cache
    def _repr_svg_(self) -> str:
        card_rect = svg.Rect(
            class_=['card_rect'],
            x=0,
            y=0,
            width=self.size[0],
            height=self.size[1],
            fill=WHITE_BRIGHT.css_hex,
            stroke_linejoin='round', rx=self.border_radius, ry=self.border_radius,
            stroke_width=1,
            stroke=BLACK_PALE.css_hex,
        )

        shadow_rect = svg.Rect(
            class_=['shadow_rect'],
            x=self.shadow_offset,
            y=self.shadow_offset,
            width=self.size[0],
            height=self.size[1],
            fill=BLACK_BRIGHT.css_hex,
            # fill='rgba(0,0,0,0.5)',
            # fill='rgba(0,0,0,0.5)',
            stroke_linejoin='round', rx=self.border_radius, ry=self.border_radius,
        )
        elements = [shadow_rect, card_rect] + self.elements
        _svg = svg.SVG(
            xmlns=None,
            width=self.size[0] + self.shadow_offset,
            height=self.size[1] + self.shadow_offset,
            elements=elements,
        )
        return str(_svg)
