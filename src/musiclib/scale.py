from __future__ import annotations

import functools
import pickle
from typing import TYPE_CHECKING
from typing import Any
from typing import Self

if TYPE_CHECKING:
    from collections.abc import Iterator

    import svg

from musiclib import config
from musiclib.intervalset import IntervalSet
from musiclib.note import Note
from musiclib.noteset import NoteSet
from musiclib.svg.card import PlanePiano
from musiclib.svg.reprsvg import ReprSVGMixin
from musiclib.util.cache import Cached
from musiclib.util.etc import setdefault_path


class Scale(Cached, ReprSVGMixin):
    def __init__(self, root: Note, intervalset: IntervalSet) -> None:
        if not isinstance(root, Note):
            raise TypeError(f'expected Note, got {type(root)}')
        if not isinstance(intervalset, IntervalSet):
            raise TypeError(f'expected IntervalSet, got {type(intervalset)}')
        self.root = root
        self.intervalset = intervalset
        self.notes = frozenset({root + interval for interval in intervalset})
        self.noteset = NoteSet(self.notes)
        _notes_octave_fit = sorted(self.notes)
        _root_i = _notes_octave_fit.index(root)
        self.notes_ascending = _notes_octave_fit[_root_i:] + _notes_octave_fit[:_root_i]
        self.note_to_interval = dict(zip(self.notes_ascending, intervalset.intervals_ascending, strict=False))
        self.bits_chromatic_notes = tuple(int(Note(note) in self.notes) for note in config.chromatic_notes)
        self.note_i = {note: i for i, note in enumerate(self.notes_ascending)}
        self._key = self.root, self.intervalset

    @classmethod
    def from_name(cls: type[Self], root: str | Note, name: str) -> Self:
        if isinstance(root, str):
            root = Note(root)
        elif not isinstance(root, Note):
            raise TypeError(f'expected str | Note, got {type(root)}')
        return cls(root, IntervalSet(config.name_to_intervals[name]))

    @classmethod
    def from_notes(cls: type[Self], root: Note, notes: frozenset[Note]) -> Self:
        if not isinstance(root, Note):
            raise TypeError(f'expected Note, got {type(root)}')
        if root not in notes:
            raise ValueError('scale root must be in scale notes')
        return cls(root, IntervalSet(frozenset(note - root for note in notes)))

    @classmethod
    def from_str(cls: type[Self], string: str) -> Self:
        if string == '':
            raise ValueError('scale string must not be empty')
        if string[-2] != '/':
            raise ValueError('scale string must ends with scale root, example "CDEFGAB/C"')
        root = Note(string[-1])
        notes = frozenset(Note(note) for note in string[:-2])
        return cls.from_notes(root, notes)

    @functools.cached_property
    def note_scales(self) -> dict[str, dict[Note, str]]:
        _note_scales: dict[str, dict[Note, str]] = {}
        for name, kind in self.intervalset.name_kinds.items():
            scales = config.scale_order[kind]
            _scale_i = scales.index(name)
            scales = scales[_scale_i:] + scales[:_scale_i]
            _note_scales[kind] = {}
            for note, scale in zip(self.notes_ascending, scales, strict=True):
                _note_scales[kind][note] = scale
        return _note_scales

    def nths(self, ns: frozenset[int]) -> tuple[Scale, ...]:
        return tuple(
            Scale.from_notes(self.notes_ascending[i], frozenset(self.notes_ascending[(i + n) % len(self)] for n in ns))
            for i in range(len(self))
        )

    def transpose_to_note(self, note: Note) -> Scale:
        return Scale(note, self.intervalset)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Scale):
            raise TypeError
        return self._key == other._key

    def __hash__(self) -> int:
        return hash(self._key)

    def __len__(self) -> int:
        return len(self.notes)

    def __getitem__(self, item: int) -> Note:
        return self.notes_ascending[item]

    def __iter__(self) -> Iterator[Note]:
        return iter(self.notes_ascending)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, Note):
            raise TypeError
        return item in self.notes

    @property
    def str_names(self) -> str:
        return f"{self.root} {' '.join(sorted(self.intervalset.names))}"

    def __str__(self) -> str:
        return f"{''.join(note.name for note in self.notes_ascending)}/{self.root}"

    def __repr__(self) -> str:
        return f'Scale({self.root!r}, {self.intervalset!r})'

    def __getnewargs__(self) -> tuple[Note, IntervalSet]:
        return (self.root, self.intervalset)

    def svg_piano(self, **kwargs: Any) -> svg.SVG:
        from musiclib.svg.card import Piano
        kwargs = pickle.loads(pickle.dumps(kwargs))  # faster than copy.deepcopy
        kwargs.setdefault('class_', tuple(self.intervalset.names))
        setdefault_path(kwargs, 'header_kwargs.title', self.str_names)
        setdefault_path(kwargs, 'regular_piano_kwargs.note_colors', {note: config.interval_colors[interval] for note, interval in self.note_to_interval.items()})
        return Piano(**kwargs).svg

    def svg_plane_piano(self, **kwargs: Any) -> svg.SVG:
        kwargs = pickle.loads(pickle.dumps(kwargs))  # faster than copy.deepcopy
        kwargs.setdefault('interval_colors', {i: config.interval_colors[i] for i in self.intervalset.intervals})
        setdefault_path(kwargs, 'header_kwargs.title', self.str_names)
        return PlanePiano(**kwargs).svg
