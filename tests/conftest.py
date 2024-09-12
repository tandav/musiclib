import mido
import pytest

from musiclib.midi.parse import Midi
from musiclib.midi.parse import MidiNote
from musiclib.midi.parse import MidiPitch
from musiclib.note import SpecificNote


@pytest.fixture
def mido_midifile():
    return mido.MidiFile(
        type=0, ticks_per_beat=96, tracks=[
            mido.MidiTrack([
                mido.Message('note_on', channel=0, note=60, velocity=100, time=0),
                mido.Message('note_off', channel=0, note=60, velocity=100, time=24),
                mido.Message('pitchwheel', channel=0, pitch=0, time=69),
                mido.Message('note_on', channel=0, note=64, velocity=100, time=3),
                mido.Message('note_on', channel=0, note=67, velocity=100, time=96),
                mido.Message('pitchwheel', channel=0, pitch=8191, time=5),
                mido.Message('note_off', channel=0, note=64, velocity=100, time=5),
                mido.Message('note_off', channel=0, note=67, velocity=100, time=14),
                mido.Message('pitchwheel', channel=0, pitch=0, time=0),
            ]),
        ],
    )


@pytest.fixture
def midi():
    return Midi(
        notes=[
            MidiNote(note=SpecificNote('C', 4), on=0, off=24),
            MidiNote(note=SpecificNote('E', 4), on=96, off=202),
            MidiNote(note=SpecificNote('G', 4), on=192, off=216),
        ],
        pitchbend=[
            MidiPitch(time=93, pitch=0),
            MidiPitch(time=197, pitch=8191),
            MidiPitch(time=216, pitch=0),
        ],
        ticks_per_beat=96,
    )
