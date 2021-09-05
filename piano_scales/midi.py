import os

if (midi_device := os.environ.get('MIDI_DEVICE')):
    import mido
    port = mido.open_output(midi_device)

    def send_message(*args, **kwargs):
        port.send(mido.Message(*args, **kwargs))
else:
    def send_message(*args, **kwargs):
        print(*args)
