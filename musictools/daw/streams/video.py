import io
import os
import queue
import random
import string
import subprocess
import sys
import time
from pathlib import Path
from threading import Event
from threading import Thread

import numpy as np
import pyvips
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from musictools import config
from musictools import util
from musictools.daw.midi.parse import ParsedMidi
from musictools.daw.streams.base import Stream

# https://support.google.com/youtube/answer/6375112
# https://support.google.com/youtube/answer/1722171

# TODO: change to thread-safe queue.Queue
#   also compare speed of appendleft, pop vs append, popleft?


font = ImageFont.truetype('static/fonts/SFMono-Semibold.otf', 30)
font2 = ImageFont.truetype('static/fonts/SFMono-Regular.otf', 20)
layer = Image.new('RGBA', (config.frame_width, config.frame_height), (255, 255, 255, 0))
text_color = (0, 0, 0)
d = ImageDraw.Draw(layer)
bg = pyvips.Image.black(config.frame_width, config.frame_height, bands=3)


class PipeWriter(Thread):
    def __init__(self, pipe, q: queue.Queue):
        super().__init__()
        self.pipe = pipe
        self.q = q
        self.stream_finished = Event()
        # self.log = open(f'logs/{self.pipe}_log.jsonl', 'w')

    def run(self):
        with open(self.pipe, 'wb') as pipe:
            while not self.stream_finished.is_set() or not self.q.empty():
                # print(self.pipe, self.q.empty(), self.stream_finished.is_set(), 'foo')
                # if self.pipe == config.video_pipe: print(self.pipe, self.q.qsize(), 'lol')
                # print(json.dumps({'timestamp': time.monotonic(), 'writer': self.pipe, 'event': 'write_start', 'qsize': self.q.qsize()}), file=self.log)

                # you can't block w/o timeout because stream_finished event may be set at any time
                try:
                    b = self.q.get(block=True, timeout=0.01)
                except queue.Empty:
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
        # self.background_draw.rectangle((0, 0, config.frame_width, config.frame_height), fill=(200, 200, 200))
        self.background_draw = self.background_draw.draw_rect((200, 200, 200), 0, 0, config.frame_width, config.frame_height, fill=True)

    def __enter__(self):
        # with open('static/images_backup.pkl', 'rb') as f: self.images = [i.getvalue() for i in pickle.load(f)]
        # with open('static/images.pkl', 'rb') as f: self.images = pickle.load(f)

        def recreate(p):
            p = Path(p)
            if p.exists():
                p.unlink()
            os.mkfifo(p)

        recreate(config.audio_pipe)
        recreate(config.video_pipe)

        # INPUT_AUDIO = config.audio_pipe

        # thread_queue_size = str(2**16)
        thread_queue_size = str(2**10)
        # thread_queue_size = str(2**5)
        # thread_queue_size = str(2 ** 8)
        keyframe_seconds = 3

        cmd = ('ffmpeg',
               # '-loglevel', 'trace',
               # '-hwaccel', 'videotoolbox',
               # '-threads', '2',
               # '-threads', '7',
               # '-y', '-r', '60', # overwrite, 60fps
               '-re',
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
               # '-r', str(config.fps),
               '-r', str(config.fps),  # input framrate. This parameter is important to stream w/o memory overflow
               # '-vsync', 'cfr', # kinda optional but you can turn it on
               # '-f', 'image2pipe',
               # '-i', 'pipe:', '-', # tell ffmpeg to expect raw video from the pipe
               # '-i', '-',  # tell ffmpeg to expect raw video from the pipe
               '-thread_queue_size', thread_queue_size,
               # '-blocksize', '2048',
               '-i', config.video_pipe,  # tell ffmpeg to expect raw video from the pipe

               # '-c:a', 'libvorbis',
               # '-ac', '1',  # number of audio channels (mono1/stereo=2)
               # '-b:a', "320k",  # output bitrate (=quality). Here, 3000kb/second
               # '-c:v', 'h264_videotoolbox',
               '-c:v', 'libx264',
               '-pix_fmt', 'yuv420p',
               # '-preset', 'ultrafast',
               # '-tune', 'zerolatency',
               # '-tune', 'animation',

               # '-g', '150',  #  GOP: group of pictures
               '-g', str(keyframe_seconds * config.fps),  # GOP: group of pictures
               # '-x264opts', 'no-scenecut',
               # '-x264-params', f'keyint={keyframe_seconds * config.fps}:scenecut=0',
               '-vsync', 'cfr',
               # '-async', '1',
               # '-tag:v', 'hvc1', '-profile:v', 'main10',
               # '-b:v', '16M',
               # '-b:a', "300k",
               '-b:a', '128k',
               # '-b:v', '64k',
               '-b:v', config.video_bitrate,
               # '-b:v', '12m',
               '-deinterlace',
               # '-r', str(config.fps),

               '-r', str(config.fps),  # output framerate
               # '-maxrate', '1000k',
               # '-map', '0:a',
               # '-map', '1:v',

               # '-b', '400k', '-minrate', '400k', '-maxrate', '400k', '-bufsize', '1835k',
               # '-b', '400k', '-minrate', '400k', '-maxrate', '400k', '-bufsize', '300m',

               # '-blocksize', '2048',
               # '-flush_packets', '1',
               '-f', 'flv',
               '-flvflags', 'no_duration_filesize',
               config.OUTPUT_VIDEO,
               )

        # self.ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        self.ffmpeg = subprocess.Popen(cmd)
        # self.p = None
        # time.sleep(5)
        # print(self.p)
        # print('2'* 100)

        self.audio_seconds_written = 0.
        self.video_seconds_written = 0.
        self.frames_written = 0  # video
        self.samples_written = 0  # audio

        # self.audio_thread = GenerateAudioToPipe()
        # self.video_thread = GenerateVideoToPipe()
        # qsize = 2 ** 9
        # qsize = 2 ** 4
        # qsize = 2 ** 6
        qsize = 2 ** 8
        self.q_audio = queue.Queue(maxsize=qsize)
        self.q_video = queue.Queue(maxsize=qsize)

        self.audio_thread = PipeWriter(config.audio_pipe, self.q_audio)
        self.video_thread = PipeWriter(config.video_pipe, self.q_video)
        self.audio_thread.start()
        self.video_thread.start()

        self.vbuff = io.BytesIO()

        # time.sleep(2)
        # print('sfsfsf')
        # self.audio_pipe = os.open(config.audio_pipe, os.O_WRONLY | os.O_NONBLOCK)
        # print('qq')
        # self.video_pipe = os.open(config.video_pipe, os.O_WRONLY | os.O_NONBLOCK)

        # self.background = Image.new('RGBA', layer.size, (200, 200, 200))
        # self.background_draw = ImageDraw.Draw(self.background)
        self.background_draw = pyvips.Image.black(config.frame_width, config.frame_height, bands=3)

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
        """
        TODO:
            track speed of audio generating here
            (timie.time, local fps)
            dont generate more if there's no need
        """

        # global n_runs
        # global audio_seconds_written
        # global video_seconds_written
        # global frames_written
        # global samples_written

        seconds = len(data) / config.sample_rate
        b = util.float32_to_int16(data).tobytes()

        real_seconds = time.time() - self.t_start
        if real_seconds < self.audio_seconds_written:
            # print('sleeping for', audio_seconds_written - real_seconds)
            # time.sleep(self.audio_seconds_written - real_seconds)
            pass
        # audio_written, video_written = False, False

        # write audio samples
        # self.path.write(float32_to_int16(data).tobytes())
        # a = float32_to_int16(data)#.tobytes()
        # ab = os.write(self.audio, a)

        # print('XG', len(b))
        # os.write(self.audio_pipe, b)
        # print('VVS')
        self.q_audio.put(b, block=True)
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

        for frame in range(n_frames):
            x += frame_dx

            # d.rectangle((0, 0, config.frame_width, config.frame_height), fill=(200, 200, 200))
            # im = bg.draw_rect((200, 200, 200), 0, 0, config.frame_width, config.frame_height, fill=True)
            # print(chord_length * chord_i, self.n * config.frame_width // self.track.n_samples - chord_length * chord_i)

            # self.vbuff.write(random.choice(self.images))
            # self.vbuff.write(layer.tobytes())
            # q_video.put(b, block=True)
            chord_i = int(x / chord_length)
            chord_start_px = int(chord_i * chord_length)

            chord = self.track.meta['progression'][chord_i]
            background_color = self.track.meta['scale'].note_colors[chord.root]
            scale = self.track.meta['scale'].note_scales[chord.root]

            # self.background_draw.rectangle((chord_start_px, 0, x + frame_dx, config.frame_height), fill=background_color)
            # self.background_draw = self.background_draw.draw_rect(background_color, chord_start_px, 0, x + frame_dx - chord_start_px, config.frame_height, fill=True)
            self.background_draw = self.background_draw.draw_rect(background_color, chord_start_px, 0, x - chord_start_px, config.frame_height, fill=True)
            # ..method:: draw_rect(ink, left, top, width, height, fill=bool)

            # out = Image.alpha_composite(layer, self.background)
            out = (
                bg.composite2(self.background_draw, pyvips.enums.BlendMode.OVER, x=0, y=0)
                .insert(pyvips.Image.text(self.track.meta['bassline']), *util.rel_to_abs(0.28, 0))
                .insert(pyvips.Image.text(f"score{self.track.meta['rhythm_score']}"), *util.rel_to_abs(0, 0))
                .insert(pyvips.Image.text(self.track.meta['chords']), *util.rel_to_abs(0, 0.25))
                .insert(pyvips.Image.text(f"dist{self.track.meta['dist']}"), *util.rel_to_abs(0.58, 0.25))
                .insert(pyvips.Image.text(f"root scale: {self.track.meta['scale'].root.name} {self.track.meta['scale'].name}"), *util.rel_to_abs(0, 0.66))
                .insert(pyvips.Image.text(scale), chord_start_px, util.rel_to_abs_h(0.75))
                .insert(pyvips.Image.text(f"bass_decay{self.track.meta['bass_decay']}"), *util.rel_to_abs(0, 0.125))
                .insert(pyvips.Image.text(f'tuning{config.tuning}Hz'), *util.rel_to_abs(0.47, 0.125))
                .insert(pyvips.Image.text('tandav.me'), *util.rel_to_abs(0, 0.83))
                .insert(pyvips.Image.text(sys.platform), *util.rel_to_abs(0.47, 0.85))
                .insert(pyvips.Image.text(random.choice(string.ascii_letters)), random.randrange(config.frame_width), random.randrange(config.frame_height))
            )

            # q = ImageDraw.Draw(out)

            # q.text(util.rel_to_abs(0.28, 0), self.track.meta['bassline'], font=font, fill=text_color)
            # q.text(util.rel_to_abs(0, 0), f"score{self.track.meta['rhythm_score']}", font=font2, fill=text_color)
            # q.text(util.rel_to_abs(0, 0.25), self.track.meta['chords'], font=font2, fill=text_color)
            # q.text(util.rel_to_abs(0.58, 0.25), f"dist{self.track.meta['dist']}", font=font2, fill=text_color)
            # q.text(util.rel_to_abs(0, 0.66), f"root scale: {self.track.meta['scale'].root.name} {self.track.meta['scale'].name}", font=font2, fill=text_color)
            # q.text((chord_start_px, util.rel_to_abs_h(0.75)), scale, font=font2, fill=text_color)
            # q.text(util.rel_to_abs(0, 0.125), f"bass_decay{self.track.meta['bass_decay']}", font=font2, fill=text_color)
            # q.text(util.rel_to_abs(0.47, 0.125), f'tuning{config.tuning}Hz', font=font2, fill=text_color)
            # q.text(util.rel_to_abs(0, 0.83), 'tandav.me', font=font, fill=text_color)
            # q.text(util.rel_to_abs(0.47, 0.85), sys.platform, font=font2, fill=text_color)

            # q.text((random.randrange(config.frame_width), random.randrange(config.frame_height)), random.choice(string.ascii_letters), font=font, fill=text_color)

            # q_video.put(random.choice(self.images), block=True)
            # self.q_video.put(out.tobytes(), block=True)
            self.q_video.put(out.write_to_memory(), block=True)

        # q_video.put(b''.join(random.choices(self.images, k=n_frames)), block=True)
        # q_video.put(self.vbuff.getvalue(), block=True)
        self.frames_written += n_frames
        self.video_seconds_written += n_frames / config.fps

        print('eeeeeeeeeeeeeeeeee', f'QA{self.q_audio.qsize()} QV{self.q_video.qsize()} {len(data)=} {seconds=} {n_frames=} {self.samples_written:} {self.frames_written=} ASW{self.audio_seconds_written:.2f} VSW{self.video_seconds_written:.2f} {real_seconds=}')
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
