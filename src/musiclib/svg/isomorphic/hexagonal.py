import cmath
import math
from musiclib.svg.isomorphic.base import IsomorphicKeyboard


class Hexagonal(IsomorphicKeyboard):
    def col_to_x(self, col: float) -> float:
        return self.h * (col + 1)

    def row_to_y(self, row: float) -> float:
        return self.radius * (row * 1.5 + 1)

    @property
    def width(self) -> int:
        return int(self.col_to_x(self.n_cols))

    @property
    def height(self) -> int:
        return int(self.row_to_y(self.n_rows) - 0.5 * self.radius)
    
    @property
    def h(self):
        return 3 ** 0.5 / 2 * self.radius

    @staticmethod
    def vertex(x: float, y: float, radius: float, i: int, phase: float = 0) -> tuple[float, float]:
        phase_start = 2 * math.pi / 2
        theta = phase_start + phase + 2 * math.pi * i / 6
        p = complex(y, x) + radius * cmath.exp(1j * theta)
        return p.imag, p.real

    def key_points(self, x: float, y: float, radius: float) -> list[float]:
        points = []
        for i in range(7):
            points += self.vertex(x, y, radius, i)
        return points
    
    def key_part_points(self, x: float, y: float, part: int) -> list[float]:
        i = part // 2
        return [
            x, 
            y, 
            *self.vertex(x, y, self.h, i, phase=2 * math.pi / 12),
            *self.vertex(x, y, self.radius, i + part % 2),
        ]
