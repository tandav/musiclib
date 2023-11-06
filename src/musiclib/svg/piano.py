from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypedDict

import svg

from musiclib import config
from musiclib.note import Note
from musiclib.note import SpecificNote
from musiclib.noteset import SpecificNoteSet

if TYPE_CHECKING:
    from colortool import Color


def note_color(note: Note | SpecificNote) -> Color:
    def _note_color(note: Note) -> Color:
        return config.BLACK_PALE if note.is_black else config.WHITE_PALE
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
    font_family: str


class RegularPiano:
    def __init__(
        self,
        *,
        note_colors: dict[Note | SpecificNote, Color] | None = None,
        note_hrefs: dict[Note | SpecificNote, Color] | None = None,
        note_onclicks: dict[Note | SpecificNote, Color] | None = None,
        top_rect_colors: dict[Note | SpecificNote, Color] | None = None,
        squares: dict[Note | SpecificNote, SquaresPayload] | None = None,
        start_stop: tuple[SpecificNote, SpecificNote] | None = None,
        ww: int = 18,  # white key width
        wh: int = 85,  # white key height
        black_small_width_ratio: float = 0.6,
        black_small_height_ratio: float = 0.6,
        top_rect_height: int = 5,
        square_size: int = 12,
        square_white_offset: int = 5,
        square_black_offset: int = 3,
        class_: tuple[str, ...] = (),
        id: str | None = None,  # noqa: A002 # pylint: disable=redefined-builtin
    ) -> None:
        self.note_colors = note_colors or {}
        self.note_hrefs = note_hrefs or {}
        self.note_onclicks = note_onclicks or {}
        self.top_rect_colors: dict[Note | SpecificNote, Color] = top_rect_colors or {}
        self.squares = squares or {}
        self.ww = ww
        self.wh = wh
        self.bw = int(ww * black_small_width_ratio)
        self.bh = int(wh * black_small_height_ratio)
        self.top_rect_height = top_rect_height
        self.square_size = square_size
        self.square_white_offset = square_white_offset
        self.square_black_offset = square_black_offset
        self.class_ = class_
        self.id = id
        if start_stop is None:
            # render 2 octaves by default
            self.sns = SpecificNoteSet.from_noterange(SpecificNote('C', 0), SpecificNote('B', 1))
        else:
            # ensure that start and stop are white keys
            self.sns = SpecificNoteSet.from_noterange(
                start=start_stop[0] - 1 if start_stop[0].is_black else start_stop[0],
                stop=start_stop[1] + 1 if start_stop[1].abstract.is_black else start_stop[1],
            )
        self.white_notes = tuple(note for note in self.sns if not note.is_black)
        self.black_notes = tuple(note for note in self.sns if note.is_black)
        self.width = ww * len(self.white_notes)
        self.height = wh
        self.elements: list[svg.Element] = []
        self.notes = self.white_notes + self.black_notes
        self.make_piano()

    def make_piano(self) -> None:
        for note in self.notes:
            x, y, w, h, c, sx, sy = self.coord_helper(note)

            note_rect = svg.Rect(
                class_=['note', str(note)],
                x=x,
                y=y,
                width=w,
                height=h,
                fill=c.css_hex,
                stroke_width=1,
                stroke=config.BLACK_PALE.css_hex,
                onclick=self.note_onclicks.get(note, self.note_onclicks.get(note.abstract)),
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
                    class_=['square', str(note)],
                    x=sx,
                    y=sy,
                    width=self.square_size,
                    height=self.square_size,
                    fill=payload.get('fill_color', config.WHITE_BRIGHT).css_hex,
                    stroke_width=1,
                    stroke=payload.get('border_color', config.BLACK_BRIGHT).css_hex,
                )
                sq_elements.append(sq_rect)

                if text := payload.get('text'):
                    sq_text = svg.Text(
                        class_=['square', str(note)],
                        x=sx + self.square_size // 2,
                        y=sy + self.square_size // 2,
                        font_family=payload.get('square_font_family', 'monospace'),  # type: ignore[arg-type]
                        font_size=payload.get('text_size', 15),
                        fill=payload.get('text_color', config.BLACK_BRIGHT).css_hex,
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
        x0 = 0
        y = 0
        if note in self.white_notes:
            x = x0 + self.ww * self.white_notes.index(note)
            sx = (x + x + self.ww) // 2 - self.square_size // 2
            sy = self.wh - self.square_size - self.square_white_offset
            return x, y, self.ww, self.wh, c, sx, sy
        if note in self.black_notes:
            x = x0 + self.ww * self.white_notes.index(note + 1) - self.bw // 2
            sx = self.ww * self.white_notes.index(note + 1) - self.square_size // 2
            sy = self.bh - self.square_size - self.square_black_offset
            return x, y, self.bw, self.bh, c, sx, sy
        raise ValueError(f'note {note} is not in {self.sns}')

    @property
    def svg(self) -> svg.SVG:
        return svg.SVG(width=self.width, height=self.height, elements=self.elements, class_=list(self.class_), id=self.id)

    def _repr_svg_(self) -> str:
        return str(self.svg)
