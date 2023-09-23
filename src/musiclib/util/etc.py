from typing import no_type_check


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


def bits_to_intervals(bits: str) -> frozenset[int]:
    return frozenset(k for k, v in enumerate(map(int, bits)) if v)


def intervals_to_bits(intervals: frozenset[int]) -> str:
    bits = ['0'] * 12
    for i in intervals:
        bits[i] = '1'
    return ''.join(bits)


def intervals_rotations(intervals: frozenset[int]) -> tuple[frozenset[int]]:
    l = len(intervals)
    out = [sorted(intervals)]
    for _ in range(len(intervals) - 1):
        x = out[-1]
        y = []
        for i in range(1, l):
            y.append(x[i] - x[1])
        y.append(x[0] + 12 - x[1])
        out.append(y)
    return tuple(map(frozenset, out))
