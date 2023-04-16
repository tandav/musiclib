import cmath
import math

import svg

from musiclib import config
from musiclib.note import SpecificNote
from musiclib.pitch import Pitch
from musiclib.scale import Scale

C_major = Scale.from_name('C', 'major')
C4 = SpecificNote('C', 4)


class JankoSquare:
    """https://en.wikipedia.org/wiki/Jankó_keyboard"""

    def __init__(
        self,
        scale: Scale = C_major,
        origin_note: SpecificNote = C4,
        radius: int = 30,
        n_rows: int = 7,
        n_cols: int = 13,
    ) -> None:
        self.width = 2 * n_cols * radius
        self.height = 2 * n_rows * radius
        self.radius = radius
        self.elements: list[svg.Element] = []
        self.scale = scale
        self.origin_note = origin_note
        self.pitch = Pitch(origin_note=origin_note)

        for j in range(-1, n_rows * 2):
            for i in range(-2, n_cols * 2, 2):
                self.add_note(j, i + j % 2)

    def add_note(
        self,
        j: float,
        i: float,
        font_size: int = 15,
    ) -> None:
        note = self.pitch.i_to_note(i)
        x = self.radius + self.radius * i
        y = self.radius + self.radius * j

        if note.abstract in self.scale.note_scales:
            color = config.scale_colors[self.scale.note_scales[note.abstract]]
        else:
            color = config.BLACK_PALE

        polygon = svg.Polygon(
            class_=['polygon-colored'],
            fill=color.css_hex,
            stroke='black',
            stroke_width=1,
            points=self.square_points(x, y, self.radius),  # type: ignore[arg-type]
        )
        self.elements.append(polygon)
        text = svg.Text(
            x=x,
            y=y,
            text=str(note),
            font_size=font_size,
            font_family='monospace',
            text_anchor='middle',
            dominant_baseline='middle',
        )
        text.note = str(note)  # type: ignore[attr-defined]
        text.note_midi = note.i  # type: ignore[attr-defined]
        self.elements.append(text)

    @staticmethod
    def square_points(x: float, y: float, radius: float) -> list[float]:
        points = []
        for i in range(4):
            theta = math.pi * i / 2
            p = complex(y, x) + radius * cmath.exp(1j * theta)
            points += [p.imag, p.real]
        return points

    def _repr_svg_(self) -> str:
        s = svg.SVG(
            width=self.width,
            height=self.height,
            elements=self.elements,
        )
        return str(s)
