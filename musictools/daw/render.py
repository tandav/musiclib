import numpy as np

from .. import config
from ..midi.parse import State


def single(stream, track):
    n_samples = track.n_samples + config.chunk_size - track.n_samples % config.chunk_size
    master = np.zeros(n_samples, dtype='float32')
    for note in track.notes:
        note.render(master)
    assert np.all(np.abs(master) <= 1)
    stream.write(master.tobytes())
    track.reset()


def chunked(stream, track):
    notes = set(track.notes)
    n = 0
    playing_notes = set()
    master = np.zeros(config.chunk_size, dtype='float32')

    while n < track.n_samples:
        samples = np.arange(n, n + config.chunk_size)
        master[:] = 0.
        playing_notes |= set(note for note in notes if n <= note.sample_on < n + config.chunk_size)
        stopped_notes = set()
        for note in playing_notes:
            note.render(master, samples)

            if note.state == State.DONE:
                stopped_notes.add(note)

        playing_notes -= stopped_notes
        notes -= stopped_notes
        n += config.chunk_size
        assert np.all(np.abs(master) <= 1)
        stream.write(master.tobytes())
    track.reset()
