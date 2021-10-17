from .. import config
from . import render
from . import streams
from . import vst
from .midi.parse import ParsedMidi


def main() -> int:
    # synth = vst.Sampler(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
    # synth = vst.Sine(adsr=vst.ADSR(attack=0.05, decay=0.3, sustain=0.1, release=0.1))
    # synth = vst.Sine(adsr=vst.ADSR(attack=0.001, decay=0.05, sustain=1, release=1))
    # synth = vst.Organ(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
    # midi = ParsedMidi.from_file(config.midi_file, vst=synth)
    # midi = ParsedMidi.from_file('drumloop.mid', vst=synth)
    # midi = ParsedMidi.from_file('bassline.mid', vst=synth)
    # midi = ParsedMidi.from_file('4-4-8.mid', vst=synth)
    # midi = ParsedMidi.from_files(['4-4-8.mid', '4-4-8-offbeat.mid'], vst=(
    midi = ParsedMidi.from_files(['drumloop.mid', 'bassline.mid'], vst=(
        vst.Sampler(),
        vst.Organ(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1)),
    ))

    # with streams.Speakers() as stream:
    # with streams.WavFile(config.wav_output_file, dtype='float32') as stream:
    # with streams.WavFile(config.wav_output_file, dtype='int16') as stream:
    # with streams.PCM16File(config.audio_pipe) as stream:
    with streams.YouTube(config.audio_pipe) as stream:
        for _ in range(1):
            render.single(stream, midi)
            # render.chunked(stream, midi)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
