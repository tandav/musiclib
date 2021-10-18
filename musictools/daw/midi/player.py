import os
from typing import Optional

if (midi_device := os.environ.get('MIDI_DEVICE')):
    import mido


    port = mido.open_output(midi_device)

    def send_message(*args, **kwargs):
        note = kwargs.pop('note') + 24  # to match ableton octaves
        port.send(mido.Message(*args, note=note, **kwargs))

    def rhythm_to_midi(rhythm, path, chord=None, progression=None, return_midi=False) -> Optional[mido.MidiFile]:
        mid = mido.MidiFile(type=0, ticks_per_beat=96)
        ticks_per_note = mid.ticks_per_beat * rhythm.beats_per_bar // rhythm.bar_notes
        track = mido.MidiTrack()
        track.append(mido.MetaMessage(type='track_name', name='test_name'))
        track.append(mido.MetaMessage(type='time_signature', numerator=4, denominator=4, clocks_per_click=36))
        t = 0

        def append_bar(chord):
            nonlocal t
            for is_play in rhythm.notes:
                if is_play:
                    notes = [48] if chord is None else [note.absolute_i for note in chord.notes]
                    for i, note in enumerate(notes):
                        track.append(mido.Message('note_on', note=note, velocity=100, time=t if i == 0 else 0))
                    for i, note in enumerate(notes):
                        track.append(mido.Message('note_off', note=note, velocity=100, time=ticks_per_note if i == 0 else 0))
                    t = 0
                else:
                    t += ticks_per_note

        if progression is None:
            append_bar(chord)
        else:
            for chord in progression:
                append_bar(chord)

        mid.tracks.append(track)
        if return_midi:
            return mid
        mid.save(path)
else:
    def send_message(*args, **kwargs):
        print(*args, ', '.join(f'{k}={v!r}' for k, v in kwargs.items()))
