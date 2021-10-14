import abc

import numpy as np


class ADSR:
    def __init__(
        self,
        attack: float = 0.,
        decay: float = 0.,
        sustain: float = 0.,
        release: float = 0.,
    ):
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release


class ADSRLinear(ADSR): pass


class ADSRExponential(ADSR):
    """TODO: make  linear a special case of exponential (zero curvature)"""
    pass


class VST(abc.ABC):
    def __init__(
        self,
        adsr=ADSRLinear(),
    ):
        self.adsr = adsr

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        ...


class Sine(VST):
    def __init__(
        self,
        adsr=ADSRLinear(),
    ):
        super().__init__(adsr)

    def __call__(self, t, f, a=1., p=0.):
        return a * np.sin(2 * np.pi * f * t + p)
