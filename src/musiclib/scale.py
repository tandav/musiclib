from __future__ import annotations

import functools
import itertools
from collections import defaultdict
from typing import Any

from musiclib import config
from musiclib.chord import Chord
from musiclib.config import BLACK_BRIGHT
from musiclib.config import BLUE
from musiclib.config import GREEN
from musiclib.config import RED
from musiclib.note import Note
from musiclib.noteset import NoteSet
from musiclib.svg.piano import Piano


class Scale(NoteSet):
    intervals_to_name = {
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
    }
    name_to_intervals = {v: k for k, v in intervals_to_name.items()}
    root: Note
    name: str

    def __init__(
        self,
        notes: frozenset[Note],
        *,
        root: Note,
    ):
        # if not isinstance(root, str | Note):

        super().__init__(notes, root=root)

        if self.name is None:
            raise TypeError('scale is not supported')
        self.kind = config.kinds[self.name]
        scales = getattr(config, self.kind)
        _scale_i = scales.index(self.name)
        scales = scales[_scale_i:] + scales[:_scale_i]
        self.note_scales = {}
        for note, scale in zip(self.notes_ascending, scales, strict=True):
            self.note_scales[note] = scale

        if self.kind == 'natural':
            self.triads = self._make_nths(frozenset({0, 2, 4}))
            self.sevenths = self._make_nths(frozenset({0, 2, 4, 6}))
            self.ninths = self._make_nths(frozenset({0, 2, 4, 6, 8}))
            self.notes_to_triad_root = {triad.notes: triad.root for triad in self.triads}
            self.notes_to_seventh_root = {seventh.notes: seventh.root for seventh in self.sevenths}
            self.notes_to_ninth_root = {ninth.notes: ninth.root for ninth in self.ninths}

    def _make_nths(self, ns: frozenset[int]) -> tuple[Chord, ...]:
        return tuple(
            Chord(frozenset(self.notes_ascending[(i + n) % len(self)] for n in ns), root=self.notes_ascending[i])
            for i in range(len(self))
        )

    def parallel(self, parallel_name: str) -> Scale:
        """same root, changes set of notess"""
        return Scale.from_name(self.root, parallel_name)

    def relative(self, relative_name: str) -> Scale:
        """same set of notes, changes root"""
        for note, name in self.note_scales.items():
            if name == relative_name:
                return Scale.from_name(note, name)
        raise KeyError(f'relative {relative_name} scale not found')

    def _repr_svg_(self, **kwargs: Any) -> str:
        kwargs.setdefault('note_colors', {note: config.scale_colors[scale] for note, scale in self.note_scales.items()})
        if C_name := self.note_scales.get(Note('C'), ''):
            C_name = f' | C {C_name}'
        kwargs.setdefault('title', f'{self.root.name} {self.name}{C_name}')
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
