from collections.abc import Iterable
from collections.abc import Sequence
from pathlib import Path
from typing import get_args

import mido

from musictool import config
from musictool.daw.midi.notesound import NoteSound
from musictool.daw.vst.base import VST
from musictool.util import color as colorutil

PathLike = str | Path


class ParsedMidi:
    def __init__(
        self,
        midi: mido.MidiFile,
        vst: VST | Sequence[VST],
        tracknames: Sequence[str] | None = None,
        meta: dict | None = None,
    ):
        """
        :param midi: Midi with one or many channels
        :param vst:
        :param meta: extra meta information to store
        :return:
        """
        ticks_info = dict()
        notes = []
        numerator = None

        if len(midi.tracks) == 1:
            vst = [vst]

        if tracknames is None:
            tracknames = [f'track_{i}' for i in range(len(vst))]

        color = None
        trackname = None

        for i, (track, vst_, name) in enumerate(zip(midi.tracks, vst, tracknames)):
            ticks, seconds, n_samples, n_frames = 0, 0., 0, 0
            note_buffer_samples = dict()
            note_buffer_seconds = dict()
            note_buffer_frames = dict()
            for message in track:
                ticks += message.time

                # print(track, message)
                if message.type == 'time_signature':
                    if message.denominator != 4:
                        raise NotImplementedError('denominators other than 4 are not supported')
                    numerator = message.numerator
                    ticks_per_bar = numerator * midi.ticks_per_beat

                d_seconds = mido.tick2second(message.time, midi.ticks_per_beat, mido.bpm2tempo(config.beats_per_minute))
                seconds += d_seconds
                n_samples += int(config.sample_rate * d_seconds)
                n_frames += int(config.fps * d_seconds)
                if message.type == 'note_on':
                    note_buffer_samples[message.note] = n_samples
                    note_buffer_seconds[message.note] = seconds
                    note_buffer_frames[message.note] = n_frames
                elif message.type == 'note_off':
                    notes.append(NoteSound(
                        message.note,
                        vst_,
                        note_buffer_samples.pop(message.note), n_samples,
                        note_buffer_seconds.pop(message.note), seconds,
                        note_buffer_frames.pop(message.note), n_frames,
                        color=color,
                        trackname=trackname,
                    ))
                elif message.type == 'marker' and meta is not None:
                    color = meta['scale'].note_colors[message.text]  # chord root
                elif message.type == 'track_name':
                    trackname = message.name
            # rounded = self.round_ticks_to_bar(ticks, ticks_per_bar)
            # if rounded < ticks:
            #     raise OverflowError('midi ticks are bigger than 1 bar')
            # assert ticks <= rounded
            # print('------->', ticks, rounded)
            # ticks_info[i] = rounded
            ticks_info[i] = self.round_ticks_to_bar(ticks, ticks_per_bar)
        if not len(set(ticks_info.values())) == 1:
            raise ValueError(f'number of ticks rounded to bar should be equal for all midi tracks/channels {ticks_info}')
        ticks = next(iter(ticks_info.values()))
        self.n_bars = ticks // ticks_per_bar

        # assert abs(seconds - mido.tick2second(ticks, midi.ticks_per_beat, mido.bpm2tempo(config.beats_per_minute))) < 0.1
        # print(seconds, mido.tick2second(ticks, midi.ticks_per_beat, mido.bpm2tempo(config.beats_per_minute)))
        # print('n_frames', seconds, n_frames, int(config.fps * seconds))
        # print('n_samples', seconds, n_samples, int(config.sample_rate * seconds))

        # you should round also seconds, frames, samples etc
        # assert seconds == mido.tick2second(ticks, midi.ticks_per_beat, mido.bpm2tempo(config.beats_per_minute))
        # assert n_frames == int(config.fps * seconds)
        # assert n_samples == int(config.sample_rate * seconds)
        # assert n_pixels == int(config.pxps * seconds), (seconds, n_pixels, int(config.pxps * seconds), config.pxps)
        self.seconds = mido.tick2second(ticks, midi.ticks_per_beat, mido.bpm2tempo(config.beats_per_minute))
        self.n_frames = int(config.fps * self.seconds)
        # print(self.n_frames)
        self.n_samples = int(config.sample_rate * self.seconds)
        self.numerator = numerator
        # self.notes = notes
        self.notes = set(notes)
        self.meta = meta

        for note in self.notes:
            note.px_on = int(config.frame_height * note.sample_on / self.n_samples)
            note.px_off = int(config.frame_height * note.sample_off / self.n_samples)
            if note.trackname == 'bass' or note.trackname == 'drumrack':
                note.smooth_rendering = False
            if note.trackname == 'drumrack' or note.trackname == 'bass':
                note.color = colorutil.random_rgb()

        # self.note_colors = {note: util.random_rgba() for note in self.notes}
        self.reset(reset_notes=False)
        # self.playing_notes = set()
        # self.releasing_notes = set()
        # self.done_notes = set()
        # self.drawn_notes = set()

    def round_ticks_to_bar(self, ticks, ticks_per_bar):
        full_bars, mod = divmod(ticks, ticks_per_bar)
        if mod:
            ticks += ticks_per_bar - mod
        return ticks

    def reset(self, reset_notes=True):
        if reset_notes:
            for note in self.notes:
                note.reset()
        self.playing_notes = set()
        self.releasing_notes = set()
        self.done_notes = set()
        self.drawn_not_complete_notes = set()

    # @classmethod
    # @functools.singledispatchmethod # TODO
    # def vstack(cls, midis: Sequence[PathLike] | Sequence[mido.MidiFile], vst: Sequence[VST]):
    #     if isinstance(Sequence)

    @classmethod
    def from_files(cls, midi_files: PathLike | Sequence[PathLike], vst: VST | Sequence[VST], meta: dict | None = None):
        if isinstance(midi_files, get_args(PathLike)):  # get_args is shitty but works
            assert isinstance(vst, VST)
            midi = mido.MidiFile(config.midi_folder + midi_files, type=0)
            return cls(midi, vst)
        return cls.vstack([mido.MidiFile(config.midi_folder + f, type=0) for f in midi_files], vst, meta)

    @classmethod
    def vstack(
        cls,
        midi_objects: Sequence[mido.MidiFile],
        vst: Sequence[VST],
        tracknames: Sequence[str] | None = None,
        meta: dict | None = None,
    ):
        """
        convert many midi objects into one with multiple channels (vertical stacking)
        """
        assert len(midi_objects) == len(vst)

        if tracknames is not None:
            assert len(tracknames) == len(midi_objects)
        else:
            tracknames = [
                Path(track_midi.filename).stem if track_midi.filename is not None else f'track_{i}'
                for i, track_midi in enumerate(midi_objects)
            ]

        midi = mido.MidiFile(type=1)

        numerators, denominators = set(), set()
        ticks_per_beat_s = dict()

        for i, (track_midi, trackname) in enumerate(zip(midi_objects, tracknames)):
            # print(f)
            track = mido.MidiTrack()
            time_signature_parsed = False
            ticks_per_beat_s[i] = track_midi.ticks_per_beat

            for message in track_midi.tracks[0]:
                # print(message)
                if message.type == 'track_name':
                    message.name = trackname
                elif message.type == 'time_signature':
                    numerators.add(message.numerator)
                    denominators.add(message.denominator)
                    if time_signature_parsed:
                        continue
                    else:
                        time_signature_parsed = True
                elif message.type == 'note_on' or message.type == 'note_off':
                    message.channel = i
                track.append(message)
            if not time_signature_parsed:
                raise ValueError(f'input midi {i} {track_midi.filename} must have time_signature message')

            midi.tracks.append(track)

        if not len(set(ticks_per_beat_s.values())) == 1:
            raise NotImplementedError(f'cant merge midi files with different ticks_per_beat: {ticks_per_beat_s}')

        midi.ticks_per_beat = next(iter(ticks_per_beat_s.values()))  # in merged file must be as in input files

        if not (len(numerators) == len(denominators) == 1):
            raise NotImplementedError(f'cant merge midi files with different or without time_signatures (numerator {numerators} and denominator {denominators})')
        return cls(midi, vst, tracknames, meta)

    @classmethod
    def from_file(cls, midi_file, vst: VST, meta: dict | None = None):
        track_midi = mido.MidiFile(config.midi_folder + midi_file, type=1)
        return cls(track_midi, vst, [Path(track_midi.filename).stem], meta)

    @staticmethod
    def hstack(midi_objects: Iterable[mido.MidiFile]) -> mido.MidiFile:
        """
        convert many midi objects into one: objects goes one by one after each other (horizontal stacking)
        TODO: assert all midis have same ticks_per_beat_s, numerators, denominators etc
        TODO: accept multi-
        TODO: assert all midis are 1-bar length (mvp, then maybe support arbitary length midi objects)
        TODO: test carefully
        :param midis:
        :return:
        """
        mid = mido.MidiFile(type=0)
        track = mido.MidiTrack()
        track.append(mido.MetaMessage(type='track_name', name='concatenated_midi'))
        time_signature = mido.MetaMessage(type='time_signature', numerator=4, denominator=4, clocks_per_click=36)
        track.append(time_signature)

        # time_signatures = dict()
        ticks_per_beat_set = set()

        for i, midi in enumerate(midi_objects):
            ticks = 0

            ticks_per_beat_set.add(midi.ticks_per_beat)

            if len(midi.tracks) != 1:
                raise NotImplementedError(f'now can hstack only midi objects with 1 track, {i}th midi object has {len(midi.tracks)}')

            for message in midi.tracks[0]:
                ticks += message.time

                if message.type == 'time_signature':
                    assert message == time_signature
                    # time_signatures[i] = message
                    # if message.denominator != 4:
                    #     raise NotImplementedError('denominators other than 4 are not supported')
                    numerator = message.numerator
                    ticks_per_bar = numerator * midi.ticks_per_beat

                if message.type == 'note_on' or message.type == 'note_off' or message.type == 'marker':
                    # m = message.copy()
                    # m.time =
                    track.append(message)
            track.append(mido.MetaMessage(type='text', text='end_of_bar', time=ticks_per_bar - ticks))
        # assert util.all_equal(time_signatures.values())

        assert len(ticks_per_beat_set) == 1
        mid.ticks_per_beat = next(iter(ticks_per_beat_set))
        # print(mid.ticks_per_beat, mid.ticks_per_beat * numerator)

        mid.tracks.append(track)
        return mid
