import numpy as np

from musictool.daw.vst.base import VST
from musictool.note import SpecificNote


class Sine(VST):
    def _call(self, ns_rendered: int, ns_to_render: int, note: SpecificNote, p=0.):
        t = self.samples_to_t(ns_rendered, ns_to_render)
        f = self.note_to_freq(note)
        return self.amplitude * np.sin(2 * np.pi * f * t + p)


class Sine8(VST):
    def _call(self, ns_rendered: int, ns_to_render: int, note: SpecificNote, p=0.):
        t = self.samples_to_t(ns_rendered, ns_to_render)
        f = self.note_to_freq(note)

        return self.amplitude * (
            1.0 * np.sin(2 * np.pi * f * 1 * t + p) +
            0.9 * np.sin(2 * np.pi * f * 2 * t + p) +
            0.8 * np.sin(2 * np.pi * f * 3 * t + p) +
            0.7 * np.sin(2 * np.pi * f * 4 * t + p) +
            0.6 * np.sin(2 * np.pi * f * 5 * t + p) +
            0.5 * np.sin(2 * np.pi * f * 6 * t + p) +
            0.4 * np.sin(2 * np.pi * f * 7 * t + p) +
            0.3 * np.sin(2 * np.pi * f * 8 * t + p)
        )
