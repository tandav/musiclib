import svg
from musiclib.svg.nested import NestedSVG
from musiclib.svg.isomorphic import Hex
from musiclib.svg.isomorphic import Piano
from musiclib.interval import AbstractInterval
from colortool import Color


class HexPiano:
    def __init__(
        self,
        interval_colors: dict[AbstractInterval | int, Color] | None = None,
        interval_parts_colors: dict[int, dict[int, Color]] | None = None,
        interval_text: dict[AbstractInterval | int, str] | str | None = 'interval',
        n_rows: int | None = 7,
        n_cols: int = 13,
        radius: int = 30,
        font_size_radius_ratio: float = 0.5,
        round_points: bool = True,
        key_height: int | None = None,
    ) -> None:
        self.hex = Hex(
            interval_colors=interval_colors,
            interval_parts_colors=interval_parts_colors,
            interval_text=interval_text,
            n_rows=n_rows,
            n_cols=n_cols,
            radius=radius,
            font_size_radius_ratio=font_size_radius_ratio,
            round_points=round_points,
        )
        self.piano = Piano(
            interval_colors=interval_colors,
            interval_parts_colors=interval_parts_colors,
            interval_text=interval_text,
            n_cols=n_cols,
            radius=self.hex.h/2,
            offset_x=self.hex.h/2,
            font_size_radius_ratio=font_size_radius_ratio,
            round_points=round_points,
            key_height = key_height or radius * 2,
        )
        self.nested_svg = NestedSVG(
            svgs=[self.hex.svg, self.piano.svg],
            coordinates=[(0, 0), (0, self.hex.svg.height)],
            width=self.hex.svg.width,
            height=self.hex.svg.height + self.piano.svg.height,
        )


    @property
    def svg(self) -> svg.SVG:
        return self.nested_svg.svg

    def _repr_svg_(self) -> str:
        return str(self.svg)
