import svg


class NestedSVG:
    def __init__(
        self,
        svgs: list[svg.SVG],
        coordinates: list[tuple[svg._types.Number, svg._types.Number]],
        width: svg._types.Number = 600,
        height: svg._types.Number = 400,
    ) -> None:
        self.svgs = svgs
        self.coordinates = coordinates
        self.width = width
        self.height = height

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
                    viewBox=svg.ViewBoxSpec(0, 0, _svg.width, _svg.height),
                    elements=_svg.elements,
                )
                for _svg, (x, y) in zip(self.svgs, self.coordinates, strict=True)
            ],
        )
    def _repr_svg_(self) -> str:
        return str(self.svg)
