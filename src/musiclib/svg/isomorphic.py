"""
https://en.wikipedia.org/wiki/Jankó_keyboard
https://shiverware.com/musixpro/
http://rainboard.shiverware.com/Main_Page
http://rainboard.shiverware.com/Research
https://news.ycombinator.com/item?id=37620474
"""
import abc
import cmath
import math

import svg
from colortool import Color

from musiclib import config
from musiclib.note import SpecificNote
from musiclib.note import Note
from musiclib.pitch import Pitch
import numpy as np

C4 = SpecificNote('C', 4)


class IsomorphicKeyboard(abc.ABC):
    def __init__(
        self,
        interval_colors: dict[int, Color] | None = None,
        n_rows: int = 7,
        n_cols: int = 13,
        radius: int = 30,
        font_size_radius_ratio: float = 0.5,
        round_points: bool = True,
        interval_parts_colors: dict[int, dict[int, Color]] | None = None,
    ) -> None:
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.radius = radius
        self.elements: list[svg.Element] = []
        self.interval_colors = interval_colors or {}
        # self.pitch = Pitch(origin_note=origin_note)
        self.font_size = int(radius * font_size_radius_ratio)
        self.round_points = round_points
        self.interval_parts_colors = interval_parts_colors or {}

        for row in range(-1, n_rows + 1):
            for col in range(-2, n_cols + 1, 2):
                self.add_key(row, col + row % 2)

    @abc.abstractmethod
    def col_to_x(self, col: float) -> float:
        ...

    @abc.abstractmethod
    def row_to_y(self, row: float) -> float:
        ...

    @property
    @abc.abstractmethod
    def width(self) -> int:
        ...

    @property
    @abc.abstractmethod
    def height(self) -> int:
        ...

    def add_key(self, row: float, col: float) -> None:
        interval = round(col)
        x = self.col_to_x(col)
        y = self.row_to_y(row)
        color = self.interval_colors.get(interval, config.BLACK_PALE)
        points = self.key_points(x, y, self.radius)
        print(len(points))
        if self.round_points:
            points = [round(p, 1) for p in points]

        polygon = svg.Polygon(
            class_=['polygon-colored'],
            fill=color.css_hex,
            # stroke='black',
            # stroke_width=1,
            points=points,
        )
        self.elements.append(polygon)
#       self.texts.append(svg.Text(x=x, y=y, text=f'{x:.1f}{y:.1f}', font_size=10, text_anchor='middle', dominant_baseline='middle'))
#       self.texts.append(svg.Text(x=x, y=y, text=f'{row}, {col}', font_size=10, text_anchor='middle', dominant_baseline='middle'))

        text = svg.Text(
            x=x,
            y=y,
            text=f'{np.base_repr(interval, base=12)}',
            font_size=self.font_size,
            font_family='monospace',
            text_anchor='middle',
            dominant_baseline='middle',
            pointer_events='none',  # probably not needed when using event.preventDefault() on transparent polygon
            # onclick=f"play_note('{note}')",
            # onmousedown=f"midi_message('note_on', '{note}')",
            # onmouseup=f"midi_message('note_off', '{note}')",
        )
        # text.note = str(note)
        # text.note_midi = note.i
        self.elements.append(text)

        # transparent polygon on top for mouse events
        polygon = svg.Polygon(
            class_=['polygon-transparent'],
            points=points,
            fill=Color.from_rgba_int((0, 0, 0, 0)).css_rgba,
            # stroke='black',
            # stroke_width=1,
            # onmousedown=f"midi_message('note_on', '{note}')",
            # onmouseup=f"midi_message('note_off', '{note}')",
        )
        # polygon.note = str(note)
        # polygon.note_midi = note.i
        self.elements.append(polygon)

        for part, color in self.interval_parts_colors.get(interval, {}).items():
            self.elements.append(
                svg.Polygon(
                    points=self.key_part_points(x, y, part),
                    fill=Color.random().css_hex,
                ),
            )


    @abc.abstractmethod
    def key_points(self, x: float, y: float) -> list[float]:
        ...

    @abc.abstractmethod
    def key_part_points(self, x: float, y: float, part: int) -> list[float]:
        ...

    @property
    def svg(self) -> svg.SVG:
        return svg.SVG(
            width=self.width,
            height=self.height,
            elements=self.elements,
        )

    def _repr_svg_(self) -> str:
        return str(self.svg)


class Square(IsomorphicKeyboard):
    def col_to_x(self, col: float) -> float:
        return self.radius * (col + 1)

    def row_to_y(self, row: float) -> float:
        return self.radius * (row + 1)

    @property
    def width(self) -> int:
        return int(self.col_to_x(self.n_cols))

    @property
    def height(self) -> int:
        return int(self.row_to_y(self.n_rows))
    
    @property
    def h(self):
        return 2 ** 0.5 / 2 * self.radius

    @staticmethod
    def vertex(x: float, y: float, radius: float, i: int, phase: float = 0) -> tuple[float, float]:
        phase_start = 2 * math.pi / 2
        theta = phase_start + phase + 2 * math.pi * i / 4
        p = complex(y, x) + radius * cmath.exp(1j * theta)
        return p.imag, p.real

    def key_points(self, x: float, y: float, radius: float) -> list[float]:
        points = []
        for i in range(4):
            points += self.vertex(x, y, radius, i)
        return points
    
    def key_part_points(self, x: float, y: float, part: int) -> list[float]:
        i = part // 2
        return [
            x, 
            y, 
            *self.vertex(x, y, self.h, i, phase=2 * math.pi / 8), # todo: support 12 parts
            *self.vertex(x, y, self.radius, i + part % 2),
        ]


class Hex(IsomorphicKeyboard):
    def col_to_x(self, col: float) -> float:
        return self.h * (col + 1)

    def row_to_y(self, row: float) -> float:
        return self.radius * (row * 1.5 + 1)

    @property
    def width(self) -> int:
        return int(self.col_to_x(self.n_cols))

    @property
    def height(self) -> int:
        return int(self.row_to_y(self.n_rows) - 0.5 * self.radius)
    
    @property
    def h(self):
        return 3 ** 0.5 / 2 * self.radius

    @staticmethod
    def vertex(x: float, y: float, radius: float, i: int, phase: float = 0) -> tuple[float, float]:
        phase_start = 2 * math.pi / 2
        theta = phase_start + phase + 2 * math.pi * i / 6
        p = complex(y, x) + radius * cmath.exp(1j * theta)
        return p.imag, p.real

    def key_points(self, x: float, y: float, radius: float) -> list[float]:
        points = []
        for i in range(7):
            points += self.vertex(x, y, radius, i)
        return points
    
    def key_part_points(self, x: float, y: float, part: int) -> list[float]:
        i = part // 2
        return [
            x, 
            y, 
            *self.vertex(x, y, self.h, i, phase=2 * math.pi / 12),
            *self.vertex(x, y, self.radius, i + part % 2),
        ]


class Piano(IsomorphicKeyboard):
    def col_to_x(self, col: float) -> float:
        return self.radius * (col + 1)

    def row_to_y(self, row: float) -> float:
        return self.radius * (row + 1)

    @property
    def width(self) -> int:
        return int(self.col_to_x(self.n_cols))

    @property
    def height(self) -> int:
        return int(self.row_to_y(self.n_rows))

    @staticmethod
    def key_points(x: float, y: float, radius: float) -> list[float]:
        points = []
        for i in range(4):
            theta = math.pi * i / 2
            p = complex(y, x) + radius * cmath.exp(1j * theta)
            points += [p.imag, p.real]
        return points
