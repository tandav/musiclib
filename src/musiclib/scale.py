from __future__ import annotations

import functools
import itertools
from typing import TYPE_CHECKING

from collections import defaultdict
from typing import Any
from typing import ClassVar
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
    intervals_to_name: ClassVar[dict[frozenset[int], str]] = {
        # natural
        frozenset({0, 2, 4, 5, 7, 9, 11}): 'major',
        frozenset({0, 2, 3, 5, 7, 9, 10}): 'dorian',
        frozenset({0, 1, 3, 5, 7, 8, 10}): 'phrygian',
        frozenset({0, 2, 4, 6, 7, 9, 11}): 'lydian',
        frozenset({0, 2, 4, 5, 7, 9, 10}): 'mixolydian',
        frozenset({0, 2, 3, 5, 7, 8, 10}): 'minor',
        frozenset({0, 1, 3, 5, 6, 8, 10}): 'locrian',
        # harmonic
        frozenset({0, 2, 3, 5, 7, 8, 11}): 'h_minor',
        frozenset({0, 1, 3, 5, 6, 9, 10}): 'h_locrian',
        frozenset({0, 2, 4, 5, 8, 9, 11}): 'h_major',
        frozenset({0, 2, 3, 6, 7, 9, 10}): 'h_dorian',
        frozenset({0, 1, 4, 5, 7, 8, 10}): 'h_phrygian',
        frozenset({0, 3, 4, 6, 7, 9, 11}): 'h_lydian',
        frozenset({0, 1, 3, 4, 6, 8, 9}): 'h_mixolydian',
        # melodic
        frozenset({0, 2, 3, 5, 7, 9, 11}): 'm_minor',
        frozenset({0, 1, 3, 5, 7, 9, 10}): 'm_locrian',
        frozenset({0, 2, 4, 6, 8, 9, 11}): 'm_major',
        frozenset({0, 2, 4, 6, 7, 9, 10}): 'm_dorian',
        frozenset({0, 2, 4, 5, 7, 8, 10}): 'm_phrygian',
        frozenset({0, 2, 3, 5, 6, 8, 10}): 'm_lydian',
        frozenset({0, 1, 3, 4, 6, 8, 10}): 'm_mixolydian',
        # pentatonic
        frozenset({0, 2, 4, 7, 9}): 'p_major',
        frozenset({0, 2, 5, 7, 10}): 'p_dorian',
        frozenset({0, 3, 5, 8, 10}): 'p_phrygian',
        frozenset({0, 2, 5, 7, 9}): 'p_mixolydian',
        frozenset({0, 3, 5, 7, 10}): 'p_minor',
        # sudu
        frozenset({0, 2, 4, 5, 7, 9}): 's_major',
        frozenset({0, 2, 3, 5, 7, 10}): 's_dorian',
        frozenset({0, 1, 3, 5, 8, 10}): 's_phrygian',
        frozenset({0, 2, 4, 7, 9, 11}): 's_lydian',
        frozenset({0, 2, 5, 7, 9, 10}): 's_mixolydian',
        frozenset({0, 3, 5, 7, 8, 10}): 's_minor',

        # chords: all have c_ prefix to distinguish from scales
        # triads
        frozenset({0, 4, 7}): 'c_major',
        frozenset({0, 3, 7}): 'c_minor',
        frozenset({0, 3, 6}): 'c_diminished',
        # 7th
        frozenset({0, 4, 7, 11}): 'c_maj7',
        frozenset({0, 4, 7, 10}): 'c_7',
        frozenset({0, 3, 7, 10}): 'c_min7',
        frozenset({0, 3, 6, 10}): 'c_half-dim7',
        frozenset({0, 3, 6, 9}): 'c_dim7',
        # 6th
        frozenset({0, 4, 7, 9}): 'c_6',
        frozenset({0, 3, 7, 9}): 'c_m6',
        # etc
        frozenset({0, 4, 8}): 'c_aug',
        frozenset({0, 2, 7}): 'c_sus2',
        frozenset({0, 5, 7}): 'c_sus4',
    }
    name_to_intervals: ClassVar[dict[str, frozenset[int]]] = {v: k for k, v in intervals_to_name.items()}
    root: Note
    name: str

    def __init__(self, root: Note, intervals: frozenset[int]):
        self.root = root
        self.intervals = intervals
        self.notes = frozenset({root + interval for interval in intervals})
        self.name = self.__class__.intervals_to_name.get(intervals)
        self.kind = config.kinds.get(self.name)

        _notes_octave_fit = sorted(self.notes)
        _root_i = _notes_octave_fit.index(root)
        self.notes_ascending = _notes_octave_fit[_root_i:] + _notes_octave_fit[:_root_i]
        self.intervals_ascending = tuple(note - self.root for note in self.notes_ascending)                   
        self.note_to_interval = dict(zip(self.notes_ascending, self.intervals_ascending, strict=False))
        self.bits = intervals_to_bits(self.intervals)
        self.bits_notes = tuple(int(Note(note) in self.notes) for note in config.chromatic_notes)
        self.note_i = {note: i for i, note in enumerate(self.notes_ascending)}
        self.key = self.root, self.intervals

        if self.kind is not None: # TODO: refactor this
            scales = getattr(config, self.kind)
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
        return cls(root, cls.name_to_intervals[name])
    
    @classmethod
    def from_notes(cls: type[Self], root: Note, notes: frozenset[Note]) -> Self:
        if not isinstance(root, Note):
            raise TypeError(f'expected Note, got {type(root)}')
        return cls(root, frozenset(note - root for note in notes))
    
    @classmethod
    def from_str(cls: type[Self], string: str) -> Self:
        if string[-2] != '/':
            raise ValueError('scale string must ends with scale root, example "CDEFGAB/C"')
        return cls.from_notes(Note(string[-1]), frozenset(Note(note) for note in string[:-2]))
    
    @classmethod
    def all_scales(cls: type[Self], kind: str) -> tuple[Self, ...]:
        return frozenset(cls.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, getattr(config, kind)))

    def transpose_to_note(self, note: Note) -> Scale:
        return Scale.from_intervals(note, self.intervals)

    @functools.cached_property
    def noteset(self) -> NoteSet:
        return NoteSet(self.notes)
    
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
        return f"{''.join(note.name for note in self)}/{self.root}"

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


# flake8: noqa


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
        if right.kind == 'natural':
            self.shared_triads = frozenset(left.triads) & frozenset(right.triads)

    def _repr_svg_(self, **kwargs: Any) -> str:
        if left_root_name := self.right.note_scales.get(self.left.root, ''):
            kwargs.setdefault('background_color', config.scale_colors[left_root_name])
            left_root_name = f' | {self.left.root.name} {left_root_name}'

        kwargs.setdefault('note_colors', {note: config.scale_colors[scale] for note, scale in self.right.note_scales.items()})
        kwargs.setdefault('top_rect_colors', dict.fromkeys(self.del_notes, RED) | dict.fromkeys(self.new_notes, GREEN) | dict.fromkeys(self.shared_notes, BLUE))
        kwargs.setdefault(
            'squares', {
                chord.root: {
                    'fill_color': config.chord_colors[chord.name],
                    'border_color': BLUE if chord in self.shared_triads else BLACK_BRIGHT,
                    'text_color': BLUE if chord in self.shared_triads else BLACK_BRIGHT,
                    'text': chord.root.name,
                    'onclick': f'play_chord("{chord}")',
                }
                for chord in self.right.triads
            } if self.right.kind == 'natural' else {},
        )

        kwargs.setdefault('classes', ('card',))
        kwargs.setdefault('title', f'{self.right.root.name} {self.right.name}{left_root_name}')
        return Piano(**kwargs)._repr_svg_()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ComparedScales):
            return NotImplemented
        return self.key == other.key

    def __hash__(self) -> int:
        return hash(self.key)

    def __repr__(self) -> str:
        return f'ComparedScale({self.left.root} {self.left.name} | {self.right.root} {self.right.name})'


natural = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.natural)}
harmonic = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.harmonic)}
melodic = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.melodic)}
pentatonic = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.pentatonic)}
sudu = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.sudu)}
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
