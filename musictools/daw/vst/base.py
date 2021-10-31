from typing import Union
import abc
from musictools.daw.vst.adsr import ADSR
from musictools.note import SpecificNote
from musictools import config
import numpy as np


class VST(abc.ABC):
    def __init__(self, adsr: Union[ADSR, dict[SpecificNote, ADSR]] = ADSR(), amplitude=0.1):
        self._adsr = adsr
        self.amplitude = amplitude

    def adsr(self, note): return self._adsr

    def note_to_freq(self, note: SpecificNote):
        return (440 / 32) * (2 ** ((note.absolute_i - 9) / 12))

    def samples_to_t(self, ns_rendered: int, ns_to_render: int):
        t0 = ns_rendered / config.sample_rate
        t1 = t0 + ns_to_render / config.sample_rate
        return np.linspace(t0, t1, ns_to_render, endpoint=False)

    @abc.abstractmethod
    def __call__(self, *args, **kwargs): ...
