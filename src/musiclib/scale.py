from __future__ import annotations

import functools
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterator
from musiclib import config
from musiclib.config import BLACK_BRIGHT
from musiclib.config import BLUE
from musiclib.config import GREEN
from musiclib.config import RED
from musiclib.note import Note
from musiclib.noteset import NoteSet
from musiclib.svg.piano import Piano
from musiclib.util.cache import Cached
from musiclib.util.etc import intervals_to_bits

Self = TypeVar('Self', bound='Scale')


class Scale(Cached):
    def __init__(self, root: Note, intervals: frozenset[int]) -> None:
        if not isinstance(root, Note):
            raise TypeError(f'expected Note, got {type(root)}')
        if not isinstance(intervals, frozenset):
            raise TypeError(f'expected frozenset, got {type(intervals)}')
        self.root = root
        self.intervals = intervals
        self.notes = frozenset({root + interval for interval in intervals})
        self.noteset = NoteSet(self.notes)
        self.names: frozenset[str] = config.intervals_to_names.get(intervals, frozenset())
        self.name_kinds = {name: config.kinds[name] for name in self.names}
        _notes_octave_fit = sorted(self.notes)
        _root_i = _notes_octave_fit.index(root)
        self.notes_ascending = _notes_octave_fit[_root_i:] + _notes_octave_fit[:_root_i]
        self.intervals_ascending = tuple(note - self.root for note in self.notes_ascending)
        self.note_to_interval = dict(zip(self.notes_ascending, self.intervals_ascending, strict=False))
        self.bits = intervals_to_bits(self.intervals)
        self.bits_chromatic_notes = tuple(int(Note(note) in self.notes) for note in config.chromatic_notes)
        self.note_i = {note: i for i, note in enumerate(self.notes_ascending)}
        self._key = self.root, self.intervals

    @classmethod
    def from_name(cls: type[Self], root: str | Note, name: str) -> Self:
        if isinstance(root, str):
            root = Note(root)
        elif not isinstance(root, Note):
            raise TypeError(f'expected str | Note, got {type(root)}')
        return cls(root, config.name_to_intervals[name])

    @classmethod
    def from_notes(cls: type[Self], root: Note, notes: frozenset[Note]) -> Self:
        if not isinstance(root, Note):
            raise TypeError(f'expected Note, got {type(root)}')
        if root not in notes:
            raise ValueError('scale root must be in scale notes')
        return cls(root, frozenset(note - root for note in notes))

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
        for name, kind in self.name_kinds.items():
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
        return Scale(note, self.intervals)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Scale):
            return NotImplemented
        return self._key == other._key

    def __hash__(self) -> int:
        return hash(self._key)

    def __len__(self) -> int:
        return len(self.intervals)

    def __getitem__(self, item: int) -> Note:
        return self.notes_ascending[item]

    def __iter__(self) -> Iterator[Note]:
        return iter(self.notes_ascending)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, Note):
            return NotImplemented
        return item in self.notes

    @property
    def str_names(self) -> str:
        return f"{self.root} {' '.join(sorted(self.names))}"

    def __str__(self) -> str:
        return f"{''.join(note.name for note in self.notes_ascending)}/{self.root}"

    def __repr__(self) -> str:
        return f'Scale({self.root!r}, {self.intervals!r})'

    def __getnewargs__(self) -> tuple[Note, frozenset[int]]:
        return (self.root, self.intervals)

    def _repr_svg_(self, **kwargs: Any) -> str:
        kwargs.setdefault('note_colors', {note: config.interval_colors[interval] for note, interval in self.note_to_interval.items()})
        kwargs.setdefault('title', f'{self.str_names}')
        kwargs.setdefault('classes', ('card', *self.names))
        return Piano(**kwargs)._repr_svg_()


class ComparedScales:
    """
    this is compared scale
    local terminology: left scale is compared to right
    left is kinda parent, right is kinda child
    """

    def __init__(self, left: Scale, right: Scale) -> None:
        self.left = left
        self.right = right
        self.key = left, right
        self.shared_notes = frozenset(left.notes) & frozenset(right.notes)
        self.new_notes = frozenset(right.notes) - frozenset(left.notes)
        self.del_notes = frozenset(left.notes) - frozenset(right.notes)
        self.left_triads = frozenset(left.nths(config.nths['triads']))
        self.right_triads = frozenset(right.nths(config.nths['triads']))
        self.shared_triads = self.left_triads & self.right_triads

    def _repr_svg_(self, **kwargs: Any) -> str:
        if self.right.note_scales is not None and self.left.root in self.right.note_scales:
            kwargs.setdefault('background_color', config.interval_colors[self.right.note_to_interval[self.left.root]])

        chord_colors = {
            frozenset({'major_0'}): config.interval_colors[0],
            frozenset({'minor_0'}): config.interval_colors[8],
            frozenset({'dim_0'}): config.interval_colors[11],
        }

        kwargs.setdefault('note_colors', {note: config.interval_colors[interval] for note, interval in self.left.note_to_interval.items()})
        kwargs.setdefault('top_rect_colors', dict.fromkeys(self.del_notes, RED) | dict.fromkeys(self.new_notes, GREEN) | dict.fromkeys(self.shared_notes, BLUE))
        kwargs.setdefault(
            'squares', {
                chord.root: {
                    'fill_color': chord_colors[chord.names],
                    'border_color': BLUE if chord in self.shared_triads else BLACK_BRIGHT,
                    'text_color': BLUE if chord in self.shared_triads else BLACK_BRIGHT,
                    'text': chord.root.name,
                    'onclick': f'play_chord("{chord}")',
                }
                for chord in self.right_triads
            } if set(self.right.name_kinds.values()) == {'natural'} else {},
        )
        kwargs.setdefault('classes', ('card',))
        kwargs.setdefault('title', f'{self.left.str_names} | {self.right.str_names}')
        return Piano(**kwargs)._repr_svg_()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ComparedScales):
            return NotImplemented
        return self.key == other.key

    def __hash__(self) -> int:
        return hash(self.key)

    def __repr__(self) -> str:
        return f'ComparedScale({self.left.str_names} | {self.right.str_names})'
