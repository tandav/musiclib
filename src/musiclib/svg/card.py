import svg
from typing import Any
from musiclib.svg.nested import NestedSVG
from musiclib.svg.header import Header
from musiclib.svg.isomorphic import Hex
from musiclib.svg.isomorphic import IsoPiano
from musiclib.interval import AbstractInterval
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
        )
        if header_kwargs is None:
            self.nested_svg = NestedSVG(
                svgs=[self.hex.svg, self.piano.svg],
                coordinates=[(0, 0), (0, self.hex.svg.height)],
                width=self.hex.svg.width,
                height=self.hex.svg.height + self.piano.svg.height,
            )
        else:
            header_kwargs.setdefault('width', self.hex.svg.width)
            self.header = Header(**header_kwargs)
            self.nested_svg = NestedSVG(
                svgs=[self.header.svg, self.hex.svg, self.piano.svg],
                coordinates=[(0, 0), (0, self.header.svg.height), (0, self.header.svg.height + self.hex.svg.height)],
                width=width or self.hex.svg.width,
                height=height or self.header.svg.height + self.hex.svg.height + self.piano.svg.height,
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
