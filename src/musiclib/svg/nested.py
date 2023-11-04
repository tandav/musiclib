import svg
from svg._types import Number


class NestedSVG:
    def __init__(
        self,
        svgs: list[svg.SVG],
        coordinates: list[tuple[Number, Number]],
        width: Number = 600,
        height: Number = 400,
        class_: list[str] | None = None,
        id: str | None = None,  # noqa: A002 pylint: disable=redefined-builtin
    ) -> None:
        self.svgs = svgs
        self.coordinates = coordinates
        self.width = width
        self.height = height
        self.class_ = class_
        self.id = id

    @property
    def svg(self) -> svg.SVG:
        return svg.SVG(
            width=self.width,
            height=self.height,
            elements=[
                svg.SVG(
                    x=x,
                    y=y,
                    width=_svg.width,
                    height=_svg.height,
                    viewBox=svg.ViewBoxSpec(0, 0, _svg.width, _svg.height),  # type: ignore[arg-type]
                    elements=_svg.elements if isinstance(_svg, svg.SVG) else [_svg],
                    class_=_svg.class_,
                    id=_svg.id,
                )
                for _svg, (x, y) in zip(self.svgs, self.coordinates, strict=True)
            ],
            class_=self.class_,
            id=self.id,
        )

    def _repr_svg_(self) -> str:
        return str(self.svg)
