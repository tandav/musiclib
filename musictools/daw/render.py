import numpy as np

from .. import config


def single(stream, track):
    n_samples = track.n_samples + config.chunk_size - track.n_samples % config.chunk_size
    master = np.zeros(n_samples, dtype='float32')
    for note in track.notes:
        master[note.sample_on: note.sample_off] += note.render()
    config.log['single'] = master
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
        # master[:] = 0.1 * np.random.random(len(master))

        playing_notes |= set(note for note in notes if n <= note.sample_on < n + config.chunk_size)
        stopped_notes = set()
        for note in playing_notes:
            mask = (note.sample_on <= samples) & (samples < note.sample_off)
            master[mask] += note.render(n_samples=np.count_nonzero(mask))
            if note.sample_off < n + config.chunk_size:
                stopped_notes.add(note)
        playing_notes -= stopped_notes
        notes -= stopped_notes
        n += config.chunk_size
        # config.log[config.n_run].append(master)
        config.log['chunked'].append(master.copy())
        stream.write(master.tobytes())
