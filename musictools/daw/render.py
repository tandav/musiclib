import numpy as np
from .. import config


def single(stream, notes, song_samples):
    notes, song_samples = parse_midi()

    print(notes)
    print(song_samples)

    master = np.zeros(song_samples, dtype='float32')
    for note, events in notes.items():
        for (note_on_sample, note_off_sample), (note_on_seconds, note_off_seconds) in events:
            t = np.linspace(note_on_seconds, note_off_seconds, note_off_sample - note_on_sample, endpoint=False)
            master[note_on_sample: note_off_sample] += sine(t, a=0.3, f=(440 / 32) * (2 ** ((note - 9) / 12)))
            print(note, note_on_sample, note_off_sample, note_on_seconds, note_off_seconds)
    print(master)
    assert np.all(np.abs(master) < 1)
    print(master.max())
    stream.write(master.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()


def chunked(stream, notes, song_samples):
    print(notes)
    print(song_samples)

    n = 0
    t = 0.

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
        stream.write(master.tobytes())
