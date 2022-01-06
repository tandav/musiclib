import os

import mido

if midi_device := os.environ.get('MIDI_DEVICE'):
    port = mido.open_output(midi_device)

    def send_message(*args, **kwargs):
        note = kwargs.pop('note') + 24  # to match ableton octaves
        port.send(mido.Message(*args, note=note, **kwargs))

else:
    def send_message(*args, **kwargs):
        print('MIDI_DEVICE not found |', *args, ', '.join(f'{k}={v!r}' for k, v in kwargs.items()))
