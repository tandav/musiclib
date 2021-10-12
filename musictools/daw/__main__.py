import mido
import numpy as np
# import pyaudio
import io
from scipy.io import wavefile

from .. import config
from ..note import PlayedNote
from . import render
from . import vst


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
            notes.append(PlayedNote(message.note, *note_buffer.pop(message.note), samples, seconds, vst=vst.sine))
    return notes, samples


def main() -> int:
    # p = pyaudio.PyAudio()
    # stream = p.open(format=pyaudio.paFloat32, channels=1, rate=config.sample_rate, output=True)

    stream = io.BytesIO()

    notes, song_samples = parse_midi()
    render.chunked(stream, notes, song_samples)

    # stream.stop_stream()
    # stream.close()
    # p.terminate()
    print(stream.getvalue()[:10])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
