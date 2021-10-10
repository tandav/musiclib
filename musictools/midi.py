import os

if (midi_device := os.environ.get('MIDI_DEVICE')):
    import mido
    from mido import Message
    from mido import MidiFile
    from mido import MidiTrack

    port = mido.open_output(midi_device)

    def send_message(*args, **kwargs):
        note = kwargs.pop('note') + 24  # to match ableton octaves
        port.send(mido.Message(*args, note=note, **kwargs))

    def rhythm_to_midi(rhythm, path, chord=None) -> None:
        mid = MidiFile(type=0)
        ticks_per_note = mid.ticks_per_beat * rhythm.beats_per_bar // rhythm.bar_notes
        track = MidiTrack()

        t = 0
        for is_play in rhythm.notes:
            if is_play:
                notes = [48] if chord is None else [note.absolute_i for note in chord.notes]
                for i, note in enumerate(notes):
                    track.append(Message('note_on', note=note, velocity=100, time=t if i == 0 else 0))
                for i, note in enumerate(notes):
                    track.append(Message('note_off', note=note, velocity=100, time=ticks_per_note if i == 0 else 0))
                t = 0
            else:
                t += ticks_per_note
        mid.tracks.append(track)
        mid.save(path)
else:
    def send_message(*args, **kwargs):
        print(*args, ', '.join(f'{k}={v!r}' for k, v in kwargs.items()))
