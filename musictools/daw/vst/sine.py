import numpy as np

from musictools.daw.vst.base import VST
from musictools.note import SpecificNote


class Sine(VST):
    def __call__(self, ns_rendered: int, ns_to_render: int, note: SpecificNote, p=0.):
        t = self.samples_to_t(ns_rendered, ns_to_render)
        f = self.note_to_freq(note)
        return self.amplitude * np.sin(2 * np.pi * f * t + p)
