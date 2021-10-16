import numpy as np

from .. import config
from .midi.parse import State


def single(stream, track):
    # n_samples = track.n_samples + config.chunk_size - track.n_samples % config.chunk_size
    master = np.zeros(track.n_samples, dtype='float32')
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
        chunk_size = min(config.chunk_size, track.n_samples - n)
        samples = np.arange(n, n + chunk_size)
        master[:chunk_size] = 0.
        playing_notes |= set(note for note in notes if n <= note.sample_on < n + config.chunk_size)
        stopped_notes = set()
        for note in playing_notes:
            note.render(master[:chunk_size], samples)

            if note.state == State.DONE:
                stopped_notes.add(note)

        playing_notes -= stopped_notes
        notes -= stopped_notes
        assert np.all(np.abs(master[:chunk_size]) <= 1)
        # stream.write(master[:chunk_size].tobytes())
        stream.write(master[:chunk_size])
        n += chunk_size
    track.reset()
