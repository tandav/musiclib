import abc
import uuid
from collections.abc import Iterable
from typing import Literal

import svg
from colortool import Color

from musiclib import config
from musiclib.interval import AbstractInterval
from musiclib.svg.isomorphic.text import TEXT_CALLABLE
from musiclib.svg.isomorphic.text import middle_text_kw_abstract_interval
from musiclib.util.etc import are_mutually_exclusive
from musiclib.util.etc import is_any_not_none
from musiclib.util.etc import vertex


class IsomorphicKeyboard(abc.ABC):
    """
    https://gitlab.tandav.me/tandav/notes/-/issues/3581
    """

    def __init__(
        self,
        *,
        interval_colors: dict[AbstractInterval | int, Color] | None = None,
        interval_strokes: dict[AbstractInterval | int, Color] | None = None,
        interval_radial_parts_colors: dict[AbstractInterval | int, dict[int, Color]] | None = None,
        interval_horizontal_parts_colors: dict[AbstractInterval | int, dict[int, Color]] | None = None,
        interval_vertical_parts_colors: dict[AbstractInterval | int, dict[int, Color]] | None = None,
        n_parts: int | None = None,
        interval_text: TEXT_CALLABLE | None = middle_text_kw_abstract_interval,
        interval_subtext: TEXT_CALLABLE | None = None,
        interval_extra_texts: Iterable[TEXT_CALLABLE] = (),
        n_rows: int | None = 7,
        n_cols: int | None = 13,
        row_range: range | None = None,
        col_range: range | None = None,
        ax0_step: int = 2,
        ax1_step: int = 1,
        radius: int = 18,
        offset_x: int = 0,
        offset_y: int = 0,
        round_points: bool = True,
        rotated: bool = False,
        default_key_color: Color = config.BLACK_PALE,
    ) -> None:
        self.rotated = rotated
        self.validate_dimensions(n_rows, n_cols, row_range, col_range)
        if self.n_rows == 0 or self.n_cols == 0:
            return
        self.radius = radius
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.elements: list[svg.Element] = []
        self.interval_colors = interval_colors or {}

        self.validate_parts_colors(
            interval_radial_parts_colors,
            interval_horizontal_parts_colors,
            interval_vertical_parts_colors,
            n_parts,
        )
        self.interval_text = interval_text
        self.interval_subtext = interval_subtext
        self.interval_extra_texts = interval_extra_texts
        self.round_points = round_points
        self.interval_strokes = interval_strokes or {}
        self.defs = svg.Defs(elements=[])
        self.elements.append(self.defs)
        self.id_suffix = str(uuid.uuid4()).split('-', maxsplit=1)[0]
        self.ax0_step = ax0_step
        self.ax1_step = ax1_step
        self.default_key_color = default_key_color
        self.add_keys()

    def validate_parts_colors(
        self,
        interval_radial_parts_colors: dict[AbstractInterval | int, dict[int, Color]] | None = None,
        interval_horizontal_parts_colors: dict[AbstractInterval | int, dict[int, Color]] | None = None,
        interval_vertical_parts_colors: dict[AbstractInterval | int, dict[int, Color]] | None = None,
        n_parts: int | None = None,
    ) -> None:
        if not are_mutually_exclusive(
            interval_radial_parts_colors,
            interval_horizontal_parts_colors,
            interval_vertical_parts_colors,
        ):
            raise ValueError('Exactly one of interval_radial_parts_colors, interval_horizontal_parts_colors, interval_vertical_parts_colors must be provided')

        if is_any_not_none(
            interval_radial_parts_colors,
            interval_horizontal_parts_colors,
            interval_vertical_parts_colors,
        ) and n_parts is None:
            raise ValueError('n_parts must be provided if any of interval_radial_parts_colors, interval_horizontal_parts_colors, interval_vertical_parts_colors is provided')

        self.interval_radial_parts_colors = interval_radial_parts_colors
        self.interval_horizontal_parts_colors = interval_horizontal_parts_colors
        self.interval_vertical_parts_colors = interval_vertical_parts_colors
        self.n_parts = n_parts

    def validate_dimensions(
        self,
        n_rows: int | None,
        n_cols: int | None,
        row_range: range | None,
        col_range: range | None,
    ) -> None:
        if not are_mutually_exclusive(n_rows, row_range):
            raise ValueError('Exactly one of n_rows or row_range must be provided')
        if not are_mutually_exclusive(n_cols, col_range):
            raise ValueError('Exactly one of n_cols or col_range must be provided')

        self.row_range = row_range
        self.col_range = col_range

        if n_rows is None:
            if row_range is None:
                raise ValueError('Exactly one of n_rows or row_range must be provided')
            self.n_rows = len(row_range)
        elif n_rows < 0:
            raise ValueError(f'n_rows={n_rows} must be positive')
        else:
            self.n_rows = n_rows

        if n_cols is None:
            if col_range is None:
                raise ValueError('Exactly one of n_cols or col_range must be provided')
            self.n_cols = len(col_range)
        elif n_cols < 0:
            raise ValueError(f'n_cols={n_cols} must be positive')
        else:
            self.n_cols = n_cols

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

    def add_parts(self, interval: int, x: float, y: float, id_: str) -> None:  # noqa: C901
        if self.n_parts is None:
            raise ValueError('n_parts must be provided if any of interval_radial_parts_colors, interval_horizontal_parts_colors, interval_vertical_parts_colors is provided')
        if self.interval_radial_parts_colors is not None:
            for part, color in self.interval_radial_parts_colors.get(interval, self.interval_radial_parts_colors.get(AbstractInterval(interval), {})).items():
                if part >= self.n_parts:
                    raise ValueError(f'part={part} must be less than n_parts={self.n_parts}')
                p0 = vertex(x, y, self.radius, self.n_parts, part)
                p1 = vertex(x, y, self.radius, self.n_parts, (part + 1) % self.n_parts)
                self.elements.append(
                    svg.Path(
                        d=[
                            svg.MoveTo(x, y),
                            svg.LineTo(*p0),
                            svg.Arc(rx=self.radius, ry=self.radius, angle=360 / self.n_parts, large_arc=False, sweep=False, x=p1[0], y=p1[1]),
                            svg.ClosePath(),
                        ],
                        fill=color.css_hex,
                        clip_path=f'url(#{id_})',
                    ),
                )

        if self.interval_horizontal_parts_colors is not None:
            for part, color in self.interval_horizontal_parts_colors.get(interval, self.interval_horizontal_parts_colors.get(AbstractInterval(interval), {})).items():
                if part >= self.n_parts:
                    raise ValueError(f'part={part} must be less than n_parts={self.n_parts}')
                self.elements.append(
                    svg.Rect(
                        **self.ax_split_part_rect_coordinates(x, y, part, 'horizontal'),  # type: ignore[arg-type]
                        fill=color.css_hex,
                        clip_path=f'url(#{id_})',
                    ),
                )

        if self.interval_vertical_parts_colors is not None:
            for part, color in self.interval_vertical_parts_colors.get(interval, self.interval_vertical_parts_colors.get(AbstractInterval(interval), {})).items():
                if part >= self.n_parts:
                    raise ValueError(f'part={part} must be less than n_parts={self.n_parts}')
                self.elements.append(
                    svg.Rect(
                        **self.ax_split_part_rect_coordinates(x, y, part, 'vertical'),  # type: ignore[arg-type]
                        fill=color.css_hex,
                        clip_path=f'url(#{id_})',
                    ),
                )

    @abc.abstractmethod
    def ax_split_part_rect_coordinates(self, x: float, y: float, part: int, ax: Literal['horizontal', 'vertical']) -> dict[str, float]:
        ...

    def add_key(self, row: float, col: float) -> None:
        interval = self.row_col_to_interval(row, col)
        abstract_interval = AbstractInterval(interval)
        x = self.col_to_x(col)
        y = self.row_to_y(row)
        color = self.interval_colors.get(interval, self.interval_colors.get(abstract_interval, self.default_key_color))
        points = self.key_points(x, y)
        if self.round_points:
            points = [round(p, 1) for p in points]

        polygon_kw = {
            'class_': ['polygon-colored'],
            'fill': color.css_hex,
            'points': points,
            # clip_path='url(#key-clip)',
        }
        id_ = f'row-{row}-col-{col}-{self.id_suffix}'
        self.defs.elements.append(svg.ClipPath(id=id_, elements=[svg.Polygon(**polygon_kw)]))  # type: ignore[union-attr]
        stroke = self.interval_strokes.get(interval, self.interval_strokes.get(abstract_interval, None))
        if stroke is not None:
            polygon_kw['stroke'] = stroke['stroke'].css_hex
            polygon_kw['stroke_width'] = stroke.get('stroke_width', 1) * 2
            polygon_kw['clip_path'] = f'url(#{id_})'
        polygon = svg.Polygon(**polygon_kw)
        polygon.interval = interval  # type: ignore[attr-defined]
        polygon.abstract_interval = abstract_interval.interval  # type: ignore[attr-defined]
        polygon.abstract_interval_base12 = abstract_interval  # type: ignore[attr-defined]
        self.elements.append(polygon)

        if self.n_parts is not None:
            self.add_parts(interval, x, y, id_)

        for text_callable in (
            self.interval_text,
            self.interval_subtext,
            *self.interval_extra_texts,
        ):
            if text_callable is None:
                continue
            value = text_callable(interval, self.radius, x, y)
            if value is None:
                continue
            self.elements.append(svg.Text(**value))

        # transparent polygon on top for mouse events and recoloring
        polygon = svg.Polygon(
            class_=['polygon-transparent'],
            points=points,  # type: ignore[arg-type]
            fill=Color.from_rgba_int((0, 0, 0, 0)).css_rgba,
        )
        polygon.interval = interval  # type: ignore[attr-defined]
        polygon.abstract_interval = abstract_interval.interval  # type: ignore[attr-defined]
        polygon.abstract_interval_base12 = abstract_interval  # type: ignore[attr-defined]
        self.elements.append(polygon)

    @abc.abstractmethod
    def key_points(self, x: float, y: float) -> list[float]:
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
