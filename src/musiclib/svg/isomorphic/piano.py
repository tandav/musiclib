from typing import Any
from typing import Literal

from musiclib.svg.isomorphic.base import IsomorphicKeyboard


class IsoPiano(IsomorphicKeyboard):
    def __init__(
        self,
        radius1: int = 36,
        **kw: Any,
    ) -> None:
        self.radius1 = radius1
        if kw.get('rotated', False):
            kw.setdefault('n_cols', 1)
            kw.setdefault('n_rows', 12)
        else:
            kw.setdefault('n_rows', 1)
            kw.setdefault('n_cols', 12)
        super().__init__(**kw)

    def validate_dimensions(
        self,
        n_rows: int | None,
        n_cols: int | None,
        row_range: range | None,
        col_range: range | None,
    ) -> None:
        if self.rotated and n_cols != 1:
            raise ValueError('n_cols must be 1 for rotated IsoPiano')
        if not self.rotated and n_rows != 1:
            raise ValueError('n_rows must be 1 for IsoPiano')
        super().validate_dimensions(n_rows, n_cols, row_range, col_range)

    def add_keys(self) -> None:
        for row in (self.row_range or range(self.n_rows)):
            for col in (self.col_range or range(self.n_cols)):
                self.add_key(row, col)

    def row_col_to_interval(self, row: float, col: float) -> int:
        if self.rotated:
            return round(row)
        return round(col)

    def col_to_x(self, col: float) -> float:
        if self.rotated:
            return self.radius1 * (col * 2 + 1) + self.offset_x
        return self.radius * (col * 2 + 1) + self.offset_x

    def row_to_y(self, row: float) -> float:
        if self.rotated:
            return self.radius * (row * 2 + 1) + self.offset_y
        return self.radius1 * (row * 2 + 1) + self.offset_y

    @property
    def width(self) -> int:
        return int(self.col_to_x(self.n_cols - 0.5))

    @property
    def height(self) -> int:
        return int(self.row_to_y(self.n_rows - 0.5))

    def key_part_points(self, x: float, y: float, part: int) -> list[float]:
        raise NotImplementedError('TODO: split vertically')

    @staticmethod
    def vertex(x: float, y: float, radius_w: float, i: int, radius_h: float) -> tuple[float, float]:
        return {
            0: (x - radius_w, y - radius_h),
            1: (x + radius_w, y - radius_h),
            2: (x + radius_w, y + radius_h),
            3: (x - radius_w, y + radius_h),
        }[i % 4]

    def key_points(self, x: float, y: float) -> list[float]:
        points: list[float] = []
        for i in range(5):
            if self.rotated:
                points += self.vertex(x, y, self.radius1, i, self.radius)
            else:
                points += self.vertex(x, y, self.radius, i, self.radius1)
        return points

    def ax_split_part_rect_coordinates(self, x: float, y: float, part: int, ax: Literal['horizontal', 'vertical']) -> dict[str, float]:
        ax_split_len = self.radius if self.rotated else self.radius1
        ax_other_len = self.radius1 if self.rotated else self.radius
        z = ax_split_len * 2 / self.n_parts  # type: ignore[operator]
        if ax == 'vertical':
            return {
                'x': x - ax_other_len,
                'y': y + ax_split_len - (part + 1) * z,
                'width': ax_other_len * 2,
                'height': z,
            }
        if ax == 'horizontal':
            ax_split_len, ax_other_len = ax_other_len, ax_split_len
            z = ax_split_len * 2 / self.n_parts  # type: ignore[operator]
            return {
                'x': x - ax_split_len + part * z,
                'y': y - ax_other_len,
                'width': z,
                'height': ax_other_len * 2,
            }
        raise ValueError(f'Unsupported ax: {ax}, must be horizontal or vertical')
