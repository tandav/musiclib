import mido
import pytest
from musiclib.midi import parse
from musiclib.note import SpecificNote
from musiclib.rhythm import Rhythm


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
    assert check.type == mido_midifile.type
    assert check.ticks_per_beat == mido_midifile.ticks_per_beat
    assert check.tracks == mido_midifile.tracks


def test_index_abs_messages(midi):
    assert parse.index_abs_messages(midi) == [
        parse.IndexedMessage(message=mido.Message('note_on', channel=0, note=60, velocity=100, time=0), index=0),
        parse.IndexedMessage(message=mido.Message('note_off', channel=0, note=60, velocity=100, time=24), index=0),
        parse.IndexedMessage(message=mido.Message('pitchwheel', channel=0, pitch=0, time=93), index=0),
        parse.IndexedMessage(message=mido.Message('note_on', channel=0, note=64, velocity=100, time=96), index=1),
        parse.IndexedMessage(message=mido.Message('note_on', channel=0, note=67, velocity=100, time=192), index=2),
        parse.IndexedMessage(message=mido.Message('pitchwheel', channel=0, pitch=8191, time=197), index=1),
        parse.IndexedMessage(message=mido.Message('note_off', channel=0, note=64, velocity=100, time=202), index=1),
        parse.IndexedMessage(message=mido.Message('pitchwheel', channel=0, pitch=0, time=216), index=2),
        parse.IndexedMessage(message=mido.Message('note_off', channel=0, note=67, velocity=100, time=216), index=2),
    ]


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
    assert midi.type == expected.type
    assert midi.ticks_per_beat == expected.ticks_per_beat
    assert midi.tracks == expected.tracks
