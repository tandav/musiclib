from . import config

if config.midi:
    import mido
    port = mido.open_output(config.midi_device)
    def send_message(*args, **kwargs):
        port.send(mido.Message(*args, **kwargs))
else:
    def send_message(*args, **kwargs):
        print(*args)
