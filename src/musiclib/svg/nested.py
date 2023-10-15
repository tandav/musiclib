import svg


class NestedSVG:
    def __init__(
        self,
        elements: list[svg.SVG | svg.Element],
        coordinates: list[tuple[svg._types.Number, svg._types.Number]],
        width: svg._types.Number = 600,
        height: svg._types.Number = 400,
        class_: list[str] | None = None,
        id: str | None = None,
    ) -> None:
        self.elements = elements
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
                    width=el.width,
                    height=el.height,
                    viewBox=svg.ViewBoxSpec(0, 0, el.width, el.height),
                    elements=el.elements if isinstance(el, svg.SVG) else [el],
                    class_=el.class_,
                    id=el.id,
                )
                for el, (x, y) in zip(self.elements, self.coordinates, strict=True)
            ],
            class_=self.class_,
            id=self.id,
        )

    def _repr_svg_(self) -> str:
        return str(self.svg)
