import cmath
from typing import Literal

from musiclib.svg.isomorphic.base import IsomorphicKeyboard
from musiclib.util.etc import vertex


class Squared(IsomorphicKeyboard):
    def add_keys(self) -> None:
        if self.rotated:
            for row in (self.row_range or range(-1, self.n_rows + 1)):
                for col in (self.col_range or range(-2, self.n_cols + 1, 2)):
                    self.add_key(row, col + row % 2)
            return
        for row in (self.row_range or range(self.n_rows)):
            for col in (self.col_range or range(self.n_cols)):
                self.add_key(row, col)

    @staticmethod
    def transform_coordinates(x: int, y: int) -> tuple[int, int]:
        """rotate_coordinates_45_degrees"""
        return (x - y) // 2, (x + y) // 2

    def row_col_to_interval(self, row: float, col: float) -> int:
        if self.rotated:
            ax0, ax1 = self.transform_coordinates(round(col), round(row))
            return ax0 * self.ax0_step + ax1 * self.ax1_step
        return round(row) * self.ax1_step + round(col) * self.ax0_step

    def col_to_x(self, col: float) -> float:
        if self.rotated:
            return self.radius * (col + 1) + self.offset_x
        return self.h * (2 * col + 1) + self.offset_x

    def row_to_y(self, row: float, *, invert_axis: bool = True) -> float:
        if invert_axis:
            return self.height - (self.row_to_y(row, invert_axis=False) + self.offset_y)
        if self.rotated:
            return self.radius * (row + 1) + self.offset_y
        return self.h * (2 * row + 1) + self.offset_y

    @property
    def width(self) -> int:
        if self.rotated:
            return int(self.col_to_x(self.n_cols))
        return int(self.col_to_x(self.n_cols - 1 + 0.5))

    @property
    def height(self) -> int:
        if self.rotated:
            return int(self.row_to_y(self.n_rows, invert_axis=False))
        return int(self.row_to_y(self.n_rows - 1 + 0.5, invert_axis=False))

    @property
    def h(self) -> float:
        return 2 ** 0.5 / 2 * self.radius

    def key_points(self, x: float, y: float) -> list[float]:
        phase = 0 if self.rotated else cmath.pi / 4
        points: list[float] = []
        for i in range(4):
            points += vertex(x, y, self.radius, 4, i, phase)
        return points

    def ax_split_part_rect_coordinates(self, x: float, y: float, part: int, ax: Literal['horizontal', 'vertical']) -> dict[str, float]:
        ax_split_len = self.radius if self.rotated else self.h
        ax_other_len = self.radius if self.rotated else self.h
        z = ax_split_len * 2 / self.n_parts  # type: ignore[operator]
        if ax == 'vertical':
            return {
                'x': x - ax_other_len,
                'y': y + ax_split_len - (part + 1) * z,
                'width': ax_other_len * 2,
                'height': z,
            }
        if ax == 'horizontal':
            return {
                'x': x - ax_split_len + part * z,
                'y': y - ax_other_len,
                'width': z,
                'height': ax_other_len * 2,
            }
        raise ValueError(f'Unsupported ax: {ax}, must be horizontal or vertical')
