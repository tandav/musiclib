import abc
from contextlib import AbstractContextManager

import numpy as np

from musictool import config
from musictool.daw.midi.notesound import State
from musictool.daw.midi.parse.sounds import ParsedMidi
from musictool.util.signal import normalize as normalize_


class Stream(AbstractContextManager):
    def __init__(self):
        self.master = np.zeros(config.chunk_size, dtype='float32')
        self.track: ParsedMidi | None = None

    def render_single(self, track: ParsedMidi, normalize=False):
        # self.track = track
        master = np.zeros(track.n_samples, dtype='float32')
        for note in track.notes:
            # note.render(master)
            note.render(master, samples=np.arange(len(master)))
        assert np.all(np.abs(master) <= 1)
        if normalize:
            self.write(normalize_(master))
        else:
            self.write(master)
        track.reset()

    def render_chunked(self, track: ParsedMidi, normalize=False):
        # self.track = track
        notes = set(track.notes)
        n = 0
        # playing_notes = set()
        self.master[:] = 0
        while n < track.n_samples:
            self.n = n
            chunk_size = min(config.chunk_size, track.n_samples - n)
            self.master[:chunk_size] = 0.
            track.playing_notes |= set(note for note in notes if n <= note.sample_on < n + config.chunk_size)
            track.done_notes = set()
            for note in track.playing_notes | track.releasing_notes:
                note.render(self.master[:chunk_size], samples=np.arange(n, n + chunk_size))

                if note.state == State.RELEASE or note.state == State.DONE:
                    if note.state == State.RELEASE:
                        track.releasing_notes.add(note)

                    if note.state == State.DONE:
                        track.done_notes.add(note)

                    # if note.px_rendered < note.n_px:
                    #     track.drawn_not_complete_notes.add(note)

            track.playing_notes -= track.done_notes | track.releasing_notes
            track.releasing_notes -= track.done_notes
            notes -= track.done_notes
            assert np.all(np.abs(self.master[:chunk_size]) <= 1)
            if normalize:
                self.write(normalize_(self.master[:chunk_size]))
            else:
                self.write(self.master[:chunk_size])
            n += chunk_size
        track.reset()
        self.px_written = 0  # todo: move somewhere?

    @abc.abstractmethod
    def write(self, data: np.ndarray):
        """data.dtype must be float32"""
        ...
