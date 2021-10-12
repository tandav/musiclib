import numpy as np

from .. import config


def single(stream, notes, song_samples):
    div, mod = divmod(song_samples, config.chunk_size)
    song_samples += config.chunk_size - mod
    master = np.zeros(song_samples, dtype='float32')
    for note in notes:
        master[note.sample_on: note.sample_off] += note.render()
    b = master.tobytes()
    print(len(b))
    stream.write(b)


def chunked(stream, notes, song_samples):
    n = 0
    t = 0.
    bytes_written = 0
    playing_notes = set()
    master = np.zeros(config.chunk_size, dtype='float32')

    while n < song_samples:
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
        t += config.chunk_seconds
        n += config.chunk_size
        b = master.tobytes()
        stream.write(master.tobytes())
        bytes_written += len(b)
    print(bytes_written)
