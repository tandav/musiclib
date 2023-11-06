from collections.abc import Iterable
from typing import Any

import svg
from colortool import Color

from musiclib import config
from musiclib.interval import AbstractInterval
from musiclib.svg.header import Header
from musiclib.svg.isomorphic.base import TEXT_CALLABLE
from musiclib.svg.isomorphic.base import middle_text_kw_abstract_interval
from musiclib.svg.isomorphic.hexagonal import Hexagonal
from musiclib.svg.isomorphic.piano import IsoPiano
from musiclib.svg.isomorphic.squared import Squared
from musiclib.svg.nested import NestedSVG
from musiclib.svg.piano import RegularPiano


class PlanePiano:
    def __init__(  # noqa: PLR0915
        self,
        *,
        interval_colors: dict[AbstractInterval | int, Color] | None = None,
        interval_strokes: dict[AbstractInterval | int, Color] | None = None,
        interval_radial_parts_colors: dict[int, dict[int, Color]] | None = None,
        interval_horizontal_parts_colors: dict[int, dict[int, Color]] | None = None,
        interval_vertical_parts_colors: dict[int, dict[int, Color]] | None = None,
        n_parts: int | None = None,
        interval_text: TEXT_CALLABLE | None = middle_text_kw_abstract_interval,
        interval_subtext: TEXT_CALLABLE | None = None,
        interval_extra_texts: Iterable[TEXT_CALLABLE] = (),
        n_rows: int = 4,
        n_cols: int = 24,
        radius: int = 18,
        width: int | None = None,
        height: int | None = None,
        class_: list[str] | None = None,
        id: str | None = None,  # noqa: A002 pylint: disable=redefined-builtin
        header_kwargs: dict[str, Any] | None = None,
        plane_kwargs: dict[str, Any] | None = None,
        plane_cls: type[Hexagonal] | type[Squared] = Hexagonal,
        piano_kwargs: dict[str, Any] | None = None,
    ) -> None:

        nested_svg_kw = {
            'svgs': [],
            'coordinates': [],
            'height': 0,
            'class_': class_,
            'id': id,
        }

        plane_kwargs = plane_kwargs.copy() if plane_kwargs is not None else {}
        plane_kwargs.setdefault('interval_colors', interval_colors)
        plane_kwargs.setdefault('interval_strokes', interval_strokes)
        plane_kwargs.setdefault('interval_radial_parts_colors', interval_radial_parts_colors)
        plane_kwargs.setdefault('interval_horizontal_parts_colors', interval_horizontal_parts_colors)
        plane_kwargs.setdefault('interval_vertical_parts_colors', interval_vertical_parts_colors)
        plane_kwargs.setdefault('n_parts', n_parts)
        plane_kwargs.setdefault('interval_text', interval_text)
        plane_kwargs.setdefault('interval_subtext', interval_subtext)
        plane_kwargs.setdefault('interval_extra_texts', interval_extra_texts)
        plane_kwargs.setdefault('radius', radius)
        plane_kwargs.setdefault('ax0_step', 2)
        plane_kwargs.setdefault('ax1_step', 1)
        plane_kwargs.setdefault('n_rows', n_rows)
        plane_kwargs.setdefault('n_cols', n_cols)
        self.plane = plane_cls(**plane_kwargs)

        if header_kwargs is not None:
            header_kwargs = header_kwargs.copy()
            header_kwargs.setdefault('width', self.plane.svg.width)
            self.header = Header(**header_kwargs)
            nested_svg_kw['svgs'].append(self.header.svg)  # type: ignore[attr-defined]
            nested_svg_kw['coordinates'].append((0, nested_svg_kw['height']))  # type: ignore[attr-defined]
            nested_svg_kw['height'] += self.header.svg.height  # type: ignore[operator]

        nested_svg_kw['svgs'].append(self.plane.svg)  # type: ignore[attr-defined]
        nested_svg_kw['coordinates'].append((0, nested_svg_kw['height']))  # type: ignore[attr-defined]
        nested_svg_kw['height'] += self.plane.svg.height  # type: ignore[operator]

        if piano_kwargs is not None:
            piano_kwargs = piano_kwargs.copy()
            piano_kwargs.setdefault('interval_colors', interval_colors)
            piano_kwargs.setdefault('interval_strokes', interval_strokes)
            # piano_kwargs.setdefault('interval_radial_parts_colors', interval_radial_parts_colors)
            # piano_kwargs.setdefault('interval_horizontal_parts_colors', interval_horizontal_parts_colors)
            # piano_kwargs.setdefault('interval_vertical_parts_colors', interval_vertical_parts_colors)
            # piano_kwargs.setdefault('n_parts', n_parts)
            piano_kwargs.setdefault('interval_text', interval_text)
            piano_kwargs.setdefault('interval_subtext', interval_subtext)
            piano_kwargs.setdefault('interval_extra_texts', interval_extra_texts)
            piano_kwargs.setdefault('col_range', range(-1, n_cols + 1))
            piano_kwargs.setdefault('ax0_step', 1)
            piano_kwargs.setdefault('ax1_step', 0)
            piano_kwargs.setdefault('n_rows', 1)
            piano_kwargs.setdefault('n_cols', None)

            if isinstance(self.plane, Hexagonal):
                if self.plane.rotated:
                    piano_kwargs.setdefault('radius', self.plane.radius * 3 / 4)
                    piano_kwargs.setdefault('radius1', self.plane.radius * 3 / 4)
                    piano_kwargs.setdefault('offset_x', self.plane.radius / 4)
                else:
                    piano_kwargs.setdefault('radius', self.plane.h / 2)
                    piano_kwargs.setdefault('radius1', self.plane.h / 2)
                    piano_kwargs.setdefault('offset_x', self.plane.h / 2)
            elif isinstance(self.plane, Squared):
                if self.plane.rotated:
                    piano_kwargs.setdefault('radius', self.plane.radius / 2)
                    piano_kwargs.setdefault('radius1', self.plane.radius / 2)
                    piano_kwargs.setdefault('offset_x', self.plane.radius / 2)
                else:
                    piano_kwargs.setdefault('radius', self.plane.h)
                    piano_kwargs.setdefault('radius1', self.plane.h)
                    piano_kwargs.setdefault('col_range', range(n_cols))
            else:
                raise ValueError(f'Unsupported plane_cls: {plane_cls}, must be Hexagonal or Squared')

            self.piano = IsoPiano(**piano_kwargs)
            nested_svg_kw['svgs'].append(self.piano.svg)  # type: ignore[attr-defined]
            nested_svg_kw['coordinates'].append((0, nested_svg_kw['height']))  # type: ignore[attr-defined]
            nested_svg_kw['height'] += self.piano.svg.height  # type: ignore[operator]

        if height is not None:
            nested_svg_kw['height'] = height
        nested_svg_kw['width'] = width or self.plane.svg.width
        self.nested_svg = NestedSVG(**nested_svg_kw)  # type: ignore[arg-type]

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
        class_: list[str] | None = None,
        id: str | None = None,  # noqa: A002 # pylint: disable=redefined-builtin
    ) -> None:
        header_kwargs = header_kwargs.copy() if header_kwargs is not None else {}
        header_kwargs.setdefault('header_rect', False)
        header_kwargs.setdefault('margin', (0, 0, 0, 0))
        header_kwargs.setdefault('height', 30)
        self.header = Header(**header_kwargs)
        self.piano = RegularPiano(**(regular_piano_kwargs or {}))
        card_width = self.piano.width + padding[1] + padding[3]
        card_height = self.header.svg.height + self.piano.height + padding[0] + padding[2]  # type: ignore[operator]
        width = margin[3] + card_width + shadow_offset + margin[1]
        height = margin[0] + card_height + shadow_offset + margin[2]
        self.shadow_rect = svg.SVG(
            elements=[
                svg.Rect(
                    class_=['shadow_rect'],
                    x=margin[3] + shadow_offset,
                    y=margin[0] + shadow_offset,
                    width=card_width,
                    height=card_height,
                    fill=config.BLACK_BRIGHT.css_hex,
                    rx=border_radius,
                    ry=border_radius,
                ),
            ],
            class_=['shadow_rect_svg'],
            width=width,
            height=height,
        )
        self.card_rect = svg.SVG(
            elements=[
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
                ),
            ],
            class_=['card_rect_svg'],
            width=width,
            height=height,
        )
        self.nested_svg = NestedSVG(
            svgs=[
                self.shadow_rect,
                self.card_rect,
                self.header.svg,
                self.piano.svg,
            ],
            coordinates=[
                (0, 0),
                (0, 0),
                (margin[3] + padding[3], margin[0]),
                (margin[3] + padding[3], margin[0] + padding[0] + self.header.svg.height),  # type: ignore[operator]
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
