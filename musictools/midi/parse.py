import mido
import numpy as np

from .. import config
from ..daw import vst
from ..note import SpecificNote


class PlayedNote:
    def __init__(
        self,
        absolute_i: int,
        sample_on: int,
        second_on: float,
        sample_off: int,
        second_off: float,
        vst=None,
    ):
        self.note = SpecificNote.from_absolute_i(absolute_i)
        self.sample_on = sample_on
        self.second_on = second_on
        self.sample_off = sample_off
        self.second_off = second_off
        self.samples_rendered = 0
        self.vst = vst

    def render(self, n_samples=None):
        if n_samples is None:
            n_samples = self.sample_off - self.sample_on  # render all samples
        f = (440 / 32) * (2 ** ((self.note.absolute_i - 9) / 12))
        t0 = self.samples_rendered / config.sample_rate
        t1 = t0 + n_samples / config.sample_rate
        self.samples_rendered += n_samples
        wave = self.vst(np.linspace(t0, t1, n_samples, endpoint=False), f, a=0.3)
        return wave

    def __hash__(self):
        return hash((self.note, self.sample_on, self.sample_off))


def parse_midi(midi_file):
    ticks, seconds, samples = 0, 0., 0
    m = mido.MidiFile(midi_file)
    print(m.ticks_per_beat)
    notes = []
    note_buffer = dict()

    for message in m.tracks[0]:
        ticks += message.time
        d_seconds = mido.tick2second(message.time, m.ticks_per_beat, mido.bpm2tempo(config.beats_per_minute))
        seconds += d_seconds
        samples += int(config.sample_rate * d_seconds)
        print(message, ticks, seconds, samples)

        if message.type == 'note_on':
            note_buffer[message.note] = samples, seconds
        elif message.type == 'note_off':
            notes.append(PlayedNote(message.note, *note_buffer.pop(message.note), samples, seconds, vst=vst.sine))
    return notes, samples
