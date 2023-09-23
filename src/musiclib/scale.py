from __future__ import annotations

import functools
import itertools
from typing import TYPE_CHECKING

from collections import defaultdict
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
from musiclib.svg.piano import Piano
from musiclib.noteset import NoteSet
from musiclib.util.cache import Cached
from musiclib.util.etc import intervals_to_bits

Self = TypeVar('Self', bound='Scale')


class Scale(Cached):
    def __init__(self, root: Note, intervals: frozenset[int]):
        if not isinstance(root, Note):
            raise TypeError(f'expected Note, got {type(root)}')
        if not isinstance(intervals, frozenset):
            raise TypeError(f'expected frozenset, got {type(intervals)}')
        self.root = root
        self.intervals = intervals
        self.notes = frozenset({root + interval for interval in intervals})
        self.name = config.intervals_to_name.get(intervals)
        self.kind = config.kinds.get(self.name)

        _notes_octave_fit = sorted(self.notes)
        _root_i = _notes_octave_fit.index(root)
        self.notes_ascending = _notes_octave_fit[_root_i:] + _notes_octave_fit[:_root_i]
        self.notes_str = f"{''.join(note.name for note in self.notes_ascending)}/{self.root}"
        self.intervals_ascending = tuple(note - self.root for note in self.notes_ascending)                   
        self.note_to_interval = dict(zip(self.notes_ascending, self.intervals_ascending, strict=False))
        self.bits = intervals_to_bits(self.intervals)
        self.bits_chromatic_notes = tuple(int(Note(note) in self.notes) for note in config.chromatic_notes)
        self.note_i = {note: i for i, note in enumerate(self.notes_ascending)}
        self._key = self.root, self.intervals

        if self.kind is not None: # TODO: refactor this
            scales = config.scale_order[self.kind]
            _scale_i = scales.index(self.name)
            scales = scales[_scale_i:] + scales[:_scale_i]
            self.note_scales = {}
            for note, scale in zip(self.notes_ascending, scales, strict=True):
                self.note_scales[note] = scale
        else:
            self.note_scales = None

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
        if not root in notes:
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
    
    @classmethod
    def all_scales(cls: type[Self], kind: str) -> tuple[Self, ...]:
        return frozenset(cls.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, getattr(config, kind)))

    def nths(self, ns: frozenset[int]) -> tuple[Scale, ...]:
        return tuple(
            Scale.from_notes(self.notes_ascending[i], frozenset(self.notes_ascending[(i + n) % len(self)] for n in ns))
            for i in range(len(self))
        )

    def transpose_to_note(self, note: Note) -> Scale:
        return Scale(note, self.intervals)

    @functools.cached_property
    def noteset(self) -> NoteSet:
        return NoteSet(self.notes)
    
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
    
    def __str__(self) -> str:
        if self.name is not None:
            return f"{self.root} {self.name}"
        return self.notes_str

    def __repr__(self) -> str:
        if self.name is not None:
            return f"Scale.from_name('{self.root}', '{self.name}')"
        return f'Scale(root={self.root!r}, intervals={self.intervals!r})'
    
    def __getnewargs__(self) -> tuple[Note, frozenset[int]]:
        return (self.root, self.intervals)

    def _repr_svg_(self, **kwargs: Any) -> str:
        kwargs.setdefault('note_colors', {note: config.interval_colors[interval] for note, interval in self.note_to_interval.items()})
        kwargs.setdefault('title', f'{self.root.name} {self.name}')
        kwargs.setdefault('classes', ('card', self.name))
        return Piano(**kwargs)._repr_svg_()


class ComparedScales:
    """
    this is compared scale
    local terminology: left scale is compared to right
    left is kinda parent, right is kinda child
    """

    def __init__(self, left: Scale, right: Scale):
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
            'major_0': config.interval_colors[0],
            'minor_0': config.interval_colors[8],
            'dim_0': config.interval_colors[11],
        }

        kwargs.setdefault('note_colors', {note: config.interval_colors[interval] for note, interval in self.left.note_to_interval.items()})
        kwargs.setdefault('top_rect_colors', dict.fromkeys(self.del_notes, RED) | dict.fromkeys(self.new_notes, GREEN) | dict.fromkeys(self.shared_notes, BLUE))
        kwargs.setdefault(
            'squares', {
                chord.root: {
                    'fill_color': chord_colors[chord.name],
                    'border_color': BLUE if chord in self.shared_triads else BLACK_BRIGHT,
                    'text_color': BLUE if chord in self.shared_triads else BLACK_BRIGHT,
                    'text': chord.root.name,
                    'onclick': f'play_chord("{chord}")',
                }
                for chord in self.right_triads
            } if self.right.kind == 'natural' else {},
        )

        kwargs.setdefault('classes', ('card',))
        left_title = f'{self.left.root.name} {self.left.name}' if self.left.name is not None else str(self.left)
        right_title = f'{self.right.root.name} {self.right.name}' if self.right.name is not None else str(self.right)
        kwargs.setdefault('title', f'{left_title} | {right_title}')
        return Piano(**kwargs)._repr_svg_()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ComparedScales):
            return NotImplemented
        return self.key == other.key

    def __hash__(self) -> int:
        return hash(self.key)

    def __repr__(self) -> str:
        return f'ComparedScale({self.left.root} {self.left.name} | {self.right.root} {self.right.name})'


natural = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.scale_order['natural'])}
harmonic = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.scale_order['harmonic'])}
melodic = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.scale_order['melodic'])}
pentatonic = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.scale_order['pentatonic'])}
sudu = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.scale_order['sudu'])}
all_scales = {
    'natural': natural,
    'harmonic': harmonic,
    'melodic': melodic,
    'pentatonic': pentatonic,
    'sudu': sudu,
}

CIRCLE_OF_FIFTHS_CLOCKWISE = 'CGDAEBfdaebF'

# circle of fifths clockwise
majors = {
    'natural': tuple(natural[note, 'major'] for note in CIRCLE_OF_FIFTHS_CLOCKWISE),
    'harmonic': tuple(harmonic[note, 'h_major'] for note in CIRCLE_OF_FIFTHS_CLOCKWISE),
    'melodic': tuple(melodic[note, 'm_major'] for note in CIRCLE_OF_FIFTHS_CLOCKWISE),
    'pentatonic': tuple(pentatonic[note, 'p_major'] for note in CIRCLE_OF_FIFTHS_CLOCKWISE),
    'sudu': tuple(sudu[note, 's_major'] for note in CIRCLE_OF_FIFTHS_CLOCKWISE),
}


@functools.cache
def neighbors(left: Scale) -> dict[int, list[ComparedScales]]:
    neighs = defaultdict(list)
    for right_ in all_scales[left.kind].values():
        # if left == right:
        #     continue
        right = ComparedScales(left, right_)
        neighs[len(right.shared_notes)].append(right)
    return neighs
