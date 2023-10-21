from musiclib.svg.isomorphic.base import IsomorphicKeyboard


class IsoPiano(IsomorphicKeyboard):
    def __init__(
        self,
        n_rows: int | None = None,
        key_height: int = 100,
        offset_x: int = 0,
        extra_radius_width_on_right: bool = False,
        **kwargs,
    ) -> None:
        if n_rows is not None:
            raise NotImplementedError('n_rows is not supported for Piano')
        self.key_height = key_height
        self.offset_x = offset_x
        self.extra_radius_width_on_right = extra_radius_width_on_right
        super().__init__(
            n_rows=n_rows,
            **kwargs,
        )

    def col_to_x(self, col: float) -> float:
        return self.radius * (col * 2 + 1) + self.offset_x

    def row_to_y(self, row: float) -> float:
        return self.key_height // 2

    @property
    def width(self) -> int:
        if self.extra_radius_width_on_right:
            return int(self.col_to_x(self.n_cols))
        return int(self.col_to_x(self.n_cols - 0.5))

    @property
    def height(self) -> int:
        return self.key_height
    
    def key_part_points(self, x: float, y: float, part: int) -> list[float]:
        raise NotImplementedError('TODO: split vertically')

    @staticmethod
    def vertex(x: float, y: float, radius_w: float, i: int, radius_h: float) -> tuple[float, float]:
        if i % 4 == 0:
            return x - radius_w, y - radius_h
        if i == 1:
            return x + radius_w, y - radius_h
        if i == 2:
            return x + radius_w, y + radius_h
        if i == 3:
            return x - radius_w, y + radius_h
        raise ValueError(f'invalid i={i}')

    def key_points(self, x: float, y: float, radius: float) -> list[float]:
        points = []
        for i in range(5):
            points += self.vertex(x, y, radius, i, self.key_height / 2)
        return points
