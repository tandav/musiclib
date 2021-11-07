import io
import os
import queue
import subprocess
import sys
import time
from pathlib import Path
from threading import Event
from threading import Thread

import cv2
import numpy as np

from musictools import config
from musictools import util
from musictools.daw.midi.parse import ParsedMidi
from musictools.daw.streams.base import Stream
from musictools.util.signal import float32_to_int16

# https://support.google.com/youtube/answer/6375112
# https://support.google.com/youtube/answer/1722171
# https://support.google.com/youtube/answer/2853702 # streaming

# TODO: change to thread-safe queue.Queue
#   also compare speed of appendleft, pop vs append, popleft?


im = np.ones(shape=(config.frame_height, config.frame_width, 4), dtype=np.uint8)
font = cv2.FONT_HERSHEY_SIMPLEX


class PipeWriter(Thread):
    def __init__(self, pipe, q: queue.Queue):
        # def __init__(self, pipe, q: collections.deque):
        super().__init__()
        self.pipe = pipe
        self.q = q
        self.stream_finished = Event()
        # self.log = open(f'logs/{self.pipe}_log.jsonl', 'w')

    def run(self):
        with open(self.pipe, 'wb') as pipe:
            while not self.stream_finished.is_set() or not self.q.empty():
                # while not self.stream_finished.is_set() or len(self.q):
                # print(self.pipe, self.q.empty(), self.stream_finished.is_set(), 'foo')
                # if self.pipe == config.video_pipe: print(self.pipe, self.q.qsize(), 'lol')
                # print(json.dumps({'timestamp': time.monotonic(), 'writer': self.pipe, 'event': 'write_start', 'qsize': self.q.qsize()}), file=self.log)

                # you can't block w/o timeout because stream_finished event may be set at any time
                try:
                    b = self.q.get(block=True, timeout=0.01)
                    # b = self.q.popleft()
                    # time.sleep(0.01)
                except queue.Empty:
                    # except IndexError:
                    pass
                else:
                    pipe.write(b)
                    self.q.task_done()
                # print(json.dumps({'timestamp': time.monotonic(), 'writer': self.pipe, 'event': 'write_stop', 'qsize': self.q.qsize()}), file=self.log)


class Video(Stream):

    def render_chunked(self, track: ParsedMidi):
        super().render_chunked(track)
        self.clear_background()

    def clear_background(self):
        im[...] = 200
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

        keyframe_seconds = 3

        cmd = ('ffmpeg',
               # '-loglevel', 'trace',
               # '-threads', '2',
               # '-threads', '7',
               # '-y', '-r', '60', # overwrite, 60fps
               # '-re',
               '-y',

               # '-err_detect', 'ignore_err',
               '-f', 's16le',  # means 16bit input
               '-acodec', 'pcm_s16le',  # means raw 16bit input
               '-r', str(config.sample_rate),  # the input will have 44100 Hz
               '-ac', '1',  # number of audio channels (mono1/stereo=2)
               # '-thread_queue_size', thread_queue_size,
               '-thread_queue_size', '1024',
               '-i', config.audio_pipe,


               '-s', f'{config.frame_width}x{config.frame_height}',  # size of image string
               '-f', 'rawvideo',
               '-pix_fmt', 'rgba',  # format
               # '-pix_fmt', 'rgb24',  # format
               '-r', str(config.fps),  # input framrate. This parameter is important to stream w/o memory overflow
               # '-vsync', 'cfr', # kinda optional but you can turn it on
               # '-f', 'image2pipe',
               # '-i', 'pipe:', '-', # tell ffmpeg to expect raw video from the pipe
               # '-i', '-',  # tell ffmpeg to expect raw video from the pipe
               '-thread_queue_size', '128',
               # '-blocksize', '2048',
               '-i', config.video_pipe,  # tell ffmpeg to expect raw video from the pipe

               # '-c:a', 'libvorbis',
               # '-ac', '1',  # number of audio channels (mono1/stereo=2)
               # '-c:v', 'h264_videotoolbox',
               '-c:v', 'libx264',
               '-pix_fmt', 'yuv420p',
               # '-tune', 'animation',


               # ultrafast or zerolatency kinda makes audio and video out of sync when save to file (but stream to yt is kinda OK)
               # '-preset', 'ultrafast',
               # '-tune', 'zerolatency',

               # '-g', '150',  #  GOP: group of pictures
               '-g', str(keyframe_seconds * config.fps),  # GOP: group of pictures
               # '-g', str(config.fps // 2),  # GOP: group of pictures
               # '-x264opts', 'no-scenecut',
               # '-x264-params', f'keyint={keyframe_seconds * config.fps}:scenecut=0',
               '-vsync', 'cfr',
               # '-async', '1',
               # '-tag:v', 'hvc1', '-profile:v', 'main10',
               '-b:a', config.audio_bitrate,
               '-b:v', config.video_bitrate,
               '-deinterlace',
               # '-r', str(config.fps),

               '-r', str(config.fps),  # output framerate

               # '-blocksize', '2048',
               # '-flush_packets', '1',

               '-f', 'flv',
               '-flvflags', 'no_duration_filesize',
               # '-f', 'mp4',

               config.OUTPUT_VIDEO,
               )

        self.ffmpeg = subprocess.Popen(cmd)

        self.audio_seconds_written = 0.
        self.video_seconds_written = 0.
        self.frames_written = 0  # video
        self.samples_written = 0  # audio

        # self.audio_thread = GenerateAudioToPipe()
        # self.video_thread = GenerateVideoToPipe()
        qsize = 2 ** 9
        # qsize = 2 ** 4
        # qsize = 2 ** 6
        # qsize = 2 ** 8
        self.q_audio = queue.Queue(maxsize=qsize)
        self.q_video = queue.Queue(maxsize=qsize)
        # self.q_audio = collections.deque(maxlen=qsize)
        # self.q_video = collections.deque(maxlen=qsize)

        self.audio_thread = PipeWriter(config.audio_pipe, self.q_audio)
        self.video_thread = PipeWriter(config.video_pipe, self.q_video)
        self.audio_thread.start()
        self.video_thread.start()

        self.vbuff = io.BytesIO()

        # self.log = open(config.log_path, 'w')
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
        # self.log.close()

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
        # n_frames = int(seconds * config.fps)# - frames_written
        # print('fffffffffff', n_frames)

        # self.vbuff.truncate(0)
        # assert self.vbuff.getvalue() == b''
        # progress_color = 0, 255, 0, 100

        start_px = int(config.frame_width * self.n / self.track.n_samples)  # like n is for audio (progress on track), px is for video (progress on frame)
        chunk_width = int(config.frame_width * len(data) / self.track.n_samples)

        chord_length = config.frame_width / len(self.track.meta['progression'])
        frame_dx = chunk_width // n_frames

        x = start_px

        meta = self.track.meta

        for frame in range(n_frames):
            x += frame_dx

            # self.vbuff.write(layer.tobytes())
            # q_video.put(b, block=True)
            chord_i = int(x / chord_length)
            chord_start_px = int(chord_i * chord_length)

            chord = meta['progression'][chord_i]
            background_color = self.track.meta['scale'].note_colors[chord.root]

            # self.background_draw.rectangle((chord_start_px, 0, x + frame_dx, config.frame_height), fill=background_color)
            # self.background_draw = self.background_draw.draw_rect(background_color, chord_start_px, 0, x + frame_dx - chord_start_px, config.frame_height, fill=True)
            # self.background_draw = self.background_draw.draw_rect(background_color, chord_start_px, 0, x - chord_start_px, config.frame_height, fill=True)
            # ..method:: draw_rect(ink, left, top, width, height, fill=bool)

            # cv2.rectangle(im, pt1=(chord_start_px, 0), pt2=(x, config.frame_height), color=background_color, thickness=-1)
            cv2.rectangle(im, pt1=(chord_start_px, 0), pt2=(x, config.frame_height), color=background_color + (255,), thickness=-1)

            # for _ in range(1):
            # cv2.rectangle(im, pt1=util.random_xy(), pt2=util.random_xy(), color=util.random_color(), thickness=1)
            # cv2.rectangle(im, pt1=util.random_xy(), pt2=util.random_xy(), color=(0,0,0), thickness=1)

            cv2.putText(im, meta['bassline'], util.rel_to_abs(0, 0.07), font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(im, meta['rhythm_score'], util.rel_to_abs(0, 0.1), font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(im, meta['bass_decay'], util.rel_to_abs(0, 0.13), font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(im, meta['tuning'], util.rel_to_abs(0, 0.16), font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(im, meta['dist'], util.rel_to_abs(0, 0.19), font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(im, meta['root_scale'], util.rel_to_abs(0, 0.22), font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(im, f'sys.platform {sys.platform}', util.rel_to_abs(0, 0.25), font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(im, 'tandav.me', util.rel_to_abs(0, 0.9), font, fontScale=2, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)

            cv2.putText(im, meta['scale'].note_scales[chord.root], (chord_start_px, util.rel_to_abs_h(0.75)), font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(im, str(chord), (chord_start_px, util.rel_to_abs_h(0.8)), font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.putText(im, '*', util.random_xy(), font, fontScale=1, color=(0, 0, 0), thickness=1, lineType=cv2.LINE_AA)

            self.q_video.put(im.tobytes(), block=True)

        # q_video.put(self.vbuff.getvalue(), block=True)
        self.frames_written += n_frames
        self.video_seconds_written += n_frames / config.fps

        # print('eeeeeeeeeeeeeeeeee', f'QA{self.q_audio.qsize()} QV{self.q_video.qsize()} {len(data)=} {seconds=} {n_frames=} {self.samples_written:} {self.frames_written=} ASW{self.audio_seconds_written:.2f} VSW{self.video_seconds_written:.2f} {real_seconds=}')
        # print('eeeeeeeeeeeeeeeeee', f'QA{self.q_audio.__len__()} QV{self.q_video.__len__()} {len(data)=} {seconds=} {n_frames=} {self.samples_written:} {self.frames_written=} ASW{self.audio_seconds_written:.2f} VSW{self.video_seconds_written:.2f} {real_seconds=}')
        # info = {
        #     'timestamp': time.monotonic(),
        #     'qa': q_audio.qsize(),
        #     'qv': q_video.qsize(),
        #     'seconds': seconds,
        #     'n_frames': n_frames,
        #     'frames_written': frames_written,
        #     'samples_written': samples_written,
        #     'audio_seconds_written': audio_seconds_written,
        #     'video_seconds_written': video_seconds_written,
        # }
        # print(json.dumps(info), file=self.log)
