import abc
import cmath
import math
import uuid
import svg
from colortool import Color

from musiclib import config
from musiclib.interval import AbstractInterval
import numpy as np


class IsomorphicKeyboard(abc.ABC):
    """
    https://notes.tandav.me/notes/3548
    """
    def __init__(
        self,
        interval_colors: dict[AbstractInterval | int, Color] | None = None,
        interval_parts_colors: dict[int, dict[int, Color]] | None = None,
        interval_text: dict[AbstractInterval | int, str] | str | None = 'abstract_interval',
        interval_strokes: dict[AbstractInterval | int, Color] | None = None,
        n_rows: int | None = 7,
        n_cols: int = 13,
        ax0_step: int = 0,
        ax1_step: int = 2,
        radius: int = 30,
        font_size_radius_ratio: float = 0.5,
        round_points: bool = True,
        rotated: bool = False,
        default_key_color: Color = config.BLACK_PALE,
    ) -> None:
        self.radius = radius
        self.elements: list[svg.Element] = []
        self.interval_colors = interval_colors or {}
        self.interval_parts_colors = interval_parts_colors or {}
        self.interval_text = interval_text
        self.font_size = int(radius * font_size_radius_ratio)
        self.round_points = round_points
        self.rotated = rotated
        self.interval_strokes = interval_strokes or {}
        self.defs = svg.Defs(elements=[])
        self.elements.append(self.defs)
        self.id_suffix = str(uuid.uuid4()).split('-')[0]
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.ax0_step = ax0_step
        self.ax1_step = ax1_step
        self.default_key_color = default_key_color
        if n_rows < 0:
            raise ValueError(f'n_rows={n_rows} must be positive')
        if n_cols < 0:
            raise ValueError(f'n_cols={n_cols} must be positive')
        if n_rows == 0 or n_cols == 0:
            return
        self.add_keys()

    @abc.abstractmethod
    def add_keys(self) -> None:
        ...

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

    @abc.abstractmethod
    def row_col_to_interval(self, row: float, col: float) -> int:
        ...

    def add_key(self, row: float, col: float) -> None:
        # interval = round(col)
        interval = self.row_col_to_interval(row, col)
        x = self.col_to_x(col)
        y = self.row_to_y(row)
        # print(f'row={row}, col={col}, interval={interval}, x={x}, y={y}')
        color = self.interval_colors.get(interval, self.interval_colors.get(AbstractInterval(interval), self.default_key_color))
        points = self.key_points(x, y, self.radius)
        if self.round_points:
            points = [round(p, 1) for p in points]

        polygon_kw = dict(
            class_=['polygon-colored'],
            fill=color.css_hex,
            points=points,
            # clip_path='url(#key-clip)',
        )
        id_ = f'row-{row}-col-{col}-{self.id_suffix}'
        self.defs.elements.append(svg.ClipPath(id=id_, elements=[svg.Polygon(**polygon_kw)]))
        stroke = self.interval_strokes.get(interval, self.interval_strokes.get(AbstractInterval(interval), None))
        if stroke is not None:
            polygon_kw['stroke'] = stroke['stroke'].css_hex
            polygon_kw['stroke_width'] = stroke.get('stroke_width', 1) * 2
            polygon_kw['clip_path'] = f'url(#{id_})'
        self.elements.append(svg.Polygon(**polygon_kw))

#       self.texts.append(svg.Text(x=x, y=y, text=f'{x:.1f}{y:.1f}', font_size=10, text_anchor='middle', dominant_baseline='middle'))
#       self.texts.append(svg.Text(x=x, y=y, text=f'{row}, {col}', font_size=10, text_anchor='middle', dominant_baseline='middle'))

        if self.interval_text is None:
            text = None
        elif isinstance(self.interval_text, dict):
            text = self.interval_text.get(interval, self.interval_text.get(AbstractInterval(interval), None))
        elif isinstance(self.interval_text, str):
            if self.interval_text == 'interval':
                text = np.base_repr(interval, base=12)
            elif self.interval_text == 'abstract_interval':
                text = str(AbstractInterval(interval))
            else:
                raise NotImplementedError(f'invalid self.interval_text={self.interval_text}, can be None, dict or "interval" or "abstract_interval"')
        else:
            raise NotImplementedError(f'invalid self.interval_text={self.interval_text}')

        if text is not None:
            self.elements.append(svg.Text(
                x=x,
                y=y,
                text=text,
                # text=f'{row} {col}│{text}',
                font_size=self.font_size,
                font_family='monospace',
                text_anchor='middle',
                dominant_baseline='middle',
                pointer_events='none',  # probably not needed when using event.preventDefault() on transparent polygon
                # onclick=f"play_note('{note}')",
                # onmousedown=f"midi_message('note_on', '{note}')",
                # onmouseup=f"midi_message('note_off', '{note}')",
            ))

        # transparent polygon on top for mouse events
        # polygon = svg.Polygon(
        #     class_=['polygon-transparent'],
        #     points=points,
        #     fill=Color.from_rgba_int((0, 0, 0, 0)).css_rgba,
        #     # stroke='black',
        #     # stroke_width=1,
        #     # onmousedown=f"midi_message('note_on', '{note}')",
        #     # onmouseup=f"midi_message('note_off', '{note}')",
        # )
        # self.elements.append(polygon)

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
