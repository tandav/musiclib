import abc
from typing import Optional

import numpy as np

from musictools import config
from musictools.daw.midi.parse import ParsedMidi
from musictools.daw.midi.parse import State


class Stream(abc.ABC):
    def __init__(self):
        self.master = np.zeros(config.chunk_size, dtype='float32')
        self.track: Optional[ParsedMidi] = None

    def render_single(self, track: ParsedMidi):
        self.track = track
        master = np.zeros(track.n_samples, dtype='float32')
        for note in track.notes:
            note.render(master)
        assert np.all(np.abs(master) <= 1)
        self.write(master)
        track.reset()

    def render_chunked(self, track: ParsedMidi):
        self.track = track
        notes = set(track.notes)
        n = 0
        playing_notes = set()
        self.master[:] = 0
        while n < track.n_samples:
            self.n = n
            chunk_size = min(config.chunk_size, track.n_samples - n)
            samples = np.arange(n, n + chunk_size)
            self.master[:chunk_size] = 0.
            playing_notes |= set(note for note in notes if n <= note.sample_on < n + config.chunk_size)
            stopped_notes = set()
            for note in playing_notes:
                note.render(self.master[:chunk_size], samples)

                if note.state == State.DONE:
                    stopped_notes.add(note)

            playing_notes -= stopped_notes
            notes -= stopped_notes
            # assert np.all(np.abs(self.master[:chunk_size]) <= 1)
            self.write(self.master[:chunk_size])
            n += chunk_size
        track.reset()

    @abc.abstractmethod
    def write(self, data: np.ndarray):
        """data.dtype must be float32"""
        ...
