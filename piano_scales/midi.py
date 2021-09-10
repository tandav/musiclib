import os

if (midi_device := os.environ.get('MIDI_DEVICE')):
    import mido
    port = mido.open_output(midi_device)

    def send_message(*args, **kwargs):
        note = kwargs.pop('note') + 24  # to match ableton octaves
        port.send(mido.Message(*args, note=note, **kwargs))
else:
    def send_message(*args, **kwargs):
        print(*args, ', '.join(f'{k}={v!r}' for k, v in kwargs.items()))
