import argparse
import itertools
import random
import sys

import mido

from musictools import config
from musictools import voice_leading
from musictools.daw import streams
from musictools.daw import vst
from musictools.daw.midi.parse import ParsedMidi
from musictools.note import SpecificNote
from musictools.note import note_range
from musictools.rhythm import Rhythm
from musictools.scale import Scale
# import joblib
# memory = joblib.Memory('/tmp', verbose=0)

# @memory.cache
def make_rhythms():
    _ = (Rhythm.all_rhythms(n_notes) for n_notes in range(6, 8 + 1))
    _ = itertools.chain.from_iterable(_)
    # return tuple(rhythm.to_midi(note_=note) for rhythm in _)
    return tuple(_)

# @memory.cache
def make_progressions():
    progressions = []
    for scale in config.diatonic[:-1]:
        # for dist, p in voice_leading.make_progressions(Scale('C', scale), note_range(SpecificNote('G', 2), SpecificNote('C', 6))):
        for dist, p in voice_leading.make_progressions(Scale('C', scale), note_range(SpecificNote('C', 3), SpecificNote('G', 6))):
            progressions.append(p)
    return progressions

#     s = Scale('C', 'major')
#     s = Scale('C', 'phrygian')
#     s = Scale('C', 'dorian')
#     s = Scale('C', 'lyd/ian')
#     s = Scale('C', 'mixolydian')
#     s = Scale('C', 'minor')


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

    # C = make_rhythms(SpecificNote('C', 4))
    #
    # notes_rhythms = [
    #     make_rhythms(SpecificNote('b', 3)),
    #     make_rhythms(SpecificNote('a', 3)),
    #     make_rhythms(SpecificNote('G', 3)),
    #     make_rhythms(SpecificNote('F', 3)),
    # ]

    rhythms = make_rhythms()
    progressions = make_progressions()

    # n = len(notes_rhythms[0])

    drum_midi = mido.MidiFile(config.midi_folder + 'drumloop.mid')
    # m1 = mido.MidiFile(config.midi_folder + '153_0101000101010010.mid')
    bass = vst.Organ(adsr=vst.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
    drumrack = vst.Sampler()
    synth = vst.Sine(adsr=vst.ADSR(attack=0.05, decay=0.1, sustain=1, release=0.1))


    # midi = ParsedMidi.from_files(['153_0101000101010010.mid'z, '153_0101000101010010.mid'], vst=(
    # midi = ParsedMidi.from_files(['drumloop.mid', '153_0101000101010010.mid'], vst=(
    # midi = ParsedMidi.from_files(['drumloop.mid', 'bassline.mid'], vst=(
    # # midi = ParsedMidi.from_many([m0, m1], vst=(
    #     vst.Sampler(),
    #     bass,
    # ))

    counter = 0
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

    # midi.rhythm_to_midi(r, Path.home() / f"Desktop/midi/prog.mid",  progression=p)

        while True:
            progression = random.choice(progressions)
            # print(progression)
            rhythm = random.choice(rhythms)
            for chord in progression:
                # bass_midi = rhythm.to_midi(note_=chord.notes_ascending[0] + 12)
                # bass_midi = rhythm.to_midi(note_=chord.notes_ascending[0] + -12)
                bass_midi = rhythm.to_midi(note_=chord.notes_ascending[0])
                # chord_midi = rhythm.to_midi(chord=chord)
                chord_midi = chord.to_midi()
                # render.chunked(stream, ParsedMidi.from_many(
                #     [drum_midi, bass_midi, chord_midi],
                #     [drumrack, bass, synth],
                # ))
                bass._adsr.decay = random.uniform(0.1, 0.5)
                synth.amplitude = 0.025
                stream.render_chunked(ParsedMidi.from_many(
                    [drum_midi, bass_midi, chord_midi],
                    [drumrack, bass, synth],
                    meta={'bassline': rhythm.bits, 'chords': '\n'.join(map(str,progression))},
                ))
            # counter += 1
            # if counter % 10 == 0:
            #     print('gc.collect()')
                # gc.collect()


        # for _ in range(1):
        #     i = random.randrange(0, n)
        #     for _ in range(1):
        #         midi = ParsedMidi.from_many([drum_midi, C[i]], vst=(vst.Sampler(), bass))
        #         render.chunked(stream, midi)
        #     for _ in range(3):
        #         midi = ParsedMidi.from_many([drum_midi, random.choice(notes_rhythms)[i]], vst=(vst.Sampler(), bass))
        #         render.chunked(stream, midi)


    print('exit main')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
