from musiclib.midi.parse import Midi
from musiclib.midi.parse import MidiNote
from musiclib.midi.parse import MidiPitch
from musiclib.note import SpecificNote
from musiclib.svg.pianoroll import PianoRoll


def test_repr_svg():
    midi = Midi(
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
    PianoRoll(midi)._repr_svg_()
