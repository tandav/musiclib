import typing as tp

import numpy as np

from musiclib.interval import AbstractInterval

SVG_TEXT_KW = dict[str, tp.Any]
TEXT_CALLABLE: tp.TypeAlias = tp.Callable[[int, int, float, float], SVG_TEXT_KW | None]
TEXT_DEFAULT_KW = {
    'font_family': 'monospace',
    'text_anchor': 'middle',
    'dominant_baseline': 'middle',
    'pointer_events': 'none',  # probably not needed when using event.preventDefault() on transparent polygon
}

IntervalDict: tp.TypeAlias = dict[AbstractInterval | int, str]


def middle_text_kw_abstract_interval(interval: int, radius: int, x: float, y: float) -> SVG_TEXT_KW:
    return {**TEXT_DEFAULT_KW, 'font_size': int(0.5 * radius), 'text': str(AbstractInterval(interval)), 'x': x, 'y': y}


def sub_text_kw_interval(interval: int, radius: int, x: float, y: float) -> SVG_TEXT_KW:
    return {**TEXT_DEFAULT_KW, 'font_size': int(0.3 * radius), 'text': np.base_repr(interval, base=12), 'x': x, 'y': y + int(0.4 * radius)}


class FromIntervalDict:
    def __init__(self, interval_dict: IntervalDict, *, abstract: bool = False) -> None:
        self.interval_dict = interval_dict
        self.abstract = abstract

    def __call__(self, interval: int, radius: int, x: float, y: float) -> SVG_TEXT_KW:
        return {
            **TEXT_DEFAULT_KW,
            'font_size': int(0.5 * radius),
            'text': self.interval_dict.get(AbstractInterval(interval) if self.abstract else interval),
            'x': x,
            'y': y,
        }
