import cmath
import math
from musiclib.svg.isomorphic.base import IsomorphicKeyboard


class Hexagonal(IsomorphicKeyboard):
    def add_keys(self) -> None:
        if self.rotated:
            for col in range(-1, self.n_cols + 1):
                for row in range(-2, self.n_rows + 1, 2):
                    self.add_key(row + col % 2, col)
            return
        for row in range(-1, self.n_rows + 1):
            for col in range(-2, self.n_cols + 1, 2):
                self.add_key(row, col + row % 2)

    def col_to_x(self, col: float) -> float:
        if self.rotated:
            return self._opposite_vertices_axis_index_to_px(col)
        return self._opposite_midpoints_axis_index_to_px(col)

    def row_to_y(self, row: float) -> float:
        if self.rotated:
            return self._opposite_midpoints_axis_index_to_px(row)
        return self._opposite_vertices_axis_index_to_px(row)

    @property
    def width(self) -> int:
        if self.rotated:
            return int(self.col_to_x(self.n_cols) - 0.5 * self.radius)
        return int(self.col_to_x(self.n_cols))

    @property
    def height(self) -> int:
        if self.rotated:
            return int(self.row_to_y(self.n_rows))
        return int(self.row_to_y(self.n_rows) - 0.5 * self.radius)
    
    def _opposite_vertices_axis_index_to_px(self, i: int) -> float:
        return self.radius * (i * 1.5 + 1)

    def _opposite_midpoints_axis_index_to_px(self, i: int) -> float:
        return self.h * (i + 1)

    @property
    def h(self):
        return 3 ** 0.5 / 2 * self.radius

    @staticmethod
    def vertex(x: float, y: float, radius: float, i: int, phase: float = 0) -> tuple[float, float]:
        theta = phase + 2 * math.pi * i / 6
        p = complex(y, x) + radius * cmath.exp(1j * theta)
        return p.imag, p.real

    def key_points(self, x: float, y: float, radius: float) -> list[float]:
        points = []
        phase = math.pi / 6 if self.rotated else 0
        for i in range(7):
            points += self.vertex(x, y, radius, i, phase)
        return points
    
    def key_part_points(self, x: float, y: float, part: int) -> list[float]:
        i = part // 2
        return [
            x, 
            y, 
            *self.vertex(x, y, self.h, i, phase=2 * math.pi / 12),
            *self.vertex(x, y, self.radius, i + part % 2),
        ]
