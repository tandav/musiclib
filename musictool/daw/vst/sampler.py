from collections.abc import Iterable
from pathlib import Path

import numpy as np

from musictool import config
from musictool.daw.vst.adsr import ADSR
from musictool.daw.vst.base import VST
from musictool.note import SpecificNote
from musictool.util import wavfile  # from scipy.io import wavfile


class Sampler(VST):
    DEFAULT_NOTE_TO_SAMPLE_PATH = (
        (SpecificNote('C', 3), config.kick),
        (SpecificNote('e', 3), config.clap),
        (SpecificNote('b', 3), config.hat),
        (SpecificNote('f', 3), config.hat),
    )

    DEFAULT_ADSR = ADSR()

    DEFAULT_NOTE_TO_ADSR = {
        SpecificNote('C', 3): ADSR(attack=0.001, decay=0.1, sustain=1, release=0.6),
        SpecificNote('e', 3): ADSR(attack=0.001, decay=0.2, sustain=0, release=0.1),
        SpecificNote('b', 3): ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1),
        SpecificNote('f', 3): ADSR(attack=0.001, decay=0.02, sustain=0, release=0.1),
    }

    DEFAULT_AMPLITUDE = 0.1
    DEFAULT_NOTE_TO_AMPLITUDE = {
        SpecificNote('C', 3): 0.15,
        SpecificNote('e', 3): 0.05,
        SpecificNote('b', 3): 0.02,
        SpecificNote('f', 3): 0.007,
    }

    def __init__(
        self,
        note_to_sample_path: Iterable[tuple[SpecificNote, str | Path]] = DEFAULT_NOTE_TO_SAMPLE_PATH,
        adsr: ADSR | dict[SpecificNote, ADSR] = DEFAULT_NOTE_TO_ADSR
    ):
        super().__init__(adsr)
        self.note_to_sample = dict()
        for note, sample_path in note_to_sample_path:
            self.note_to_sample[note] = self.load_sample(sample_path)
        self.note_to_amplitude = Sampler.DEFAULT_NOTE_TO_AMPLITUDE

        self.note_mute = {
            SpecificNote('C', 3): False,
            SpecificNote('e', 3): False,
            SpecificNote('b', 3): False,
            SpecificNote('f', 3): False,
        }

    def load_sample(self, sample_path: str | Path):
        sample_rate, sample = wavfile.read(sample_path)
        if sample.dtype != 'float32':
            raise ValueError(f'Sample {sample_path} should be in float32 format')
        if sample_rate != config.sample_rate:
            raise NotImplementedError(
                f'resampling is not supported yet, please save sample {sample_path} with sample rate {config.sample_rate}')
        return sample

    def _call(self, ns_rendered: int, ns_to_render: int, note: SpecificNote):
        out = np.zeros(ns_to_render, dtype='float32')  # handle cases when samples ends earlier than note_off, render zeros till note_off (and maybe release? idk lol)
        sample = self.note_to_sample.get(note)
        if sample is not None:
            sample = self.note_to_amplitude.get(note, self.amplitude) * sample[ns_rendered: ns_rendered + ns_to_render]
            out[:len(sample)] = sample

        if self.note_mute[note]:
            return out * 0
        return out

    def adsr(self, note):
        return self._adsr.get(note, Sampler.DEFAULT_ADSR)
