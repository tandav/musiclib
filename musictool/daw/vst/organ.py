import numpy as np

from musictool.daw.vst.base import VST
from musictool.note import SpecificNote


class Organ(VST):
    def _call(self, ns_rendered: int, ns_to_render: int, note: SpecificNote, p=0.):
        t = self.samples_to_t(ns_rendered, ns_to_render)
        f0 = self.note_to_freq(note)
        f1 = self.note_to_freq(note + 7)
        f2 = self.note_to_freq(note + 19)

        return (
            self.amplitude * np.sin(2 * np.pi * f0 * t + p) +
            self.amplitude * np.sin(2 * np.pi * f1 * t + p) +
            self.amplitude * np.sin(2 * np.pi * f2 * t + p)
        )
