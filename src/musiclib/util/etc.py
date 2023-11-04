import cmath

from musiclib.interval import AbstractInterval



def are_all_none(*args) -> bool:
    return all(arg is None for arg in args)


def any_not_none(*args) -> bool:
    return any(arg is not None for arg in args)


def are_mutually_exclusive(*args, exactly_one: bool = False) -> bool:
    n_not_none = sum(1 for arg in args if arg is not None)
    if exactly_one:
        return n_not_none == 1
    return n_not_none <= 1


def increment_duplicates(a: list[int]) -> list[int]:
    if not a:
        return []
    res = [a[0]]
    for num in a[1:]:
        if num <= res[-1]:
            res.append(res[-1] + 1)
        else:
            res.append(num)
    return res


def intervals_rotations(intervals: frozenset[int]) -> tuple[frozenset[int], ...]:
    out = [sorted(intervals)]
    for _ in range(len(intervals) - 1):
        x = out[-1]
        out.append([x[i] - x[1] for i in range(1, len(intervals))] + [x[0] + 12 - x[1]])
    return tuple(map(frozenset, out))


def named_intervals_rotations(
    intervals: frozenset[int | AbstractInterval] | set[int | AbstractInterval],
    name_prefix: str,
) -> dict[str, frozenset[int]]:
    return {f'{name_prefix}_{i}': fs for i, fs in enumerate(intervals_rotations(intervals))}


def vertex(
    x: float,
    y: float,
    radius: float,
    n: int,
    i: int,
    phase: float = 0,
) -> tuple[float, float]:
    theta = phase + 2 * cmath.pi * i / n
    p = complex(y, x) + radius * cmath.exp(1j * theta)
    return p.imag, p.real


def line_intersection(
    x00: float,
    y00: float,
    x01: float,
    y01: float,
    x10: float,
    y10: float,
    x11: float,
    y11: float,
) -> tuple[float, float]:
    """
    computes coordinates of intersection of 2 lines.
    Each line is defined by 2 points:
    input arguments:
    x00 - x coordinate of 1st point of 1st line
    y00 - y coordinate of 1st point of 1st line
    x01 - x coordinate of 2nd point of 1st line
    y01 - y coordinate of 2nd point of 1st line
    x10 - x coordinate of 1st point of 2nd line
    y10 - y coordinate of 1st point of 2nd line
    x11 - x coordinate of 2nd point of 2nd line
    y11 - y coordinate of 2nd point of 2nd line

    output: x, y - coordinates of intersection of 2 lines
    """
    # Calculate the slope and y-intercept of the first line
    if x01 - x00 != 0:
        m1 = (y01 - y00) / (x01 - x00)
        b1 = y00 - m1 * x00
    else:
        m1 = None
        b1 = x00

    # Calculate the slope and y-intercept of the second line
    if x11 - x10 != 0:
        m2 = (y11 - y10) / (x11 - x10)
        b2 = y10 - m2 * x10
    else:
        m2 = None
        b2 = x10

    # Check if the lines are parallel
    if m1 == m2:
        return None, None  # The lines are parallel, so no intersection

    # If the first line is vertical
    if m1 is None:
        x = b1
        y = m2 * x + b2
        return x, y

    # If the second line is vertical
    if m2 is None:
        x = b2
        y = m1 * x + b1
        return x, y

    # Calculate the intersection point
    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1

    return x, y
