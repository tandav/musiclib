import abc
import uuid
import svg
from collections.abc import Iterable
from colortool import Color

from musiclib import config
from musiclib.interval import AbstractInterval
from musiclib.svg.isomorphic.text import TEXT_CALLABLE
from musiclib.svg.isomorphic.text import middle_text_kw_abstract_interval


class IsomorphicKeyboard(abc.ABC):
    """
    https://notes.tandav.me/notes/3548
    """
    def __init__(
        self,
        interval_colors: dict[AbstractInterval | int, Color] | None = None,
        interval_strokes: dict[AbstractInterval | int, Color] | None = None,
        interval_parts_colors: dict[int, dict[int, Color]] | None = None,
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
        self.interval_parts_colors = interval_parts_colors or {}
        self.interval_text = interval_text
        self.interval_subtext = interval_subtext
        self.interval_extra_texts = interval_extra_texts
        self.round_points = round_points
        self.interval_strokes = interval_strokes or {}
        self.defs = svg.Defs(elements=[])
        self.elements.append(self.defs)
        self.id_suffix = str(uuid.uuid4()).split('-')[0]
        self.ax0_step = ax0_step
        self.ax1_step = ax1_step
        self.default_key_color = default_key_color
        self.add_keys()


    def validate_dimensions(
        self,
        n_rows: int | None, 
        n_cols: int | None,
        row_range: range | None,
        col_range: range | None,
    ) -> None:
        if not ((n_rows is None) ^ (row_range is None)):
            raise ValueError('Exactly one of n_rows or row_range must be provided')
        if not ((n_cols is None) ^ (col_range is None)):
            raise ValueError('Exactly one of n_cols or col_range must be provided')
        
        self.row_range = row_range
        self.col_range = col_range

        if n_rows is None:
            self.n_rows = len(row_range)
        elif n_rows < 0:
            raise ValueError(f'n_rows={n_rows} must be positive')
        else:
            self.n_rows = n_rows

        if n_cols is None:
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
