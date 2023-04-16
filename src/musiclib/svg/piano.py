from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Literal
from typing import TypedDict

import svg

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

if TYPE_CHECKING:
    from colortool import Color


def note_color(note: Note | SpecificNote) -> Color:
    def _note_color(note: Note) -> Color:
        return WHITE_PALE if note in WHITE_NOTES else BLACK_PALE
    if isinstance(note, SpecificNote):
        return _note_color(note.abstract)
    if isinstance(note, Note):
        return _note_color(note)
    raise TypeError


class SquaresPayload(TypedDict, total=False):
    fill_color: Color
    border_color: Color
    text_color: Color
    text_size: Color
    text: str
    onclick: str


class Piano:
    def __init__(  # noqa: PLR0915,PLR0912,C901 # pylint: disable=too-many-branches,too-many-statements
        self,
        *,
        note_colors: dict[Note | SpecificNote, Color] | None = None,
        note_hrefs: dict[Note | SpecificNote, Color] | None = None,
        note_onclicks: dict[Note | SpecificNote, Color] | None = None,
        top_rect_colors: dict[Note | SpecificNote, Color] | None = None,
        squares: dict[Note | SpecificNote, SquaresPayload] | None = None,
        top_rect_height: int = 5,
        square_size: int = 12,
        square_white_offset: int = 5,
        square_black_offset: int = 3,
        ww: int = 18,  # white key width
        wh: int = 85,  # white key height
        noterange: NoteRange | None = None,
        black_small: bool = True,
        card: bool = True,
        title: str | None = None,
        subtitle: str | None = None,
        title_href: str | None = None,
        title_font_size: int = 15,
        subtitle_href: str | None = None,
        subtitle_font_size: int = 12,
        title_font_family: str = 'sans-serif',
        subtitle_font_family: str = 'sans-serif',
        square_font_family: str = 'monospace',
        title_y: int = 4,
        subtitle_y: int = 18,
        background_color: Color = WHITE_BRIGHT,
        classes: tuple[str, ...] = (),
        id: str | None = None,  # noqa: A002 # pylint: disable=redefined-builtin
        margin: tuple[int, int, int, int] = (3, 3, 3, 3),
        padding: tuple[int, int, int, int] = (30, 2, 2, 2),
        shadow_offset: int = 2,
        border_radius: int = 3,
        black_small_width_ratio: float = 0.6,
        black_small_height_ratio: float = 0.6,
        debug_rect: bool = False,
    ) -> None:
        self.ww = ww
        self.wh = wh
        if black_small:
            self.bw = int(ww * black_small_width_ratio)
            self.bh = int(wh * black_small_height_ratio)
        else:
            self.bw = ww
            self.bh = wh

        self.top_rect_height = top_rect_height
        self.square_size = square_size
        self.square_white_offset = square_white_offset
        self.square_black_offset = square_black_offset
        self.black_small = black_small
        self.note_colors = note_colors or {}
        self.top_rect_colors: dict[Note | SpecificNote, Color]
        self.top_rect_colors = top_rect_colors or {}
        self.squares = squares or {}
        self.note_hrefs = note_hrefs or {}
        self.note_onclicks = note_onclicks or {}
        self.card = card
        self.background_color = background_color
        self.classes = classes
        self.id = id
        self.title_font_size = title_font_size
        self.subtitle_font_size = subtitle_font_size
        self.square_font_family = square_font_family
        if not card:
            self.padding = (0, 0, 0, 0)
            self.margin = (0, 0, 0, 0)
        else:
            self.padding = padding
            self.margin = margin
        self.shadow_offset = shadow_offset
        self.border_radius = border_radius
        self.debug_rect = debug_rect
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
        self.piano_width = ww * len(self.white_notes) if self.black_small else ww * len(self.noterange)
        self.piano_height = wh
        self.elements: list[svg.Element] = []
        self.notes = self.white_notes + self.black_notes if black_small else self.noterange
        self.make_piano()

        if title_href is not None and title is None:
            raise ValueError('title_href requires title')

        if subtitle_href is not None and subtitle is None:
            raise ValueError('subtitle_href requires subtitle')

        if self.card:
            if title is not None:
                dominant_baseline: Literal['hanging', 'central']
                if subtitle is not None:
                    y = self.margin[0] + title_y
                    dominant_baseline = 'hanging'
                else:
                    y = (self.margin[0] + self.padding[0]) // 2
                    dominant_baseline = 'central'
                text_title = svg.Text(
                    x=self.margin[3] + self.padding[3], y=y, font_family=title_font_family, font_size=title_font_size,
                    font_weight='bold', fill=BLACK_BRIGHT.css_hex, text=title, dominant_baseline=dominant_baseline,
                )
                if title_href:
                    self.elements.append(svg.A(href=title_href, elements=[text_title]))
                else:
                    self.elements.append(text_title)

            if subtitle is not None:
                text_subtitle = svg.Text(
                    x=self.margin[3] + self.padding[3],
                    y=self.margin[0] + subtitle_y,
                    font_family=subtitle_font_family,
                    font_size=subtitle_font_size,
                    fill=BLACK_BRIGHT.css_hex,
                    text=subtitle,
                    dominant_baseline='hanging',
                )
                if subtitle_href is not None:
                    self.elements.append(svg.A(href=subtitle_href, elements=[text_subtitle]))
                else:
                    self.elements.append(text_subtitle)

    def x(self, value: int) -> int:
        return self.margin[3] + self.padding[3] + value

    def y(self, value: int) -> int:
        return self.margin[0] + self.padding[0] + value

    def make_piano(self) -> None:
        for note in self.notes:
            x, y, w, h, c, sx, sy = self.coord_helper(note)

            note_rect = svg.Rect(
                class_=[
                    'note',
                    str(note),
                ],
                x=x,
                y=y,
                width=w,
                height=h,
                fill=c.css_hex,
                stroke_width=1,
                stroke=BLACK_PALE.css_hex,
                onclick=self.note_onclicks.get(
                    note,
                    self.note_onclicks.get(
                        note.abstract,
                    ),
                ),
            )
            # draw key

            if note_href := self.note_hrefs.get(note, self.note_hrefs.get(note.abstract)):
                self.elements.append(svg.A(href=note_href, elements=[note_rect]))
            else:
                self.elements.append(note_rect)

            # draw rectangle on top of note
            if rect_color := self.top_rect_colors.get(note, self.top_rect_colors.get(note.abstract)):
                self.elements.append(svg.Rect(class_=['top_rect', str(note)], x=x, y=y, width=w, height=self.top_rect_height, fill=rect_color.css_hex))

            # draw squares on notes
            if payload := self.squares.get(note, self.squares.get(note.abstract)):
                sq_elements: list[svg.Element] = []
                sq_rect = svg.Rect(
                    class_=[
                        'square',
                        str(note),
                    ],
                    x=sx,
                    y=sy,
                    width=self.square_size,
                    height=self.square_size,
                    fill=payload.get(
                        'fill_color',
                        WHITE_BRIGHT,
                    ).css_hex,
                    stroke_width=1,
                    stroke=payload.get(
                        'border_color',
                        BLACK_BRIGHT,
                    ).css_hex,
                )
                sq_elements.append(sq_rect)

                if text := payload.get('text'):
                    sq_text = svg.Text(
                        class_=[
                            'square',
                            str(note),
                        ],
                        x=sx + self.square_size // 2,
                        y=sy + self.square_size // 2,
                        font_family=self.square_font_family,
                        font_size=payload.get(
                            'text_size',
                            self.title_font_size,
                        ),
                        fill=payload.get(
                            'text_color',
                            BLACK_BRIGHT,
                        ).css_hex,
                        text=text,
                        text_anchor='middle',
                        dominant_baseline='central',
                    )
                    sq_elements.append(sq_text)
                self.elements.append(svg.G(class_=['square', str(note)], onclick=payload.get('onclick'), elements=sq_elements))

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
        x0 = self.x(0)
        y = self.y(0)
        if self.black_small:
            if note in self.white_notes:
                x = x0 + self.ww * self.white_notes.index(note)
                sx = (x + x + self.ww) // 2 - self.square_size // 2
                sy = self.y(self.wh - self.square_size - self.square_white_offset)
                return x, y, self.ww, self.wh, c, sx, sy
            if note in self.black_notes:
                x = x0 + self.ww * self.white_notes.index(note + 1) - self.bw // 2
                sx = self.x(self.ww * self.white_notes.index(note + 1) - self.square_size // 2)
                sy = self.y(self.bh - self.square_size - self.square_black_offset)
                return x, y, self.bw, self.bh, c, sx, sy

        x = self.ww * self.noterange.index(note)
        sx = self.x((x + x + self.ww) // 2 - self.square_size // 2)
        sy = self.y(self.wh - self.square_size - self.square_white_offset)
        return self.x(x), y, self.ww, self.wh, c, sx, sy

    # @functools.cache
    def _repr_svg_(self) -> str:
        w_pp = self.padding[1] + self.padding[3] + self.piano_width
        h_pp = self.padding[0] + self.padding[2] + self.piano_height
        svg_width = self.margin[1] + self.margin[3] + w_pp + self.shadow_offset
        svg_height = self.margin[0] + self.margin[2] + h_pp + self.shadow_offset
        elements: list[svg.Element] = []
        if self.debug_rect:
            debug_rect = svg.Rect(class_=['debug_rect'], x=0, y=0, width=svg_width, height=svg_height, fill='red')
            elements.append(debug_rect)
        if self.card:
            card_rect = svg.Rect(
                class_=['card_rect'],
                x=self.margin[3],
                y=self.margin[0],
                width=w_pp,
                height=h_pp,
                fill=self.background_color.css_hex,
                rx=self.border_radius,
                ry=self.border_radius,
                stroke_width=1,
                stroke=BLACK_PALE.css_hex,
            )
            shadow_rect = svg.Rect(
                class_=['shadow_rect'],
                x=self.margin[3] +
                self.shadow_offset,
                y=self.margin[0] +
                self.shadow_offset,
                width=w_pp,
                height=h_pp,
                fill=BLACK_BRIGHT.css_hex,
                rx=self.border_radius,
                ry=self.border_radius,
            )
            elements += [shadow_rect, card_rect]
        elements += self.elements
        _svg = svg.SVG(width=svg_width, height=svg_height, elements=elements, class_=list(self.classes), id=self.id)
        return str(_svg)
