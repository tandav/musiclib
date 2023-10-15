from __future__ import annotations

import operator
import warnings
from typing import TYPE_CHECKING

import svg
from colortool import Color

from musiclib.config import BLACK_PALE
from musiclib.config import BLUE
from musiclib.config import GREEN
from musiclib.midi.pitchbend import make_notes_pitchbends
from musiclib.svg.isomorphic import IsoPiano
from musiclib.noteset import SpecificNoteSet
from musiclib.note import SpecificNote

if TYPE_CHECKING:
    from svg._types import Number

    from musiclib.midi.parse import Midi
    from musiclib.midi.parse import MidiNote
    from musiclib.midi.parse import MidiPitch


class PianoRoll:
    def __init__(
        self,
        midi: Midi,
        pitchbend_semitones: int = 2,
        key_width: int = 20,
        key_height: int = 400,
        time_signature: tuple[int, int] = (4, 4),
        grid_denominator: int = 4,
        start_stop: tuple[SpecificNote, SpecificNote] | None = None,
    ) -> None:
        if time_signature != (4, 4):
            raise NotImplementedError('only time_signature=(4, 4) is supported')
        self.time_signature = time_signature
        if grid_denominator < 1:
            raise ValueError('grid_denominator should be >= 1')
        self.grid_denominator = grid_denominator
        if start_stop is None:
            start_stop = (
                min(midi.notes, key=operator.attrgetter('note')).note,
                max(midi.notes, key=operator.attrgetter('note')).note,
            )
        self.sns = SpecificNoteSet.from_noterange(*start_stop)
        self.key_width = key_width
        self.key_height = key_height
        self.piano = IsoPiano(radius=key_width, key_height=key_height)
        self.midi = midi
        self.duration = max(self.midi.notes, key=operator.attrgetter('off')).off
        self.pitchbend_semitones = pitchbend_semitones
        self.elements = self.piano.elements.copy()
        self.draw_bar_lines()
        self.add_notes_elements()
        self.add_pitchbend_elements()

    def add_notes_elements(self) -> None:
        for i, note in enumerate(self.midi.notes):
            if note.note not in self.sns:
                warnings.warn(f'note {note.note} is not in {self.sns}')
                continue
            x = self.piano.width * self.sns.index(note.note)
            h = (note.off - note.on) / self.duration * self.piano.height
            y = note.on / self.duration * self.piano.height
            y_svg = self.piano.height - y - h
            self.elements.append(
                svg.Rect(
                    id=f'note-{i}',
                    class_=['note', str(note.note)],
                    x=x,
                    y=y_svg,
                    width=self.piano.width,
                    height=h,
                    fill=Color(0xFC7B7B).css_hex,
                    stroke_width=1,
                    stroke=BLACK_PALE.css_hex,
                    onclick=f"select_note('note-{i}')",
                ),
            )

    def add_pitchbend_elements(self) -> None:
        if not self.midi.pitchbend:
            return

        PITCHBEND_MAX = 8192  # noqa: N806

        defs = svg.Defs(
            elements=[
                svg.Marker(
                    id='circle',
                    markerWidth=4,
                    markerHeight=4,
                    refX=2,
                    refY=2,
                    elements=[svg.Circle(cx=2, cy=2, r=2, stroke='none', fill=BLUE.css_hex)],
                ),
            ],
        )
        self.elements.append(defs)

        def note_pitch_x(note: MidiNote, p: MidiPitch) -> int:
            return int(self.piano.width * self.piano.sns.index(note.note) + self.piano.width // 2 + self.pitchbend_semitones * self.piano.width * p.pitch / PITCHBEND_MAX)

        for note, pitches in make_notes_pitchbends(self.midi).items():
            if note.note not in self.piano.sns:
                warnings.warn(f'note {note.note} is not in {self.piano.sns}')
                continue
            polyline_points_notes: list[Number] = []
            for pitch in pitches:
                x = note_pitch_x(note, pitch)
                y = pitch.time / self.duration * self.piano.height
                y_svg = self.piano.height - y
                polyline_points_notes += [x, y_svg]
            self.elements.append(
                svg.Polyline(
                    points=polyline_points_notes,
                    stroke=GREEN.css_hex,
                    fill='none',
                    stroke_width=2,
                    marker_start='circle',
                    marker_mid='circle',
                    marker_end='circle',
                ),
            )

        def pitch_x(p: MidiPitch) -> int:
            return int(self.piano.width / 2 * (p.pitch / PITCHBEND_MAX + 1))

        polyline_points: list[Number] = []
        for pitch in self.midi.pitchbend:
            x = pitch_x(pitch)
            y = pitch.time / self.duration * self.piano.height
            y_svg = self.piano.height - y
            polyline_points += [x, y_svg]
        self.elements.append(
            svg.Polyline(
                points=polyline_points,
                stroke=BLUE.css_hex,
                fill='none',
                stroke_width=2,
                marker_start='url(#circle)',
                marker_mid='url(#circle)',
                marker_end='url(#circle)',
            ),
        )

    def draw_bar_lines(self) -> None:
        ticks_per_bar = self.midi.ticks_per_beat * self.time_signature[0]
        for i in range(0, self.duration, ticks_per_bar // self.grid_denominator):
            stroke_width = 0.5 if i % self.midi.ticks_per_beat == 0 else 0.125
            y = self.piano.height - i / self.duration * self.piano.height
            self.elements.append(
                svg.Line(
                    x1=0,
                    x2=self.piano.width,
                    y1=y,
                    y2=y,
                    stroke=Color(0x404040).css_hex,
                    stroke_width=stroke_width,
                ),
            )

    @property
    def svg(self) -> svg.SVG:
        return svg.SVG(width=self.piano.width, height=self.piano.height, elements=self.elements)

    def _repr_svg_(self) -> str:
        return str(self.svg)
