import mido

from .. import config
from ..daw import vst
from ..note import PlayedNote


def parse_midi(midi_file):
    ticks, seconds, samples = 0, 0., 0
    m = mido.MidiFile(midi_file)
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
