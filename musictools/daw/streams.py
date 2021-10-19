import abc
import io
import itertools
import pickle
import random
import time

import errno
from threading import Thread

import collections
import numpy as np
import os
# from scipy.io import wavfile
from . import wavfile
# import matplotlib.pyplot as plt
import subprocess
import numpy as np
from musictools import config
from pathlib import Path

from .. import config


def float32_to_int16(signal: np.ndarray, dtype='int16'):
    """Convert floating point signal with a range from -1 to 1 to PCM.
    Any signal values outside the interval [-1.0, 1.0) are clipped.
    No dithering is used.
    Note that there are different possibilities for scaling floating
    point numbers to PCM numbers, this function implements just one of
    them.  For an overview of alternatives see
    http://blog.bjornroche.com/2009/12/int-float-int-its-jungle-out-there.html
    """
    if signal.dtype.kind != 'f':
        raise TypeError("'signal' must be a float array")
    dtype = np.dtype(dtype)
    if dtype.kind not in 'iu':
        raise TypeError("'dtype' must be an integer type")

    i = np.iinfo(dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (signal * abs_max + offset).clip(i.min, i.max).astype(dtype)


class Stream(abc.ABC):
    @abc.abstractmethod
    def write(self, data: np.ndarray):
        """data.dtype must be float32"""
        ...


class Bytes(Stream):
    def __enter__(self):
        return io.BytesIO()


class WavFile(Stream):
    def __init__(self, path, dtype='int16'):
        if dtype not in {'float32', 'int16'}:
            raise ValueError('unsupported wave format')
        self.path = path
        self.dtype = dtype

    def __enter__(self):
        # kinda workarounds, maybe there are a better ways
        # self.arrays = []
        self.stream = io.BytesIO()
        return self

    def write(self, data: np.ndarray):
        # self.arrays.append(data)
        self.stream.write(data.tobytes())

    def __exit__(self, type, value, traceback):
        # data = np.concatenate(self.arrays) # TODO: not works, fix it
        # assert data.dtype == 'float32'
        data = np.frombuffer(self.stream.getvalue(), dtype='float32')
        if self.dtype == 'int16':
            data = float32_to_int16(data)
        wavfile.write(self.path, config.sample_rate, data)


class PCM16File(Stream):
    """
    pcm_s16le PCM signed 16-bit little-endian
    """
    def __init__(self, path):
        self.path = open(path, 'wb')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.path.close()

    def write(self, data: np.ndarray):
        self.path.write(float32_to_int16(data).tobytes())
        # float32_to_int16(data).tofile(self.path)


class Speakers(Stream):
    def __enter__(self):
        import pyaudio
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=pyaudio.paFloat32, channels=1, rate=config.sample_rate, output=True)
        return self
        # return self.stream

    def __exit__(self, type, value, traceback):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    def write(self, data: np.ndarray):
        self.stream.write(data.tobytes())

# https://support.google.com/youtube/answer/6375112
frame_width = 426
frame_height = 240


import queue
# TODO: change to thread-safe queue.Queue
#   also compare speed of appendleft, pop vs append, popleft?
# audio_data = collections.deque()
audio_data = queue.Queue(maxsize=256)
video_data = queue.Queue(maxsize=256)
# video_data = collections.deque()
audio_finished = False
video_finished = False
no_more_data = False
audio_seconds_written = 0.
video_seconds_written = 0.
n_runs = 0
# class GenerateAudioToPipe(Thread):
#     def __init__(self):
#         super().__init__()
#         self._pipe_name = config.audio_pipe
#
#
#     def run(self):
#         global audio_finished
#         global audio_seconds_written
#         fd = open(self._pipe_name, 'wb')
#         # print('GenerateAudioToPipe')
#
#         # while not no_more_data or len(audio_data) > 0:
#         #     # print('1111111111111GenerateAudioToPipe')
#         #
#         #     if not audio_data:
#         #         # print('***********AUDIO', len(audio_data))
#         #         time.sleep(1)
#         #         continue
#         #
#         #     while audio_data:
#         #         # print('44444444444 AUDIO')
#         #         # b = audio_data.pop()
#         #         print(audio_data.qsize())
#         #         b = audio_data.get(block=True)
#         #         # print(b, b.tobytes()[:100])
#         #         fd.write(b.tobytes())
#         #         # print('5555555555')
#         #         audio_seconds_written += len(b) / config.sample_rate
#
#         while not no_more_data:
#             print(audio_data.qsize(), audio_seconds_written)
#             b = audio_data.get(block=True)
#             fd.write(b.tobytes())
#             audio_seconds_written += len(b) / config.sample_rate
#
#         fd.close()
#         print('IIIIIIIIIII')
#         audio_finished = True



# class GenerateVideoToPipe(Thread):
#     def __init__(self):
#         super().__init__()
#         self._pipe_name = config.video_pipe
#         with open('static/images.pkl', 'rb') as f:
#             self.images = pickle.load(f)
#
#     def run(self):
#         # global video_seconds_written
#         fd = open(self._pipe_name, 'wb')
#         frames_written = 0
#         video_seconds_written = 0
#         seconds_to_write = 0.
#
#         while not audio_finished or frames_written != int(audio_seconds_written * config.fps):
#
#             if frames_written == 0:
#                 n_frames = 30
#             else:
#                 n_frames = int(audio_seconds_written * config.fps) - frames_written
#
#             for frame in range(n_frames):
#                 b = random.choice(self.images).getvalue()
#                 fd.write(b)
#                 frames_written += 1
#             if n_frames != 0:
#                 print(frames_written, n_frames)
#             video_seconds_written += seconds_to_write
#         fd.close()


class PipeWriter(Thread):
    def __init__(self, pipe, q):
        super().__init__()
        self.pipe = pipe
        self.q = q

    def run(self):
        with open(self.pipe, 'wb') as pipe:
            # while True:
            while not audio_finished:
                print(self.pipe, 'lol')
                b = self.q.get(block=True)
                print(self.pipe, 'kek')
                pipe.write(b)
                self.q.task_done()

# def audio_thread():
#     with open(config.audio_pipe, 'wb') as pipe:
#         while True:
#             item = audio_data.get(block=True)
#             audio_data.task_done()
#
# def audio_thread():
#     with open(config.audio_pipe, 'wb') as pipe:
#         while True:
#             item = audio_data.get(block=True)
#             audio_data.task_done()



class YouTube(Stream):
    def __init__(self):
        """maybe move all to __enter__"""

        with open('static/images.pkl', 'rb') as f:
            self.images = pickle.load(f)

        def recreate(p):
            p = Path(p)
            if p.exists():
                p.unlink()
            os.mkfifo(p)

        recreate(config.audio_pipe)
        recreate(config.video_pipe)

        # INPUT_AUDIO = config.audio_pipe


        cmd = ('ffmpeg',
           '-loglevel', 'trace',
           # '-hwaccel', 'videotoolbox',
           # '-threads', '16',
           # '-y', '-r', '60', # overwrite, 60fps
           '-y',
           # '-r', str(config.fps),  # overwrite, 60fps

           '-s', f'{frame_width}x{frame_height}',  # size of image string
           '-f', 'rawvideo',
           '-pix_fmt', 'rgba',  # format
           # '-f', 'image2pipe',
           # '-i', 'pipe:', '-', # tell ffmpeg to expect raw video from the pipe
           # '-i', '-',  # tell ffmpeg to expect raw video from the pipe
           # '-i', f'pipe:{config.video_pipe}',  # tell ffmpeg to expect raw video from the pipe
           '-thread_queue_size', '1024',
           '-i', config.video_pipe,  # tell ffmpeg to expect raw video from the pipe

           "-f", 's16le',  # means 16bit input
           "-acodec", "pcm_s16le",  # means raw 16bit input
           '-r', "44100",  # the input will have 44100 Hz
           '-ac', '1',  # number of audio channels (mono1/stereo=2)
           # '-i', f'pipe:{config.audio_pipe}',
           '-thread_queue_size', '2048',
           '-i', config.audio_pipe,
           # '-b:a', "3000k",  # output bitrate (=quality). Here, 3000kb/second

           '-deinterlace',
           # '-c:v', 'hevc_videotoolbox',
           '-c:v', 'libx264',
           '-pix_fmt', 'yuv420p',
           # '-preset', 'ultrafast',

           # '-tag:v', 'hvc1', '-profile:v', 'main10',
           # '-b:v', '16M',
           # '-b:a', "100k",
           # '-b:v', '200k',
           # '-b:v', '100k',

           # '-framerate', '20',
           # '-maxrate', '1000k',

           # '-f', 'flv',
           # '-flvflags', 'no_duration_filesize',
           # 'rtmp://a.rtmp.youtube.com/live2/u0x7-vxkq-6ym4-s4qk-0acg',
           # f'rtmp://a.rtmp.youtube.com/live2/{os.environ["YOUTUBE_STREAM_KEY"]}',

           config.OUTPUT_VIDEO,  # output encoding
        )

        # self.ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        self.ffmpeg = subprocess.Popen(cmd)
        # self.p = None
        # time.sleep(5)
        # print(self.p)
        # print('2'* 100)

        # self.audio_thread = GenerateAudioToPipe()
        # self.video_thread = GenerateVideoToPipe()

        self.audio_thread = PipeWriter(config.audio_pipe, audio_data)
        self.video_thread = PipeWriter(config.video_pipe, video_data)
        self.audio_thread.start()
        self.video_thread.start()

        # self.audio_pipe = os.open(config.audio_pipe, os.O_WRONLY)
        # self.video_pipe = os.open(config.video_pipe, os.O_WRONLY)

        print('1'* 100)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        global audio_finished, video_finished, no_more_data
        audio_finished = True
        video_finished = True
        no_more_data = True

        self.audio_thread.join()
        self.video_thread.join()
        self.ffmpeg.wait()

        os.unlink(config.audio_pipe)
        os.unlink(config.video_pipe)

        # os.close(self.audio)
        # os.close(self.video)
        # self.path.close()

    def write(self, data: np.ndarray):
        global n_runs
        # global audio_seconds_written
        # audio_written, video_written = False, False

        # write audio samples
        # self.path.write(float32_to_int16(data).tobytes())
        # a = float32_to_int16(data)#.tobytes()
        # ab = os.write(self.audio, a)
        seconds = len(data) / config.sample_rate

        audio_data.put(data.tobytes(), block=True)
        n_frames = int(seconds * config.fps)# - frames_written
        assert n_frames > 0
        # print('fffffffffff', n_frames)
        print('eeeeeeeeeeeeeeeeee', audio_data.qsize(), video_data.qsize(), n_frames)

        for frame in range(n_frames):
            # print(n_frames)
            b = random.choice(self.images).getvalue()
            video_data.put(b, block=True)
        # if n_runs < 100:
        #     n_runs += 1
        #     return
        # # audio_data.appendleft(a)
        # # audio_data.put(a, block=True)
        # audio_data.join()
        # video_data.join()
