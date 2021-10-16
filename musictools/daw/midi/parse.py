from enum import Enum
from enum import auto

import mido
import numpy as np

from ... import config
from ...note import SpecificNote
from .. import vst


class State(Enum):
    TODO = auto()
    IN_PROGRESS = auto()
    DONE = auto()


class NoteSound:
    def __init__(
        self,
        absolute_i: int,
        sample_on: int,
        sample_off: int,
        vst: vst.VST,
    ):
        """
        TODO:
            - maybe remove some variables (which can be expressed via other)
            - maybe add some logic for  not to use sustain envelope when self.stop_decay > self.sample_off
                - now it does automatically (empty masks)

        ns_ means number of samples
        stop_xxx means sample where xxx is no more playing
        """
        self.note = SpecificNote.from_absolute_i(absolute_i)
        self.sample_on = sample_on
        self.sample_off = sample_off
        self.ns = sample_off - sample_on

        self.ns_release = int(vst.adsr.release * config.sample_rate)
        self.stop_release = sample_off + self.ns_release  # actual sample when note is off (including release)

        self.ns_attack = min(int(vst.adsr.attack * config.sample_rate), self.ns)
        self.ns_decay_original = max(int(vst.adsr.decay * config.sample_rate), 1)  # prevent from equal to zero
        self.ns_decay = min(self.ns_decay_original, self.ns - self.ns_attack)
        self.ns_sustain = self.ns - self.ns_attack - self.ns_decay

        self.stop_attack = self.sample_on + self.ns_attack
        self.stop_decay = self.stop_attack + self.ns_decay
        # self.stop_sustain = self.sample_off  # do the math

        # todo: use difference, not ranges
        self.range_attack = np.arange(self.sample_on, self.stop_attack)
        self.range_decay = np.arange(self.stop_attack, self.stop_decay)
        self.range_sustain = np.arange(self.stop_decay, self.sample_off)
        self.range_release = np.arange(self.sample_off, self.stop_release)

        self.attack_envelope = np.linspace(0, 1, self.ns_attack, endpoint=False, dtype='float32')
        # if decay is longer than note then actual sustain is higher than vst.adsr.sustain (do the math)
        se = max((vst.adsr.sustain - 1) * (self.ns - self.ns_attack) / self.ns_decay_original + 1, vst.adsr.sustain)  # sustain extra
        self.decay_envelope = np.linspace(1, se, self.ns_decay, endpoint=False, dtype='float32')
        self.release_envelope = np.linspace(se, 0, self.ns_release, endpoint=False, dtype='float32')

        self.ns_rendered = 0
        self.vst = vst
        self.key = self.note, self.sample_on, self.stop_release
        self.state = State.TODO

    def render(self, chunk, samples=None):
        self.state = State.IN_PROGRESS
        if samples is None:
            samples = np.arange(len(chunk))
        mask = (self.sample_on <= samples) & (samples < self.stop_release)
        ns_to_render = np.count_nonzero(mask)

        mask_attack = (self.sample_on <= samples) & (samples < self.stop_attack)
        mask_decay = (self.stop_attack <= samples) & (samples < self.stop_decay)
        mask_sustain = (self.stop_decay <= samples) & (samples < self.sample_off)
        mask_release = (self.sample_off <= samples) & (samples < self.stop_release)

        wave = self.vst(self.ns_rendered, ns_to_render, self.note)

        wave[mask_attack[mask]] *= self.attack_envelope[(samples[0] <= self.range_attack) & (self.range_attack <= samples[-1])]
        wave[mask_decay[mask]] *= self.decay_envelope[(samples[0] <= self.range_decay) & (self.range_decay <= samples[-1])]
        wave[mask_sustain[mask]] *= self.vst.adsr.sustain
        wave[mask_release[mask]] *= self.release_envelope[(samples[0] <= self.range_release) & (self.range_release <= samples[-1])]
        chunk[mask] += wave
        self.ns_rendered += ns_to_render

        if samples is None or self.stop_release + self.ns_release <= samples[-1]:
            self.state = State.DONE

    def reset(self):
        self.ns_rendered = 0

    def __hash__(self): return hash(self.key)
    def __eq__(self, other): return self.key == other.key


class ParsedMidi:
    def __init__(self, notes, n_samples, numerator=4, vst=None):
        self.notes = notes
        self.n_samples = n_samples
        self.numerator = numerator
        self.vst = vst

    def reset(self):
        for note in self.notes:
            note.reset()

    @classmethod
    def from_file(cls, midi_file, vst):
        ticks, seconds, n_samples = 0, 0., 0
        m = mido.MidiFile(config.midi_folder + midi_file, type=1)
        notes = []
        note_buffer = dict()

        numerator = None

        for track in m.tracks:
            for message in track:
                if message.type == 'time_signature':
                    assert message.denominator == 4
                    numerator = message.numerator
                ticks += message.time
                d_seconds = mido.tick2second(message.time, m.ticks_per_beat, mido.bpm2tempo(config.beats_per_minute))
                seconds += d_seconds
                n_samples += int(config.sample_rate * d_seconds)
                print(message)
                if message.type == 'note_on':
                    note_buffer[message.note] = n_samples
                elif message.type == 'note_off':
                    notes.append(NoteSound(message.note, note_buffer.pop(message.note), n_samples, vst=vst))

        ticks_per_bar = numerator * m.ticks_per_beat
        div, mod = divmod(ticks, ticks_per_bar)
        if mod:
            ticks += ticks_per_bar - mod
        n_samples = int(config.sample_rate * mido.tick2second(ticks, m.ticks_per_beat, mido.bpm2tempo(config.beats_per_minute)))
        return cls(notes, n_samples, numerator)
