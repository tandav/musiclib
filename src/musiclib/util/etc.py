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
    intervals: frozenset[int],
    name_prefix: str,
) -> dict[str, frozenset[int]]:
    return {f'{name_prefix}_{i}': fs for i, fs in enumerate(intervals_rotations(intervals))}
