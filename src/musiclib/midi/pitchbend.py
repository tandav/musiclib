import collections
import dataclasses

import mido
import numpy as np

from musiclib.midi.parse import IndexedMessage
from musiclib.midi.parse import Midi
from musiclib.midi.parse import MidiNote
from musiclib.midi.parse import MidiPitch
from musiclib.tempo import Tempo
from musiclib.util.etc import increment_duplicates


@dataclasses.dataclass
class PitchPattern:
    time_bars: list[int]
    pitch_st: list[int]


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
    return PitchPattern(time_bars=new_t, pitch_st=new_p)


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


def midiobj_to_midifile(midi: Midi) -> mido.MidiFile:
    abs_messages = index_abs_messages(midi)
    t = 0
    messages = []
    for im in abs_messages:
        m = im.message.copy()
        m.time = im.message.time - t
        messages.append(m)
        t = im.message.time
    track = mido.MidiTrack(messages)
    return mido.MidiFile(type=0, tracks=[track], ticks_per_beat=midi.ticks_per_beat)


def index_abs_messages(midi: Midi) -> list[IndexedMessage]:
    """this are messages with absolute time, note real midi messages"""
    abs_messages = []
    for i, note in enumerate(midi.notes):
        abs_messages.append(IndexedMessage(message=mido.Message(type='note_on', time=note.on, note=note.note.i, velocity=100), index=i))
        abs_messages.append(IndexedMessage(message=mido.Message(type='note_off', time=note.off, note=note.note.i, velocity=100), index=i))
    for i, pitch in enumerate(midi.pitchbend):
        abs_messages.append(IndexedMessage(message=mido.Message(type='pitchwheel', time=pitch.time, pitch=pitch.pitch), index=i))
    # Sort by time. If time is equal sort using type priority in following order: note_on, pitchwheel, note_off
    abs_messages.sort(key=lambda m: (m.message.time, {'note_on': 0, 'pitchwheel': 1, 'note_off': 2}[m.message.type]))
    return abs_messages


def make_notes_pitchbends(midi: Midi) -> dict[MidiNote, list[MidiPitch]]:
    T, P = zip(*[(e.time, e.pitch) for e in midi.pitchbend], strict=True)  # noqa: N806
    interp_t = []
    for note in midi.notes:
        interp_t += [note.on, note.off]
    interp_p = np.interp(interp_t, T, P, left=0).astype(int).tolist()  # https://docs.scipy.org/doc/scipy/tutorial/interpolate/1D.html#piecewise-linear-interpolation
    interp_pitches = sorted(midi.pitchbend + [MidiPitch(time=t, pitch=p) for t, p in zip(interp_t, interp_p, strict=True)], key=lambda p: p.time)
    midi_tmp = Midi(notes=midi.notes, pitchbend=interp_pitches)
    notes_pitchbends = collections.defaultdict(list)
    playing_notes = set()
    for im in index_abs_messages(midi_tmp):
        if im.message.type in {'note_on', 'note_off'}:
            note = midi.notes[im.index]
            if im.message.type == 'note_on':
                playing_notes.add(note)
            elif im.message.type == 'note_off':
                playing_notes.remove(note)
        elif im.message.type == 'pitchwheel':
            for note in playing_notes:
                notes_pitchbends[note].append(midi_tmp.pitchbend[im.index])
    return dict(notes_pitchbends)
