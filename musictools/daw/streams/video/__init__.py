import concurrent.futures
import os
import queue
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

from musictools import config
from musictools import util
from musictools.daw.midi.parse import ParsedMidi
from musictools.daw.streams.base import Stream
from musictools.daw.streams.video import ffmpeg
from musictools.daw.streams.video.pipewriter import PipeWriter
from musictools.util import image as imageutil
from musictools.util.signal import float32_to_int16

# https://support.google.com/youtube/answer/6375112
# https://support.google.com/youtube/answer/1722171
# https://support.google.com/youtube/answer/2853702 # streaming

# TODO: change to thread-safe queue.Queue
#   also compare speed of appendleft, pop vs append, popleft?

# im = np.ones(shape=(config.frame_height, config.frame_width, 4), dtype=np.uint8)
font = cv2.FONT_HERSHEY_SIMPLEX

# piano = np.full(shape=(config.frame_height, config.frame_width, 4), fill_value=255, dtype=np.uint8)
# piano[:, :, :3] = 180
# black_white_pattern = itertools.cycle(bool(int(x)) for x in '010100101010')
# for x, is_black in zip(range(0, config.frame_width, config.key_width), black_white_pattern):
#     thickness = cv2.FILLED if is_black else 1
#     cv2.rectangle(piano, pt1=(x, 0), pt2=(x + config.key_width, config.frame_height), color=(0, 0, 0, 255), thickness=thickness)


# bg = np.full(shape=(config.frame_height, config.frame_width, 4), fill_value=255, dtype=np.uint8)
bg = np.zeros((config.frame_height, config.frame_width, 4), dtype=np.uint8)
bg[:, :, -1] = 255
chord_length = config.frame_height / 4


# def make_frame(y, meta, bg, bg_bright):
def make_frame(args):
    y, meta, bg, bg_bright, note_to_x, key_width = args
    # print('zed')

    chord_i = int(y / chord_length)
    chord_start_px = int(chord_i * chord_length)

    chord = meta['progression'][chord_i]
    background_color = meta['scale'].note_colors[chord.root]

    # self.background_draw.rectangle((chord_start_px, 0, x + frame_dx, config.frame_height), fill=background_color)
    # self.background_draw = self.background_draw.draw_rect(background_color, chord_start_px, 0, x + frame_dx - chord_start_px, config.frame_height, fill=True)
    # self.background_draw = self.background_draw.draw_rect(background_color, chord_start_px, 0, x - chord_start_px, config.frame_height, fill=True)
    # ..method:: draw_rect(ink, left, top, width, height, fill=bool)

    # cv2.rectangle(im, pt1=(chord_start_px, 0), pt2=(x, config.frame_height), color=background_color, thickness=cv2.FILLED)
    # cv2.rectangle(self.progress, pt1=(0, chord_start_px), pt2=(config.frame_width, y), color=background_color, thickness=cv2.FILLED)

    for note in chord.notes_ascending:
        cv2.rectangle(bg_bright, pt1=(note_to_x[note], chord_start_px), pt2=(note_to_x[note] + key_width, y), color=background_color, thickness=cv2.FILLED)

    # cv2.rectangle(bg_bright, pt1=(0, chord_start_px), pt2=(config.frame_width, y), color=background_color, thickness=cv2.FILLED)

    im = imageutil.overlay_image(bg, bg_bright, alpha=1.0)
    im = cv2.flip(im, 0)
    for note in chord.notes_ascending:
        cv2.putText(im, repr(note), (note_to_x[note], config.frame_height - chord_start_px), font, fontScale=1, color=config.BLACK, thickness=2, lineType=cv2.LINE_AA)

    for note in chord.root_specific:
        cv2.putText(im, 'r', (note_to_x[note], config.frame_height - (chord_start_px + util.rel_to_abs_h(0.03))), font, fontScale=1, color=config.BLACK, thickness=2, lineType=cv2.LINE_AA)

    # print('kek')
    # for _ in range(1):
    # cv2.rectangle(im, pt1=util.random_xy(), pt2=util.random_xy(), color=util.random_color(), thickness=1)
    # cv2.rectangle(im, pt1=util.random_xy(), pt2=util.random_xy(), color=(0,0,0), thickness=1)

    cv2.putText(im, meta['message'], util.rel_to_abs(0, 0.03), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(im, meta['bassline'], util.rel_to_abs(0, 0.07), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(im, meta['rhythm_score'], util.rel_to_abs(0, 0.1), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(im, meta['bass_decay'], util.rel_to_abs(0, 0.13), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(im, meta['tuning'], util.rel_to_abs(0, 0.16), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(im, meta['dist'], util.rel_to_abs(0, 0.19), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(im, meta['root_scale'], util.rel_to_abs(0, 0.22), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(im, f'sys.platform {sys.platform}', util.rel_to_abs(0, 0.25), font, fontScale=1, color=(config.WHITE), thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(im, f'bpm {config.beats_per_minute}', util.rel_to_abs(0, 0.28), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(im, f'sample_rate {config.sample_rate}', util.rel_to_abs(0, 0.31), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(im, f"{chord.root.name} {chord.abstract.name} | {meta['scale'].note_scales[chord.root]}", (util.rel_to_abs_w(0.82), config.frame_height - (chord_start_px + util.rel_to_abs_h(0.01))), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    # cv2.putText(im, str(chord), (util.rel_to_abs_w(0.6), config.frame_height - chord_start_px), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    for _ in range(2):
        cv2.putText(im, '*', util.random_xy(), font, fontScale=1, color=config.WHITE, thickness=1, lineType=cv2.LINE_AA)
    cv2.putText(im, 'tandav.me', util.rel_to_abs(0.8, 0.07), font, fontScale=2, color=config.BLACK, thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(im, 'tandav.me', util.rel_to_abs(0.802, 0.072), font, fontScale=2, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
    return im.tobytes()


class Video(Stream):

    def render_chunked(self, track: ParsedMidi, normalize=False):
        self.make_background(track)
        super().render_chunked(track, normalize)

    def make_background(self, track):
        # self.piano = piano.copy()
        # self.progress = piano.copy()

        chord_rects = np.empty_like(bg)

        # self.bg = bg.copy()
        # overlay = bg.copy()
        chord_length_int = int(chord_length)
        for y, chord in zip(range(0, config.frame_height, chord_length_int), track.meta['progression']):
            background_color = track.meta['scale'].note_colors[chord.root]
            cv2.rectangle(chord_rects, pt1=(0, y), pt2=(config.frame_width, y + chord_length_int), color=background_color, thickness=cv2.FILLED)
            cv2.putText(chord_rects, f"{chord.root.name} {chord.abstract.name} | {track.meta['scale'].note_scales[chord.root]}", (util.rel_to_abs_w(0.82), (y + util.rel_to_abs_h(0.01))), font, fontScale=1, color=(210, 210, 210), thickness=2, lineType=cv2.LINE_AA, bottomLeftOrigin=True)

        self.bg = imageutil.overlay_image(bg, chord_rects, alpha=0.3)

        # self.bg = image.overlay_image(self.bg, piano, alpha=0.4)
        # for x, note in zip(range(0, config.frame_width, key_width), config.note_range):
        #     if note.is_black:
        # self.bg = image.overlay_rect(self.bg, pt1=(x, 0), pt2=(x + key_width, config.frame_height), color=(0, 0, 0), alpha=0.5)
        # self.bg = image.overlay_rect(self.bg, pt1=(x, 0), pt2=(x + key_width, config.frame_height), color=(0, 0, 0), alpha=0.5)

        self.note_to_x = dict()
        for x, note in zip(range(0, config.frame_width, self.key_width), config.note_range):
            self.note_to_x[note] = x
            if note.is_black:
                self.bg = imageutil.overlay_rect(self.bg, pt1=(x, 0), pt2=(x + self.key_width, config.frame_height), color=(0, 0, 0), alpha=0.5)
            else:
                cv2.line(self.bg, (x + self.key_width, 0), (x + self.key_width, config.frame_height), (0, 0, 0, 255), thickness=1)

        if self.extra_note_space:
            extra_note, extra_space = self.extra_note_space
            x += self.key_width
            self.bg = imageutil.overlay_rect(self.bg, pt1=(x, 0), pt2=(x + extra_space, config.frame_height), color=(0, 0, 0), alpha=0.5)

        # alpha = 0.3
        # self.bg = cv2.addWeighted(overlay, alpha, self.bg, 1 - alpha, 0)

        # add piano
        # alpha = 0.2
        # self.bg = cv2.addWeighted(piano, alpha, self.bg, 1 - alpha, gamma=0)

        self.bg_bright = self.bg.copy()
        # im[...] = 200
        # im[...] = piano[...]
        # for x, is_black in zip(range(0, config.frame_width, config.key_width), black_white_pattern):
        #     thickness = -1 if is_black else 1
        #     cv2.rectangle(im, pt1=(x, 0), pt2=(x + config.key_width, config.frame_height), color=(0, 0, 0, 50), thickness=thickness)
        # self.background_draw.rectangle((0, 0, config.frame_width, config.frame_height), fill=(200, 200, 200))
        # self.background_draw = self.background_draw.draw_rect((200, 200, 200), 0, 0, config.frame_width, config.frame_height, fill=True)

    def __enter__(self):
        def recreate(p):
            p = Path(p)
            if p.exists():
                p.unlink()
            os.mkfifo(p)

        recreate(config.audio_pipe)
        recreate(config.video_pipe)

        self.ffmpeg = subprocess.Popen(ffmpeg.cmd)

        self.audio_seconds_written = 0.
        self.video_seconds_written = 0.
        self.frames_written = 0  # video
        self.samples_written = 0  # audio

        # self.audio_thread = GenerateAudioToPipe()
        # self.video_thread = GenerateVideoToPipe()
        # qsize = 2 ** 9
        # qsize = 2 ** 11
        # qsize = 2 ** 4
        qsize = 2 ** 6
        # qsize = 2 ** 8
        self.q_audio = queue.Queue(maxsize=qsize)
        self.q_video = queue.Queue(maxsize=qsize)
        # self.q_audio = collections.deque(maxlen=qsize)
        # self.q_video = collections.deque(maxlen=qsize)

        self.audio_thread = PipeWriter(config.audio_pipe, self.q_audio)
        self.video_thread = PipeWriter(config.video_pipe, self.q_video)
        self.audio_thread.start()
        self.video_thread.start()

        # self.vbuff = io.BytesIO()
        self.key_width = config.frame_width // len(config.note_range)

        self.extra_note_space = None
        if (extra_space := config.frame_width % self.key_width):
            extra_note = config.note_range[-1] + 1
            if extra_note.is_black:  # if it white there is nothing extra to do
                self.extra_note_space = extra_note, extra_space

        self.t_start = time.time()
        return self

    def __exit__(self, type, value, traceback):
        self.audio_thread.stream_finished.set()
        self.video_thread.stream_finished.set()

        self.audio_thread.join()
        self.video_thread.join()
        self.ffmpeg.wait()

        os.unlink(config.audio_pipe)
        os.unlink(config.video_pipe)

        assert self.frames_written == int(self.audio_seconds_written * config.fps)
        print(self.frames_written, self.audio_seconds_written, int(self.audio_seconds_written * config.fps))

    def make_frames(self, n_frames, chunk_width):

        start_px = int(config.frame_height * self.n / self.track.n_samples)  # like n is for audio (progress on track), px is for video (progress on frame)
        frame_dy = chunk_width // n_frames
        # y = start_px

        Y = range(start_px, start_px + frame_dy * n_frames, frame_dy)
        # with concurrent.futures.ThreadPoolExecutor() as pool:

        # with concurrent.futures.ProcessPoolExecutor() as pool:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            # with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            # return tuple(pool.map(self.make_frame, Y))
            # return tuple(pool.map(partial(make_frame, meta=self.track.meta, bg=self.bg, bg_bright=self.bg_bright), Y))
            args = ((y, self.track.meta, self.bg, self.bg_bright, self.note_to_x, self.key_width) for y in Y)
            # return tuple(pool.map(partial(make_frame, meta=self.track.meta, bg=self.bg, bg_bright=self.bg_bright), Y))
            return tuple(pool.map(make_frame, args))

        # frames = []
        #
        # for frame in range(n_frames):
        #     y += frame_dy
        #     frames.append()
        # return frames

    def write(self, data: np.ndarray):
        seconds = len(data) / config.sample_rate
        b = float32_to_int16(data).tobytes()

        real_seconds = time.time() - self.t_start
        if real_seconds < self.audio_seconds_written:
            time.sleep(self.audio_seconds_written - real_seconds)

        self.q_audio.put(b, block=True)
        # self.q_audio.append(b)
        self.samples_written += len(data)
        self.audio_seconds_written += seconds

        n_frames = int(self.audio_seconds_written * config.fps) - self.frames_written
        # assert n_frames > 0
        # if n_frames == 0:
        # if n_frames < 100:
        if n_frames < config.video_queue_item_size:
            # if n_frames < 1:
            # if n_frames < 300:
            return
        print(n_frames)
        chunk_width = int(config.frame_height * len(data) / self.track.n_samples)
        frames = self.make_frames(n_frames, chunk_width)
        # n_frames = int(seconds * config.fps)# - frames_written
        # print('fffffffffff', n_frames)

        for frame in frames:
            self.q_video.put(frame, block=True)

        # q_video.put(self.vbuff.getvalue(), block=True)
        self.frames_written += n_frames
        self.video_seconds_written += n_frames / config.fps

        # print('eeeeeeeeeeeeeeeeee', f'QA{self.q_audio.qsize()} QV{self.q_video.qsize()} {len(data)=} {seconds=} {n_frames=} {self.samples_written:} {self.frames_written=} ASW{self.audio_seconds_written:.2f} VSW{self.video_seconds_written:.2f} {real_seconds=}')
