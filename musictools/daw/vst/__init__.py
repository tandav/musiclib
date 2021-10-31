import abc
from collections.abc import Iterable
from pathlib import Path
from typing import Union

import numpy as np

from musictools import config
from musictools.note import SpecificNote
# import musictools.util.wavfile as wavfile  # from scipy.io import wavfile
from musictools.util import wavfile  # from scipy.io import wavfile
from musictools.daw.vst.adsr import ADSR




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


class Sine(VST):
    def __call__(self, ns_rendered: int, ns_to_render: int, note: SpecificNote, p=0.):
        t = self.samples_to_t(ns_rendered, ns_to_render)
        f = self.note_to_freq(note)
        return self.amplitude * np.sin(2 * np.pi * f * t + p)


class Organ(VST):
    def __call__(self, ns_rendered: int, ns_to_render: int, note: SpecificNote, p=0.):
        t = self.samples_to_t(ns_rendered, ns_to_render)
        f0 = self.note_to_freq(note)
        f1 = self.note_to_freq(note + 7)
        f2 = self.note_to_freq(note + 19)

        return (
            self.amplitude * np.sin(2 * np.pi * f0 * t + p) +
            self.amplitude * np.sin(2 * np.pi * f1 * t + p) +
            self.amplitude * np.sin(2 * np.pi * f2 * t + p)
        )


class Sampler(VST):
    DEFAULT_NOTE_TO_SAMPLE_PATH = (
        (SpecificNote('C', 3), config.kick),
        (SpecificNote('e', 3), config.clap),
        (SpecificNote('b', 3), config.hat),
    )

    DEFAULT_ADSR = ADSR()

    DEFAULT_NOTE_TO_ADSR = {
        SpecificNote('C', 3): ADSR(attack=0.001, decay=0.1, sustain=1, release=0.2),
        SpecificNote('e', 3): ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1),
        SpecificNote('b', 3): ADSR(attack=0.001, decay=0.2, sustain=0, release=0.1),
    }

    def __init__(
        self,
        note_to_sample_path: Iterable[tuple[SpecificNote, Union[str, Path]]] = DEFAULT_NOTE_TO_SAMPLE_PATH,
        adsr: Union[ADSR, dict[SpecificNote, ADSR]] = DEFAULT_NOTE_TO_ADSR
    ):
        super().__init__(adsr)
        self.note_to_sample = dict()
        for note, sample_path in note_to_sample_path:
            self.note_to_sample[note] = self.load_sample(sample_path)

    def load_sample(self, sample_path: Union[str, Path]):
        sample_rate, sample = wavfile.read(sample_path)
        if sample.dtype != 'float32':
            raise ValueError(f'Sample {sample_path} should be in float32 format')
        if sample_rate != config.sample_rate:
            raise NotImplementedError(
                f'resampling is not supported yet, please save sample {sample_path} with sample rate {config.sample_rate}')
        return sample

    def __call__(self, ns_rendered: int, ns_to_render: int, note: SpecificNote):
        out = np.zeros(ns_to_render, dtype='float32')  # handle cases when samples ends earlier than note_off, render zeros till note_off (and maybe release? idk lol)
        sample = self.note_to_sample.get(note)
        if sample is not None:
            sample = self.amplitude * sample[ns_rendered: ns_rendered + ns_to_render]
            out[:len(sample)] = sample
        return out

    def adsr(self, note):
        return self._adsr.get(note, Sampler.DEFAULT_ADSR)
