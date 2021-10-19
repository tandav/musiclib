import mido

from .. import config
from . import render
from . import streams
from . import vst
from ..rhythm import Rhythm
from .midi.parse import ParsedMidi
from ..note import SpecificNote
import itertools
import random
from .midi.player import rhythm_to_midi
import argparse
import sys


def make_rhythms(note):
    _ = (Rhythm.all_rhythms(n_notes) for n_notes in range(6, 8 + 1))
    _ = itertools.chain.from_iterable(_)
    return tuple(rhythm_to_midi(rhythm, note_=note) for rhythm in _)


def main() -> int:
    # todo: argparse
    # parser = argparse.ArgumentParser(description='Run streaming, pass output stream')
    # parser.add_argument('--output', action='store_const', const=streams.Speakers , default=streams.Speakers)
    # parser.add_argument('--speakers', dest='output_stream', action='store_const', const=streams.Speakers , help='stream to speakers')
    # parser.add_argument('--youtube' , dest='output_stream', action='store_const', const=streams.YouTube  , help='stream to youtube')
    # parser.add_argument('--wav'     , dest='output_stream', action='store_const', const=streams.WavFile  , help='save to wave/riff file')
    # parser.add_argument('--pcm'     , dest='output_stream', action='store_const', const=streams.PCM16File, help='save to pcm16 file')
    # args = parser.parse_args()
    # print(args, args.output_stream)
    # print(args)
    # raise
    # synth = vst.Sampler(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
    # synth = vst.Sine(adsr=vst.ADSR(attack=0.05, decay=0.3, sustain=0.1, release=0.1))
    # synth = vst.Sine(adsr=vst.ADSR(attack=0.001, decay=0.05, sustain=1, release=1))
    # synth = vst.Organ(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
    # midi = ParsedMidi.from_file(config.midi_file, vst=synth)
    # midi = ParsedMidi.from_file('drumloop.mid', vst=synth)
    # midi = ParsedMidi.from_file('bassline.mid', vst=synth)
    # midi = ParsedMidi.from_file('4-4-8.mid', vst=synth)
    # midi = ParsedMidi.from_files(['4-4-8.mid', '4-4-8-offbeat.mid'], vst=(

    if len(sys.argv) == 1:
        output = streams.Speakers
    else:
        output = {
            'speakers': streams.Speakers,
            'youtube': streams.YouTube,
            'wav': streams.WavFile,
            'pcm': streams.PCM16File,
            # 'devnull': streams.DevNull,
        }[sys.argv[1]]

    C = make_rhythms(SpecificNote('C', 4))

    notes_rhythms = [
        make_rhythms(SpecificNote('b', 3)),
        make_rhythms(SpecificNote('a', 3)),
        make_rhythms(SpecificNote('G', 3)),
        make_rhythms(SpecificNote('F', 3)),
    ]

    n = len(notes_rhythms[0])

    m0 = mido.MidiFile(config.midi_folder + 'drumloop.mid')
    # m1 = mido.MidiFile(config.midi_folder + '153_0101000101010010.mid')
    bass = vst.Organ(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))

    # midi = ParsedMidi.from_files(['153_0101000101010010.mid'z, '153_0101000101010010.mid'], vst=(
    # midi = ParsedMidi.from_files(['drumloop.mid', '153_0101000101010010.mid'], vst=(
    midi = ParsedMidi.from_files(['drumloop.mid', 'bassline.mid'], vst=(
    # midi = ParsedMidi.from_many([m0, m1], vst=(
        vst.Sampler(),
        bass,
    ))
    # with streams.WavFile(config.wav_output_file, dtype='float32') as stream:
    # with streams.WavFile(config.wav_output_file, dtype='int16') as stream:
    # with streams.WavFile(config.wav_output_file, dtype='int16') as stream:
    # with streams.PCM16File(config.audio_pipe) as stream:
    # with streams.Speakers() as stream:
    with output() as stream:
        # for _ in range(4): render.chunked(stream, midi)
        # for _ in range(4): render.single(stream, midi)
        # for _ in range(1): render.chunked(stream, midi)
        # for _ in range(4): render.single(stream, ParsedMidi.from_file('weird.mid', vst=synth))
    #     for _ in range(4): render.chunked(stream, ParsedMidi.from_file('dots.mid', vst=synth))

        while True:
        # for _ in range(1):
            i = random.randrange(0, n)
            for _ in range(1):
                midi = ParsedMidi.from_many([m0, C[i]], vst=(vst.Sampler(), bass))
                render.chunked(stream, midi)
            for _ in range(3):
                midi = ParsedMidi.from_many([m0, random.choice(notes_rhythms)[i]], vst=(vst.Sampler(), bass))
                render.chunked(stream, midi)


    print('exit main')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
