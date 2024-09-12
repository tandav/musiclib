import mido
import pytest

from musiclib.midi import parse
from musiclib.note import SpecificNote
from musiclib.noteset import SpecificNoteSet
from musiclib.rhythm import Rhythm


def is_midi_equal(a: mido.MidiFile, b: mido.MidiFile) -> bool:
    return a.type == b.type and a.ticks_per_beat == b.ticks_per_beat and a.tracks == b.tracks  # type: ignore[no-any-return]


@pytest.mark.parametrize(
    ('type_', 'message', 'expected'), [
        ('on', mido.Message('note_on', note=60, velocity=1), True),
        ('on', mido.Message('note_on', note=60, velocity=0), False),
        ('on', mido.Message('note_off', note=60, velocity=1), False),
    ],
)
def test_is_note(type_, message, expected):
    assert parse.is_note(type_, message) == expected


def test_parse(mido_midifile, midi):
    assert parse.parse_midi(mido_midifile) == midi


def test_midiobj_to_midifile(midi, mido_midifile):
    check = parse.midiobj_to_midifile(midi)
    assert is_midi_equal(check, mido_midifile)


def test_abs_messages(midi):
    assert parse.abs_messages(midi) == [
        mido.Message('note_on', channel=0, note=60, velocity=100, time=0),
        mido.Message('note_off', channel=0, note=60, velocity=100, time=24),
        mido.Message('pitchwheel', channel=0, pitch=0, time=93),
        mido.Message('note_on', channel=0, note=64, velocity=100, time=96),
        mido.Message('note_on', channel=0, note=67, velocity=100, time=192),
        mido.Message('pitchwheel', channel=0, pitch=8191, time=197),
        mido.Message('note_off', channel=0, note=64, velocity=100, time=202),
        mido.Message('note_off', channel=0, note=67, velocity=100, time=216),
        mido.Message('pitchwheel', channel=0, pitch=0, time=216),
    ]


def test_specific_note_set_to_midi():
    sns = SpecificNoteSet(frozenset({SpecificNote.from_str('C1'), SpecificNote.from_str('E1'), SpecificNote.from_str('G1')}))
    midi = parse.specific_note_set_to_midi(sns)
    assert is_midi_equal(
        midi, mido.MidiFile(
            type=0, ticks_per_beat=96, tracks=[
                mido.MidiTrack([
                    mido.Message('note_on', channel=0, note=24, velocity=100, time=0),
                    mido.Message('note_on', channel=0, note=28, velocity=100, time=0),
                    mido.Message('note_on', channel=0, note=31, velocity=100, time=0),
                    mido.Message('note_off', channel=0, note=24, velocity=100, time=384),
                    mido.Message('note_off', channel=0, note=28, velocity=100, time=0),
                    mido.Message('note_off', channel=0, note=31, velocity=100, time=0),
                ]),
            ],
        ),
    )


def test_rhythm_to_midi():
    rhythm = Rhythm((1, 0, 1, 1))
    midi = parse.rhythm_to_midi(rhythm, note_=SpecificNote('C', 1))
    expected = mido.MidiFile(
        type=0,
        ticks_per_beat=96,
        tracks=[
            mido.MidiTrack([
                mido.Message('note_on', channel=0, note=24, velocity=100, time=0),
                mido.Message('note_off', channel=0, note=24, velocity=100, time=24),
                mido.Message('note_on', channel=0, note=24, velocity=100, time=24),
                mido.Message('note_off', channel=0, note=24, velocity=100, time=24),
                mido.Message('note_on', channel=0, note=24, velocity=100, time=0),
                mido.Message('note_off', channel=0, note=24, velocity=100, time=24),
            ]),
        ],
    )
    assert is_midi_equal(midi, expected)


def test_dict(mido_midifile):
    assert str(parse.from_dict(parse.to_dict(mido_midifile))) == str(mido_midifile)
