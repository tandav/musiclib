import svg
from typing import Any
from musiclib.svg.nested import NestedSVG
from musiclib.svg.header import Header
from musiclib.svg.isomorphic import Hex
from musiclib.svg.isomorphic import IsoPiano
from musiclib.svg.piano import RegularPiano
from musiclib.interval import AbstractInterval
from musiclib import config
from colortool import Color


class HexPiano:
    def __init__(
        self,
        interval_colors: dict[AbstractInterval | int, Color] | None = None,
        interval_parts_colors: dict[int, dict[int, Color]] | None = None,
        interval_text: dict[AbstractInterval | int, str] | str | None = 'interval',
        interval_strokes: dict[AbstractInterval | int, Color] | None = None,
        n_rows: int | None = 3,
        n_cols: int = 24,
        radius: int = 18,
        font_size_radius_ratio: float = 0.5,
        round_points: bool = True,
        key_height: int | None = None,
        width: int | None = None,
        height: int | None = None,
        class_: list[str] | None = None,
        id: str | None = None,
        header_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self.hex = Hex(
            interval_colors=interval_colors,
            interval_parts_colors=interval_parts_colors,
            interval_text=interval_text,
            interval_strokes=interval_strokes,
            n_rows=n_rows,
            n_cols=n_cols,
            radius=radius,
            font_size_radius_ratio=font_size_radius_ratio,
            round_points=round_points,
        )
        self.piano = IsoPiano(
            interval_colors=interval_colors,
            interval_parts_colors=interval_parts_colors,
            interval_text=interval_text,
            interval_strokes=interval_strokes,
            n_cols=n_cols,
            radius=self.hex.h/2,
            offset_x=self.hex.h/2,
            font_size_radius_ratio=font_size_radius_ratio,
            round_points=round_points,
            key_height = key_height or radius * 2,
            extra_radius_width_on_right=True,
        )
        if header_kwargs is None:
            self.nested_svg = NestedSVG(
                elements=[self.hex.svg, self.piano.svg],
                coordinates=[(0, 0), (0, self.hex.svg.height)],
                width=self.hex.svg.width,
                height=self.hex.svg.height + self.piano.svg.height,
            )
        else:
            header_kwargs.setdefault('width', self.hex.svg.width)
            self.header = Header(**header_kwargs)
            self.nested_svg = NestedSVG(
                elements=[self.header.svg, self.hex.svg, self.piano.svg],
                coordinates=[(0, 0), (0, self.header.svg.height), (0, self.header.svg.height + self.hex.svg.height)],
                width=width or self.hex.svg.width,
                height=height or self.header.height + self.hex.height + self.piano.svg.height,
                class_=class_,
                id=id,
            )

    @property
    def svg(self) -> svg.SVG:
        return self.nested_svg.svg

    def __str__(self) -> str:
        return str(self.svg)

    def _repr_svg_(self) -> str:
        return str(self)


class Piano:
    def __init__(
        self,
        *,
        margin: tuple[int, int, int, int] = (3, 3, 3, 3),
        padding: tuple[int, int, int, int] = (2, 2, 2, 2),
        shadow_offset: int = 2,
        border_radius: int = 3,
        background_color: Color = config.WHITE_BRIGHT,
        header_kwargs: dict[str, Any] | None = None,
        regular_piano_kwargs: dict[str, Any] | None = None,
        class_: tuple[str, ...] = (),
        id: str | None = None,  # noqa: A002 # pylint: disable=redefined-builtin
    ):
        header_kwargs.setdefault('header_rect', False)
        header_kwargs.setdefault('margin', (0, 0, 0, 0))
        header_kwargs.setdefault('height', 30)
        self.header = Header(**(header_kwargs or {}))
        self.piano = RegularPiano(**(regular_piano_kwargs or {}))
        card_width = self.piano.width + padding[1] + padding[3]
        card_height = self.header.svg.height + self.piano.height + padding[0] + padding[2]
        width = margin[3] + card_width + shadow_offset + margin[1]
        height = margin[0] + card_height + shadow_offset + margin[2]
        self.shadow_rect = svg.SVG(elements=[
            svg.Rect(
                class_=['shadow_rect'],
                x=margin[3] + shadow_offset,
                y=margin[0] + shadow_offset,
                width=card_width,
                height=card_height,
                fill=config.BLACK_BRIGHT.css_hex,
                rx=border_radius,
                ry=border_radius,
            )],
            class_=['shadow_rect_svg'],
            width=width,
            height=height,
        )
        self.card_rect = svg.SVG(elements=[
            svg.Rect(
                x=margin[3],
                y=margin[0],
                class_=['card_rect'],
                width=card_width,
                height=card_height,
                fill=background_color.css_hex,
                rx=border_radius,
                ry=border_radius,
                stroke_width=1,
                stroke=config.BLACK_PALE.css_hex,
            )],
            class_=['card_rect_svg'],
            width=width,
            height=height,
        )
        self.nested_svg = NestedSVG(
            elements=[
                self.shadow_rect,
                self.card_rect,
                self.header.svg,
                self.piano.svg,
            ],
            coordinates=[
                (0, 0),
                (0, 0),
                (margin[3] + padding[3], margin[0]),
                (margin[3] + padding[3], margin[0] + padding[0] + self.header.svg.height),
            ],
            width=width,
            height=height,
            class_=class_,
            id=id,
        )

    @property
    def svg(self) -> svg.SVG:
        return self.nested_svg.svg
    
    def __str__(self) -> str:
        return str(self.svg)

    def _repr_svg_(self) -> str:
        return str(self)
