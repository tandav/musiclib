from typing import Literal

import svg
from colortool import Color

from musiclib import config


class Header:
    def __init__(
        self,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        title_href: str | None = None,
        title_font_size: int = 15,
        subtitle_href: str | None = None,
        subtitle_font_size: int = 12,
        title_y: int = 4,
        subtitle_y: int = 20,
        background_color: Color = config.WHITE_BRIGHT,
        width: int = 300,
        height: int = 35,
        margin: tuple[int, int, int, int] = (3, 3, 3, 3),
        padding: tuple[int, int, int, int] = (30, 2, 2, 2),
        border_radius: int = 0,
        header_rect: bool = True,
    ) -> None:
        self.width = width
        self.height = height
        self.elements: list[svg.Element] = []
        if header_rect:
            self.elements.append(
                svg.Rect(
                    class_=['header_rect'],
                    x=0,
                    y=0,
                    width=width,
                    height=height,
                    fill=background_color.css_hex,
                    rx=border_radius,
                    ry=border_radius,
                    stroke_width=1,
                    stroke=config.BLACK_PALE.css_hex,
                ),
            )

        if title is not None:
            dominant_baseline: Literal['hanging', 'central']
            if subtitle is not None:
                y = margin[0] + title_y
                dominant_baseline = 'hanging'
            else:
                y = (margin[0] + padding[0]) // 2
                dominant_baseline = 'central'
            text_title = svg.Text(
                x=margin[3] + padding[3],
                y=y,
                text=title,
                font_size=title_font_size,
                font_weight='bold',
                dominant_baseline=dominant_baseline,
            )
            if title_href is not None:
                self.elements.append(svg.A(href=title_href, elements=[text_title]))
            else:
                self.elements.append(text_title)
        if subtitle is not None:
            text_subtitle = svg.Text(
                x=margin[3] + padding[3],
                y=margin[0] + subtitle_y,
                font_size=subtitle_font_size,
                fill=config.BLACK_BRIGHT.css_hex,
                text=subtitle,
                dominant_baseline='hanging',
            )
            if subtitle_href is not None:
                self.elements.append(svg.A(href=subtitle_href, elements=[text_subtitle]))
            else:
                self.elements.append(text_subtitle)

    @property
    def svg(self) -> svg.SVG:
        return svg.SVG(width=self.width, height=self.height, elements=self.elements)

    def _repr_svg_(self) -> str:
        return str(self.svg)
