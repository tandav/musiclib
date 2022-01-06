from enum import Enum
from enum import auto

import numpy as np

from musictool import config
from musictool.daw.vst.base import VST
from musictool.note import SpecificNote


class State(Enum):
    TODO = auto()
    PLAYING = auto()
    RELEASE = auto()
    DONE = auto()


class NoteSound:
    def __init__(
        self,
        absolute_i: int,
        vst: VST,
        sample_on: int, sample_off: int,
        second_on: float | None = None, second_off: float | None = None,
        frame_on: int | None = None, frame_off: int | None = None,
        px_on: int | None = None, px_off: int | None = None,
        color=None,
        trackname: str | None = None,
        # context_chord_root = None,
        # frac_on: float, frac_off: float,
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
        self.sample_on, self.sample_off = sample_on, sample_off
        self.second_on, self.second_off = second_on, second_off

        self.px_on, self.px_off = px_on, px_off

        self.color = color
        self.trackname = trackname
        self.smooth_rendering = True
        # self.frac_on = frac_on
        # self.frac_off = frac_off

        self.frame_on, self.frame_off = frame_on, frame_off

        self.ns = sample_off - sample_on

        self.ns_release = int(vst.adsr(self.note).release * config.sample_rate)
        self.stop_release = sample_off + self.ns_release  # actual sample when note is off (including release)

        self.ns_attack = min(int(vst.adsr(self.note).attack * config.sample_rate), self.ns)
        self.ns_decay_original = max(int(vst.adsr(self.note).decay * config.sample_rate), 1)  # prevent from equal to zero
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
        # if decay is longer than note then actual sustain is higher than vst.adsr(self.note).sustain (do the math)
        se = max((vst.adsr(self.note).sustain - 1) * (self.ns - self.ns_attack) / self.ns_decay_original + 1, vst.adsr(self.note).sustain)  # sustain extra
        self.decay_envelope = np.linspace(1, se, self.ns_decay, endpoint=False, dtype='float32')
        self.release_envelope = np.linspace(se, 0, self.ns_release, endpoint=False, dtype='float32')

        self.key = self.note, self.sample_on, self.stop_release
        self.vst = vst
        self.reset()

    def render(self, chunk, samples):
        self.state = State.PLAYING
        # if samples is None:
        #     samples = np.arange(len(chunk))
        mask = (self.sample_on <= samples) & (samples < self.stop_release)
        ns_to_render = np.count_nonzero(mask)

        mask_attack = (self.sample_on <= samples) & (samples < self.stop_attack)
        mask_decay = (self.stop_attack <= samples) & (samples < self.stop_decay)
        mask_sustain = (self.stop_decay <= samples) & (samples < self.sample_off)
        mask_release = (self.sample_off <= samples) & (samples < self.stop_release)

        wave = self.vst(self.ns_rendered, ns_to_render, self.note)

        # more readable ??
        out = np.zeros_like(chunk)
        out[mask] = wave
        out[mask_attack] *= self.attack_envelope[(samples[0] <= self.range_attack) & (self.range_attack <= samples[-1])]
        out[mask_decay] *= self.decay_envelope[(samples[0] <= self.range_decay) & (self.range_decay <= samples[-1])]
        out[mask_sustain] *= self.vst.adsr(self.note).sustain
        out[mask_release] *= self.release_envelope[(samples[0] <= self.range_release) & (self.range_release <= samples[-1])]
        chunk += out

        # same as above but kinda less readable (because of double masking)
        # wave[mask_attack[mask]] *= self.attack_envelope[(samples[0] <= self.range_attack) & (self.range_attack <= samples[-1])]
        # wave[mask_decay[mask]] *= self.decay_envelope[(samples[0] <= self.range_decay) & (self.range_decay <= samples[-1])]
        # wave[mask_sustain[mask]] *= self.vst.adsr(self.note).sustain
        # wave[mask_release[mask]] *= self.release_envelope[(samples[0] <= self.range_release) & (self.range_release <= samples[-1])]
        # chunk[mask] += wave

        self.ns_rendered += ns_to_render

        if self.sample_off <= samples[-1]:
            self.state = State.RELEASE
            if self.stop_release <= samples[-1]:
                self.state = State.DONE

        # if samples is None or self.stop_release + self.ns_release <= samples[-1]:
        #     self.state = State.DONE

    def reset(self):
        self.ns_rendered = 0
        self.px_rendered = 0
        self.state = State.TODO

    def __hash__(self): return hash(self.key)
    def __eq__(self, other): return self.key == other.key
