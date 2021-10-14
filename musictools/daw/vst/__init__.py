import abc

import numpy as np


class ADSR:
    def __init__(
        self,
        attack: float = 0.,
        decay: float = 1e-3,
        sustain: float = 1.,
        release: float = 1e-3,
    ):
        # ranges like in Ableton Live Operator, Wavetable
        if not (0. <= attack <= 20.): raise ValueError('wrong attack value')
        if not (0. < decay <= 20.): raise ValueError('wrong decay value')
        if not (0. <= sustain <= 1.): raise ValueError('wrong sustain value')
        if not (0. < release <= 20.): raise ValueError('wrong release value')

        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release


class VST(abc.ABC):
    def __init__(self, adsr=ADSR()):
        self.adsr = adsr

    @abc.abstractmethod
    def __call__(self, *args, **kwargs): ...


class Sine(VST):
    def __init__(self, adsr=ADSR()):
        super().__init__(adsr)

    def __call__(self, t, f, a=1., p=0.):
        return a * np.sin(2 * np.pi * f * t + p)
