import mido
import numpy as np
import pyaudio

from . import config


def sine(t, f, a=1., p=0.):
    return a * np.sin(2 * np.pi * f * t + p)


p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=config.sample_rate, output=True)


class Note:
    def __init__(
        self,
        midi_note: int,
        sample_on: int,
        second_on: float,
        sample_off: int,
        second_off: float,
    ):
        self.midi_note = midi_note
        self.sample_on = sample_on
        self.second_on = second_on
        self.sample_off = sample_off
        self.second_off = second_off
        self.samples_rendered = 0

    def render(self, n_samples):
        f = (440 / 32) * (2 ** ((self.midi_note - 9) / 12))
        t0 = self.samples_rendered / config.sample_rate
        t1 = t0 + n_samples / config.sample_rate
        self.samples_rendered += n_samples
        wave = sine(np.linspace(t0, t1, n_samples, endpoint=False), f, a=0.3)
        return wave

    def __hash__(self):
        return hash((self.midi_note, self.sample_on, self.sample_off))


def parse_midi():
    ticks, seconds, samples = 0, 0., 0
    m = mido.MidiFile(config.midi_file)
    print(m.ticks_per_beat)
    notes = []
    note_buffer = dict()

    for message in m.tracks[0]:
        ticks += message.time
        d_seconds = mido.tick2second(message.time, m.ticks_per_beat, mido.bpm2tempo(config.beats_per_minute))
        seconds += d_seconds
        samples += int(config.sample_rate * d_seconds)
        print(message, ticks, seconds, samples)

        if message.type == 'note_on':
            note_buffer[message.note] = samples, seconds
        elif message.type == 'note_off':
            notes.append(Note(message.note, *note_buffer.pop(message.note), samples, seconds))
    return notes, samples


def main() -> int:
    notes, song_samples = parse_midi()

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

    stream.stop_stream()
    stream.close()
    p.terminate()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
