from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import svg
from colortool import Color

from musiclib import config
from musiclib.midi.pitchbend import make_notes_pitchbends
from musiclib.noteset import SpecificNoteSet
from musiclib.svg.isomorphic.piano import IsoPiano
from musiclib.svg.isomorphic.text import FromIntervalDict

if TYPE_CHECKING:
    from svg._types import Number

    from musiclib.midi.parse import Midi
    from musiclib.midi.parse import MidiNote
    from musiclib.midi.parse import MidiPitch
    from musiclib.note import SpecificNote


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
        note_font_size: int = 10,
    ) -> None:
        if time_signature != (4, 4):
            raise NotImplementedError('only time_signature=(4, 4) is supported')
        self.time_signature = time_signature
        if grid_denominator < 1:
            raise ValueError('grid_denominator should be >= 1')
        self.grid_denominator = grid_denominator
        if start_stop is None:
            start_stop = (
                min(n.note for n in midi.notes),
                max(n.note for n in midi.notes),
            )
        self.sns = SpecificNoteSet.from_noterange(*start_stop)
        self.key_width = key_width
        self.key_height = key_height
        self.piano = IsoPiano(
            n_cols=len(self.sns),
            interval_colors=dict.fromkeys(self.sns.intervals, config.WHITE_PALE),
            interval_strokes=dict.fromkeys(self.sns.intervals, {'stroke': config.BLACK_PALE, 'stroke_width': 0.5}),
            interval_text=FromIntervalDict({i: str(n) for i, n in zip(self.sns.intervals, self.sns.notes_ascending, strict=True)}),
            radius=key_width // 2,
            radius1=key_height // 2,
        )
        self.midi = midi
        self.duration = max(n.off for n in self.midi.notes)
        self.pitchbend_semitones = pitchbend_semitones
        self.note_font_size = note_font_size
        self.elements = self.piano.elements.copy()
        self.draw_bar_lines()
        self.add_notes_elements()
        self.add_pitchbend_elements()

    def add_notes_elements(self) -> None:
        for i, note in enumerate(self.midi.notes):
            if note.note not in self.sns:
                warnings.warn(f'note {note.note} is not in {self.sns}')
                continue
            x = self.key_width * self.sns.index(note.note)
            h = (note.off - note.on) / self.duration * self.key_height
            y = note.on / self.duration * self.key_height
            y_svg = self.key_height - y - h
            self.elements.append(
                svg.Rect(
                    id=f'note-{i}',
                    class_=['note', str(note.note)],
                    x=x,
                    y=y_svg,
                    width=self.key_width,
                    height=h,
                    fill=Color(0xFC7B7B).css_hex,
                    stroke_width=1,
                    stroke=config.BLACK_PALE.css_hex,
                    onclick=f"select_note('note-{i}')",
                ),
            )
            self.elements.append(
                svg.Text(
                    id=f'note-{i}-text',
                    class_=['note-text', str(note.note)],
                    x=x + self.key_width / 2,
                    y=y_svg + h / 2,
                    text=str(note.note),
                    font_family='monospace',
                    font_size=self.note_font_size,
                    text_anchor='middle',
                    dominant_baseline='middle',
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
                    elements=[svg.Circle(cx=2, cy=2, r=2, stroke='none', fill=config.BLUE.css_hex)],
                ),
            ],
        )
        self.elements.append(defs)

        def note_pitch_x(note: MidiNote, p: MidiPitch) -> int:
            return int(self.key_width * self.sns.index(note.note) + self.key_width // 2 + self.pitchbend_semitones * self.key_width * p.pitch / PITCHBEND_MAX)

        for note, pitches in make_notes_pitchbends(self.midi).items():
            if note.note not in self.sns:
                warnings.warn(f'note {note.note} is not in {self.sns}')
                continue
            polyline_points_notes: list[Number] = []
            for pitch in pitches:
                x = note_pitch_x(note, pitch)
                y = pitch.time / self.duration * self.key_height
                y_svg = self.key_height - y
                polyline_points_notes += [x, y_svg]
            self.elements.append(
                svg.Polyline(
                    points=polyline_points_notes,
                    stroke=config.GREEN.css_hex,
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
            y = pitch.time / self.duration * self.key_height
            y_svg = self.key_height - y
            polyline_points += [x, y_svg]
        self.elements.append(
            svg.Polyline(
                points=polyline_points,
                stroke=config.BLUE.css_hex,
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
            y = self.key_height - i / self.duration * self.piano.height
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
