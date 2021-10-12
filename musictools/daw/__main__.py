from .. import config
from ..midi.parse import parse_midi
from . import render


def main() -> int:
    import pyaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=config.sample_rate, output=True)

    notes, song_samples = parse_midi(config.midi_file)
    print(notes)
    print('song_samples', song_samples)
    render.single(stream, notes, song_samples)
    render.chunked(stream, notes, song_samples)

    stream.stop_stream()
    stream.close()
    p.terminate()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
