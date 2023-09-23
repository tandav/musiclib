from typing import no_type_check
import pipe21 as P  # noqa: N812


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


@no_type_check
def bits_to_intervals(bits: str) -> frozenset[int]:
    return (
        bits
        | P.Map(int)
        | P.Pipe(enumerate)
        | P.FilterValues()
        | P.Keys()
        | P.Pipe(frozenset)
    )

def intervals_to_bits(intervals: frozenset[int]) -> str:
    bits = ['0'] * 12
    for i in intervals:
        bits[i] = '1'
    return ''.join(bits)


def intervals_rotations(intervals: frozenset[int]) -> frozenset[frozenset[int]]:
    """TODO: refactor and add tests"""
    out = set()
    for j in range(12):
        fs = frozenset((i + j) % 12 for i in intervals)
        if 0 in fs:
            out.add(fs)
    return frozenset(out)
