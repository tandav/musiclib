import cmath
import math
from musiclib.svg.isomorphic.base import IsomorphicKeyboard


class Squared(IsomorphicKeyboard):
    def add_keys(self) -> None:
        if self.rotated:
            for row in range(0, self.n_rows):
                for col in range(0, self.n_cols):
                    self.add_key(row, col)
            return
        for row in range(-1, self.n_rows + 1):
            for col in range(-2, self.n_cols + 1, 2):
                self.add_key(row, col + row % 2)
        
    @staticmethod
    def rotate_coordinates_45_degrees(x: int, y: int) -> tuple[int, int]:
        return (x - y) // 2, (x + y) // 2

    def row_col_to_interval(self, row: float, col: float) -> int:
        if self.rotated:
            return (self.n_rows - round(row) - 1) * self.ax1_step + round(col) * self.ax0_step
        r_col, r_row = self.rotate_coordinates_45_degrees(round(col), round(row))
        return r_col * self.ax0_step + r_row * self.ax1_step

    def col_to_x(self, col: float) -> float:
        if self.rotated:
            return self.h * (2 * col + 1)
        return self.radius * (col + 1)

    def row_to_y(self, row: float, invert_axis: bool = True) -> float:
        if invert_axis:
            if self.rotated:
                return self.height - self.row_to_y(row, invert_axis=False)
            return self.height - self.row_to_y(row, invert_axis=False)
        if self.rotated:
            return self.h * (2 * row + 1)
        return self.radius * (row + 1)
        
    @property
    def width(self) -> int:
        if self.rotated:
            return int(self.col_to_x(self.n_cols - 1 + 0.5))
        return int(self.col_to_x(self.n_cols))

    @property
    def height(self) -> int:
        if self.rotated:
            return int(self.row_to_y(self.n_rows - 1 + 0.5, invert_axis=False))
        return int(self.row_to_y(self.n_rows, invert_axis=False))
    
    @property
    def h(self):
        return 2 ** 0.5 / 2 * self.radius

    @staticmethod
    def vertex(x: float, y: float, radius: float, i: int, phase: float = 0) -> tuple[float, float]:
        theta = phase + 2 * math.pi * i / 4
        p = complex(y, x) + radius * cmath.exp(1j * theta)
        return p.imag, p.real

    def key_points(self, x: float, y: float, radius: float) -> list[float]:
        phase = math.pi / 4 if self.rotated else 0
        points = []
        for i in range(4):
            points += self.vertex(x, y, radius, i, phase)
        return points
    
    def key_part_points(self, x: float, y: float, part: int) -> list[float]:
        i = part // 2
        return [
            x, 
            y, 
            *self.vertex(x, y, self.h, i, phase=2 * math.pi / 8), # todo: support 12 parts
            *self.vertex(x, y, self.radius, i + part % 2),
        ]

