import bisect
import dataclasses
import itertools
import operator
from typing import no_type_check

import numpy as np

from musiclib.midi.parse import Midi
from musiclib.midi.parse import MidiNote
from musiclib.midi.parse import MidiPitch
from musiclib.tempo import Tempo
from musiclib.util.etc import increment_duplicates


@dataclasses.dataclass
class PitchPattern:
    time_bars: list[float]
    pitch_st: list[float]


def interpolate_pattern(pattern: PitchPattern, n_interp_points: int) -> PitchPattern:
    if n_interp_points <= len(pattern.time_bars):
        raise ValueError(f'n_interp_points should be > len(pattern.time_bars), got {n_interp_points=} and {len(pattern.time_bars)=}')
    original_points_list = list(zip(pattern.time_bars, pattern.pitch_st, strict=True))
    original_points_indices = {point: i for i, point in enumerate(original_points_list)}
    original_points = set(original_points_list)
    new_t = np.linspace(pattern.time_bars[0], pattern.time_bars[-1], num=n_interp_points).tolist()
    new_p = np.interp(new_t, pattern.time_bars, pattern.pitch_st).tolist()
    new_points = original_points.copy()
    for t, p in zip(new_t, new_p, strict=True):
        if len(new_points) >= n_interp_points:
            break
        if (t, p) in original_points:
            continue
        new_points.add((t, p))
    new_points_sorted = sorted(new_points, key=lambda point: (original_points_indices.get(point, -1), point))
    new_t, new_p = zip(*new_points_sorted, strict=True)
    return PitchPattern(time_bars=list(new_t), pitch_st=list(new_p))


def insert_pitch_pattern(
    midi: Midi,
    time_ticks: int,
    pattern: PitchPattern,
    *,
    pitchbend_semitones: int = 2,
    n_interp_points: int | None = None,
    increment_duplicates_: bool = True,
) -> Midi:
    if n_interp_points is not None:
        pattern = interpolate_pattern(pattern, n_interp_points)
    time_bars = Tempo(ticks=time_ticks, ticks_per_beat=midi.ticks_per_beat).bars
    pitchbend = [
        MidiPitch(
            time=int((time_bars + t) * midi.ticks_per_beat * 4),
            pitch=int(p / pitchbend_semitones * 8191),
        )
        for t, p in zip(pattern.time_bars, pattern.pitch_st, strict=True)
    ]
    pitchbend = sorted(midi.pitchbend + pitchbend, key=lambda p: p.time)
    if increment_duplicates_:
        pitchbend = [
            MidiPitch(time=time, pitch=pitch)
            for time, pitch in zip(
                increment_duplicates([p.time for p in pitchbend]),
                [p.pitch for p in pitchbend],
                strict=True,
            )
        ]
    return Midi(
        notes=midi.notes,
        pitchbend=pitchbend,
        ticks_per_beat=midi.ticks_per_beat,
    )


def make_notes_pitchbends(midi: Midi) -> dict[MidiNote, list[MidiPitch]]:
    T, P = zip(*[(e.time, e.pitch) for e in midi.pitchbend], strict=True)  # noqa: N806
    T_set = set(T)  # noqa: N806
    interp_t = []
    for note in midi.notes:
        for t in (note.on, note.off):
            if t in T_set:
                continue
            interp_t.append(t)
            T_set.add(t)
    interp_p = np.interp(interp_t, T, P, left=0).astype(int).tolist()  # https://docs.scipy.org/doc/scipy/tutorial/interpolate/1D.html#piecewise-linear-interpolation
    interp_pitches = sorted(midi.pitchbend + [MidiPitch(time=t, pitch=p) for t, p in zip(interp_t, interp_p, strict=True)])
    notes_pitchbends = {}
    for note in midi.notes:
        notes_pitchbends[note] = interp_pitches[
            bisect.bisect_left(interp_pitches, note.on, key=operator.attrgetter('time')):
            bisect.bisect_right(interp_pitches, note.off, key=operator.attrgetter('time'))
        ]
    return notes_pitchbends


@no_type_check
def add_pitchbend_from_overlapping_notes(midi: Midi, pitchbend_semitones: int = 2) -> Midi:
    notes_to_delete = set()
    pitchbend = []
    new_notes = []
    it = itertools.chain(midi.notes, [None])
    for a, b in itertools.pairwise(it):
        if b is None:
            new_notes.append(a)
            break
        if a in notes_to_delete:
            continue
        if a.off < b.on:
            new_notes.append(a)
            continue
        if b.note - a.note > pitchbend_semitones:
            raise ValueError(f'note leap {b.note - a.note} is larger than {pitchbend_semitones=}. Increase pitchbend_semitones')
        pitch = -int((b.note - a.note) / pitchbend_semitones * 8191)
        pitchbend.append(MidiPitch(time=a.on, pitch=pitch))
        pitchbend.append(MidiPitch(time=b.on, pitch=0))
        pitchbend.append(MidiPitch(time=b.off, pitch=0))
        new_notes.append(MidiNote(note=b.note, on=a.on, off=b.off))
        notes_to_delete.add(b)
    return Midi(notes=new_notes, pitchbend=pitchbend)
