import datetime
import itertools
import random
import sys
from collections import deque

import joblib
import mido

from musictool import config
from musictool import voice_leading
from musictool.daw.midi.parse.sounds import ParsedMidi
from musictool.daw.streams.pcmfile import PCM16File
from musictool.daw.streams.speakers import Speakers
from musictool.daw.streams.video.stream import Video
from musictool.daw.streams.wavfile import WavFile
from musictool.daw.vst.adsr import ADSR
from musictool.daw.vst.organ import Organ
from musictool.daw.vst.sampler import Sampler
from musictool.daw.vst.sine import Sine8
from musictool.note import SpecificNote
from musictool.notes import note_range
from musictool.rhythm import Rhythm
from musictool.scale import Scale
from musictool.util.text import ago

memory = joblib.Memory('static/cache', verbose=0)


# @memory.cache
def make_rhythms():
    _ = (Rhythm.all_rhythms(n_notes) for n_notes in range(5, 8 + 1))
    _ = itertools.chain.from_iterable(_)
    return tuple(_)


# @memory.cache
def make_progressions(note_range_, scale=Scale.from_name('C', 'phrygian')):
    progressions = []
    scales = [Scale.from_name(note, name) for note, name in scale.note_scales.items()]
    for scale in scales:
        for dist, p in voice_leading.make_progressions(scale, note_range_):
            P = p, dist, scale
            progressions.append(P)
            config.progressions_search_cache[''.join(c.root.name for c in p)].append(P)
    return progressions


def render_loop(stream, rhythms, progression, bass, synth, drum_midi, drumrack, messages):

    progression, dist, scale = progression
    # rhythm = random.choice(rhythms)

    bass_midi = []
    chord_midi = []

    config.tuning = random.randint(*config.RANDOM_TUNING_RANGE) if random.random() < 0.15 else config.DEFAULT_TUNING

    drumrack.note_mute = {
        SpecificNote('C', 3): random.random() < 0.1,
        SpecificNote('e', 3): random.random() < 0.1,
        SpecificNote('b', 3): random.random() < 0.1,
        SpecificNote('f', 3): random.random() < 0.5,
    }

    bass.mute = random.random() < 0.03

    bass_rhythm0 = random.choice(rhythms)
    bassline_str = f'bassline {bass_rhythm0.bits}'
    rhythm_score_str = f'score {bass_rhythm0.score:.2f}'

    if random.random() < 0.05:
        bass_rhythm1 = random.choice(rhythms)
        bassline_str += f' {bass_rhythm1.bits}'
        rhythm_score_str += f' {bass_rhythm1.score:.2f}'
    else:
        bass_rhythm1 = bass_rhythm0

    for chord_i, chord in enumerate(progression):
        # bass_midi = rhythm.to_midi(note_=chord.notes_ascending[0] + 12)
        # bass_midi = rhythm.to_midi(note_=chord.notes_ascending[0] + -12)

        # bass_midi = rhythm.to_midi(note_=chord.notes_ascending[0])
        # bass_midi.append(rhythm.to_midi(note_=chord.notes_ascending[0]))
        if chord_i % 2 == 0:
            bass_midi.append(bass_rhythm0.to_midi(note_=chord.notes_ascending[0] + -12))
        else:
            bass_midi.append(bass_rhythm1.to_midi(note_=chord.notes_ascending[0] + -12))

        # chord_midi = rhythm.to_midi(chord=chord)
        # chord_midi = chord.to_midi(n_bars=1)
        chord_midi.append(chord.to_midi(n_bars=1))

        # render.chunked(stream, ParsedMidi.vstack(
        #     [drum_midi, bass_midi, chord_midi],
        #     [drumrack, bass, synth],
        # ))

    bass._adsr.decay = random.uniform(0.1, 0.5)
    bass_midi = ParsedMidi.hstack(bass_midi)
    chord_midi = ParsedMidi.hstack(chord_midi)

    timestamp, rest = random.choice(messages).split(maxsplit=1)
    timestamp = int(timestamp)
    ago_ = ago(datetime.datetime.now().timestamp() - timestamp)
    sha, message = rest.split(maxsplit=1)

    stream.render_chunked(ParsedMidi.vstack(
        [drum_midi, bass_midi, chord_midi],
        [drumrack, bass, synth],
        ['drumrack', 'bass', 'synth'],
        meta={
            'muted': {
                'kick': drumrack.note_mute[SpecificNote('C', 3)],
                'clap': drumrack.note_mute[SpecificNote('e', 3)],
                'open_hat': drumrack.note_mute[SpecificNote('b', 3)],
                'closed_hat': drumrack.note_mute[SpecificNote('f', 3)],
                'bassline': bass.mute,
            },
            'message': f'{sha} | {ago_} | {message}',
            # 'bassline': f'bassline {rhythm.bits}',
            'bassline': bassline_str,
            # 'rhythm_score': f'score{rhythm.score:.2f}',
            'rhythm_score': rhythm_score_str,
            'bass_decay': f'bass_decay{bass._adsr.decay:.2f}',
            'tuning': f'tuning{config.tuning}Hz',
            'root_scale': f'root scale: {scale.root.name} {scale.name}',
            'progression': progression,
            'dist': f'dist{dist}',
            'scale': scale,
        },
    ))


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

    is_test = False
    if len(sys.argv) == 1:
        output = Speakers
    else:
        if sys.argv[1] == 'video_test':
            output = Video
            config.OUTPUT_VIDEO = '/dev/null'
            # config.OUTPUT_VIDEO = '/tmp/output.flv'
            config.beats_per_minute = 480
            # config.frame_width = 426
            # config.frame_width = 240
            is_test = True
            n_loops = 2
        elif sys.argv[1] == 'video_file':
            output = Video
            config.OUTPUT_VIDEO = '/tmp/output.flv'
            is_test = True
            n_loops = int(sys.argv[2]) if len(sys.argv) == 3 else 4
        elif sys.argv[1] == 'video':
            # from musictool.ui.server import start_ui
            # start_ui()
            import credentials
            config.OUTPUT_VIDEO = credentials.stream_url
            output = Video
        else:
            output = {
                'speakers': Speakers,
                'wav': WavFile,
                'pcm': PCM16File,
            }[sys.argv[1]]

    # C = make_rhythms(SpecificNote('C', 4))
    #
    # notes_rhythms = [
    #     make_rhythms(SpecificNote('b', 3)),
    #     make_rhythms(SpecificNote('a', 3)),
    #     make_rhythms(SpecificNote('G', 3)),
    #     make_rhythms(SpecificNote('F', 3)),
    # ]

    # config.note_range = note_range(SpecificNote('C', 3), SpecificNote('G', 6))
    # config.note_range = note_range(SpecificNote('C', 3), SpecificNote('G', 5))  # bass !
    # config.note_range = note_range(SpecificNote('C', 3), SpecificNote('C', 6))
    # config.note_range = note_range(SpecificNote('C', 4), SpecificNote('C', 7))
    config.note_range = note_range(SpecificNote('C', 5), SpecificNote('C', 8))
    rhythms = make_rhythms()
    config.progressions = make_progressions(config.note_range, scale=Scale.from_name('C', 'major'))
    config.progressions_queue = deque()
    config.note_range = note_range(config.note_range[0] + -24, config.note_range[-1])

    # n = len(notes_rhythms[0])

    # drum_midi = mido.MidiFile(config.midi_folder + 'drumloop.mid')
    # drum_midi = ParsedMidi.hstack([mido.MidiFile(config.midi_folder + 'drumloop.mid')] * 4)
    drum_midi = ParsedMidi.hstack([mido.MidiFile(config.midi_folder + 'drumloop-with-closed-hat.mid')] * config.bars_per_screen)

    # m1 = mido.MidiFile(config.midi_folder + '153_0101000101010010.mid')
    bass = Organ(adsr=ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1), amplitude=0.05, transpose=-12)
    drumrack = Sampler()
    # synth = Sine(adsr=ADSR(attack=0.05, decay=0.1, sustain=1, release=0.1), amplitude=0.025)
    synth = Sine8(adsr=ADSR(attack=0.05, decay=0.1, sustain=1, release=0.1), amplitude=0.003, transpose=-24)
    # midi = ParsedMidi.from_files(['153_0101000101010010.mid'z, '153_0101000101010010.mid'], vst=(
    # midi = ParsedMidi.from_files(['drumloop.mid', '153_0101000101010010.mid'], vst=(
    # midi = ParsedMidi.from_files(['drumloop.mid', 'bassline.mid'], vst=(
    # # midi = ParsedMidi.vstack([m0, m1], vst=(
    #     vst.Sampler(),
    #     bass,
    # ))

    messages = open('static/messages.txt').read().splitlines()

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

        if is_test:
            for _ in range(n_loops):
                render_loop(stream, rhythms, random.choice(config.progressions), bass, synth, drum_midi, drumrack, messages)
        else:
            while True:
                if len(config.progressions_queue) < 4:
                    config.progressions_queue.append(random.choice(config.progressions))
                render_loop(stream, rhythms, config.progressions_queue.popleft(), bass, synth, drum_midi, drumrack, messages)

        # for _ in range(1):
        #     i = random.randrange(0, n)
        #     for _ in range(1):
        #         midi = ParsedMidi.vstack([drum_midi, C[i]], vst=(vst.Sampler(), bass))
        #         render.chunked(stream, midi)
        #     for _ in range(3):
        #         midi = ParsedMidi.vstack([drum_midi, random.choice(notes_rhythms)[i]], vst=(vst.Sampler(), bass))
        #         render.chunked(stream, midi)

    print('exit main')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
