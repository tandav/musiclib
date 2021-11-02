import abc
from typing import Union

import numpy as np

from musictools import config
from musictools.daw.vst.adsr import ADSR
from musictools.note import SpecificNote


class VST(abc.ABC):
    def __init__(self, adsr: Union[ADSR, dict[SpecificNote, ADSR]] = ADSR(), amplitude=0.1):
        self._adsr = adsr
        self.amplitude = amplitude
        self.mute = False

    def adsr(self, note): return self._adsr

    def note_to_freq(self, note: SpecificNote, tunning: float = config.tuning):
        return (tunning / 32) * (2 ** ((note.absolute_i - 9) / 12))

    def samples_to_t(self, ns_rendered: int, ns_to_render: int):
        t0 = ns_rendered / config.sample_rate
        t1 = t0 + ns_to_render / config.sample_rate
        return np.linspace(t0, t1, ns_to_render, endpoint=False)

    def __call__(self, *args, **kwargs):
        out = self._call(*args, **kwargs)
        if self.mute:
            return out * 0
        return out
        # out *= # final volume

    @abc.abstractmethod
    def _call(self, *args, **kwargs): ...
