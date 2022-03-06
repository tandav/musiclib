from __future__ import annotations

import functools
import itertools
from collections import defaultdict

from musictool import config
from musictool.chord import Chord
from musictool.note import Note
from musictool.noteset import NoteSet
from musictool.piano import Piano
from musictool.util.color import hex_to_rgb
from musictool.util.iteration import iter_scales
from musictool.util.text import cprint


class Scale(NoteSet):
    intervals_to_name = {
        # diatonic
        frozenset({2, 4, 5, 7, 9, 11}): 'major',
        frozenset({2, 3, 5, 7, 9, 10}): 'dorian',
        frozenset({1, 3, 5, 7, 8, 10}): 'phrygian',
        frozenset({2, 4, 6, 7, 9, 11}): 'lydian',
        frozenset({2, 4, 5, 7, 9, 10}): 'mixolydian',
        frozenset({2, 3, 5, 7, 8, 10}): 'minor',
        frozenset({1, 3, 5, 6, 8, 10}): 'locrian',
        # harmonic
        frozenset({2, 3, 5, 7, 8, 11}): 'h_minor',
        frozenset({1, 3, 5, 6, 9, 10}): 'h_locrian',
        frozenset({2, 4, 5, 8, 9, 11}): 'h_major',
        frozenset({2, 3, 6, 7, 9, 10}): 'h_dorian',
        frozenset({1, 4, 5, 7, 8, 10}): 'h_phrygian',
        frozenset({3, 4, 6, 7, 9, 11}): 'h_lydian',
        frozenset({1, 3, 4, 6, 8, 9}): 'h_mixolydian',
        # melodic
        frozenset({2, 3, 5, 7, 9, 11}): 'm_minor',
        frozenset({1, 3, 5, 7, 9, 10}): 'm_locrian',
        frozenset({2, 4, 6, 8, 9, 11}): 'm_major',
        frozenset({2, 4, 6, 7, 9, 10}): 'm_dorian',
        frozenset({2, 4, 5, 7, 8, 10}): 'm_phrygian',
        frozenset({2, 3, 5, 6, 8, 10}): 'm_lydian',
        frozenset({1, 3, 4, 6, 8, 10}): 'm_mixolydian',
        # pentatonic
        frozenset({2, 4, 7, 9}): 'p_major',
        frozenset({2, 5, 7, 10}): 'p_dorian',
        frozenset({3, 5, 8, 10}): 'p_phrygian',
        frozenset({2, 5, 7, 9}): 'p_mixolydian',
        frozenset({3, 5, 7, 10}): 'p_minor',
        # sudu
        frozenset({2, 4, 5, 7, 9}): 's_major',
        frozenset({2, 3, 5, 7, 10}): 's_dorian',
        frozenset({1, 3, 5, 8, 10}): 's_phrygian',
        frozenset({2, 4, 7, 9, 11}): 's_lydian',
        frozenset({2, 5, 7, 9, 10}): 's_mixolydian',
        frozenset({3, 5, 7, 8, 10}): 's_minor',
    }
    name_to_intervals = {v: k for k, v in intervals_to_name.items()}

    def __init__(
        self,
        notes: frozenset[str | Note],
        *,
        root: str | Note,
    ):
        super().__init__(notes, root=root)
        self.kind = config.kinds.get(self.name)

        if self.kind is not None:
            self.note_colors = {}
            self.note_scales = {}

            for note, scale in zip(self.notes_ascending, iter_scales(self.kind, start=self.name)):
                self.note_colors[note] = hex_to_rgb(config.scale_colors[scale])
                self.note_scales[note] = scale

            if self.kind == 'diatonic':
                self.triads = self._make_nths(frozenset({0, 2, 4}))
                self.sevenths = self._make_nths(frozenset({0, 2, 4, 6}))
                self.ninths = self._make_nths(frozenset({0, 2, 4, 6, 8}))
                self.notes_to_triad_root = {triad.notes: triad.root for triad in self.triads}
                self.notes_to_seventh_root = {seventh.notes: seventh.root for seventh in self.sevenths}
                self.notes_to_ninth_root = {ninth.notes: ninth.root for ninth in self.ninths}

        self.html_classes = ('card', self.name)

    def _make_nths(self, ns: frozenset[int]) -> tuple[Chord]:
        return tuple(
            Chord(frozenset(self.notes_ascending[(i + n) % len(self)] for n in ns), root=self.notes_ascending[i])
            for i in range(len(self))
        )

    def parallel(self, parallel_name: str | None = None) -> Scale:
        """same root, convert major to minor and vice versa"""
        if parallel_name is None:
            parallel_name = {'major': 'minor', 'minor': 'major'}[self.name]
        return Scale.from_name(self.root, parallel_name)

    def relative(self, relative_name: str | None = None) -> Scale:
        """same set of notes, changes root, convert major to minor and vice versa"""
        if relative_name is None:
            relative_name = {'major': 'minor', 'minor': 'major'}[self.name]
        for note, name in self.note_scales.items():
            if name == relative_name:
                return Scale.from_name(note, name)

    def to_piano_image(self):
        return Piano(scale=self)._repr_svg_()

    def with_html_classes(self, classes: tuple):
        prev = self.html_classes
        self.html_classes = prev + classes
        r = self._repr_html_()
        self.html_classes = prev
        return r

    def _repr_html_(self):
        # <code>bits: {self.bits}</code><br>
        # chords_hover = f"title='{self._chords_text()}'" if self.kind =='diatonic' else ''
        chords_hover = ''
        if C_name := self.note_scales.get(Note('C'), ''):
            C_name = f' | C {C_name}'
        return f'''
        <div class='{' '.join(self.html_classes)}' {chords_hover}>
        <a href='{self.root.name}'><span class='card_header'><h3>{self.root.name} {self.name}{C_name}</h3></span></a>
        {self.to_piano_image()}
        </div>
        '''

# flake8: noqa


class ComparedScales:
    '''
    this is compared scale
    local terminology: left scale is compared to right
    left is kinda parent, right is kinda child
    '''

    def __init__(self, left: Scale, right: Scale):
        self.left = left
        self.right = right
        self.key = left, right
        self.shared_notes = frozenset(left.notes) & frozenset(right.notes)
        self.new_notes = frozenset(right.notes) - frozenset(left.notes)
        self.del_notes = frozenset(left.notes) - frozenset(right.notes)
        if right.kind == 'diatonic':
            self.shared_triads = frozenset(left.triads) & frozenset(right.triads)
        self.html_classes = ('card',)

    def with_html_classes(self, classes: tuple):
        prev = self.html_classes
        self.html_classes = prev + classes
        r = self._repr_html_()
        self.html_classes = prev
        return r

    # def __format__(self, format_spec): raise No

    # @functools.cached_property
    def _repr_html_(self):
        # <code>bits: {self.bits}</code><br>
        # chords_hover = f"title='{self._chords_text()}'" if self.kind =='diatonic' else ''
        chords_hover = ''
        if C_name := self.right.note_scales.get(Note('C'), ''):
            C_name = f' | C {C_name}'
        return f'''
        <div class='{' '.join(self.html_classes)}' {chords_hover}>
        <a href='{self.right.root.name}'><span class='card_header'><h3>{self.right.root.name} {self.right.name}{C_name}</h3></span></a>
        {self.to_piano_image()}
        </div>
        '''

    def to_piano_image(self, as_base64=False):

        return Piano(
            scale=self.right,
            red_notes=self.del_notes, green_notes=self.new_notes, blue_notes=self.shared_notes,
            notes_squares={
                chord.root: (
                    hex_to_rgb(config.chord_colors[chord.name]),
                    config.BLUE_COLOR if chord in self.shared_triads else config.BLACK_COLOR,
                    config.BLUE_COLOR if chord in self.shared_triads else config.BLACK_COLOR,
                    str(chord),
                )
                for chord in self.right.triads
            } if self.right.kind == 'diatonic' else dict(),
        )._repr_svg_()

    def __eq__(self, other): return self.key == other.key
    def __hash__(self): return hash(self.key)
    def __repr__(self): return f'ComparedScale({self.left.root} {self.left.name} | {self.right.root} {self.right.name})'


diatonic = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.diatonic)}
harmonic = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.harmonic)}
melodic = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.melodic)}
pentatonic = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.pentatonic)}
sudu = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.sudu)}
all_scales = {
    'diatonic': diatonic,
    'harmonic': harmonic,
    'melodic': melodic,
    'pentatonic': pentatonic,
    'sudu': sudu,
}

# circle of fifths clockwise
majors = dict(
    diatonic=tuple(diatonic[note, 'major'] for note in 'CGDAEBfdaebF'),
    harmonic=tuple(harmonic[note, 'h_major'] for note in 'CGDAEBfdaebF'),
    melodic=tuple(melodic[note, 'm_major'] for note in 'CGDAEBfdaebF'),
    pentatonic=tuple(pentatonic[note, 'p_major'] for note in 'CGDAEBfdaebF'),
    sudu=tuple(sudu[note, 's_major'] for note in 'CGDAEBfdaebF'),
)


@functools.cache
def neighbors(left: Scale):
    neighs = defaultdict(list)
    for right in all_scales[left.kind].values():
        # if left == right:
        #     continue
        right = ComparedScales(left, right)
        neighs[len(right.shared_notes)].append(right)
    return neighs


def print_neighbors(s: Scale):
    neighs = neighbors(s)
    for n_intersect in sorted(neighs.keys(), reverse=True):
        for n in neighs[n_intersect]:
            if n.name != 'major': continue
            print(repr(n).ljust(32), '|', end=' ')
            for note in n.chromatic_mask:
                if note in s.chromatic_mask: print(cprint(note, color='BLUE'), end='')
                else: print(note, end='')
            print(' |', end=' ')
            for chord in n.triads:
                if chord in n.shared_triads: print(cprint(chord, color='BLUE'), end=' ')
                else: print(chord, end=' ')
            print()
        print('=' * 100)

# warm up cache
# for scale in tqdm.tqdm(tuple(itertools.chain(all_scales['diatonic'].values(), all_scales['pentatonic'].values()))):
#     _ = scale.to_piano_image(as_base64=True)
#     for neighbor in itertools.chain.from_iterable(neighbors(scale).values()):
#         _ = neighbor.to_piano_image(as_base64=True)
