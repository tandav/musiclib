import concurrent.futures
import os
import queue
import time
from pathlib import Path

import numpy as np

from musictool import config
from musictool.daw.midi.parse.sounds import ParsedMidi
from musictool.daw.streams.base import Stream
from musictool.daw.streams.video import ffmpeg
from musictool.daw.streams.video.pipewriter import PipeWriter
from musictool.daw.streams.video.render import VideoRender
from musictool.util.signal import float32_to_int16

# from musictool.youtube.messages import YoutubeMessages

# https://support.google.com/youtube/answer/6375112
# https://support.google.com/youtube/answer/1722171
# https://support.google.com/youtube/answer/2853702 # streaming

# TODO: change to thread-safe queue.Queue
#   also compare speed of appendleft, pop vs append, popleft?

# im = np.ones(shape=(config.frame_height, config.frame_width, 4), dtype=np.uint8)

# piano = np.full(shape=(config.frame_height, config.frame_width, 4), fill_value=255, dtype=np.uint8)
# piano[:, :, :3] = 180
# black_white_pattern = itertools.cycle(bool(int(x)) for x in '010100101010')
# for x, is_black in zip(range(0, config.frame_width, config.key_width), black_white_pattern):
#     thickness = cv2.FILLED if is_black else 1
#     cv2.rectangle(piano, pt1=(x, 0), pt2=(x + config.key_width, config.frame_height), color=(0, 0, 0, 255), thickness=thickness)


class Video(Stream):

    def render_chunked(self, track: ParsedMidi, normalize=False):
        self.track = track
        n_frames = int((self.audio_seconds_written + track.seconds) * config.fps) - self.frames_written
        print(f'{n_frames=}')
        self.video_render = VideoRender(track, self.q_video, n_frames, self.render_pool)
        self.video_render.start()
        super().render_chunked(track, normalize)
        self.video_render.join()
        self.frames_written += n_frames

    def __enter__(self):
        def recreate(p):
            p = Path(p)
            if p.exists():
                p.unlink()
            os.mkfifo(p)

        recreate(config.audio_pipe)
        recreate(config.video_pipe)

        self.ffmpeg = ffmpeg.make_process(config.OUTPUT_VIDEO)

        self.audio_seconds_written = 0.
        self.video_seconds_written = 0.
        self.frames_written = 0  # video
        self.samples_written = 0  # audio
        # self.px_written = 0

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

        if config.OUTPUT_VIDEO.startswith('rtmp://'):
            # self.yt_messages = YoutubeMessages()
            # self.yt_messages.start()
            pass

        self.render_pool = concurrent.futures.ThreadPoolExecutor(max_workers=config.draw_threads)
        # self.render_pool = concurrent.futures.ProcessPoolExecutor(max_workers=config.draw_threads)
        # self.dt_hist = []
        self.t_start = time.time()
        return self

    def __exit__(self, type, value, traceback):
        self.audio_thread.stream_finished.set()
        self.video_thread.stream_finished.set()

        # if config.OUTPUT_VIDEO.startswith('rtmp://'):
        #     self.yt_messages.stream_finished.set()
        #     self.yt_messages.join()

        self.audio_thread.join()
        self.video_thread.join()

        self.render_pool.shutdown()
        self.ffmpeg.wait()

        os.unlink(config.audio_pipe)
        os.unlink(config.video_pipe)

        assert self.frames_written == int(self.audio_seconds_written * config.fps)
        print(self.frames_written, self.audio_seconds_written, int(self.audio_seconds_written * config.fps))

    # def make_frames(self, n_frames, px_width, len_data):
    #     # start_px = int(config.frame_height * self.n / self.track.n_samples)  # like n is for audio (progress on track), px is for video (progress on frame)
    #     # frame_dy = px_width // n_frames
    #     # frame_dn = len_data // n_frames
    #
    #     frame_dy = px_width / n_frames
    #     frame_dn = len_data / n_frames
    #     Y = np.arange(self.px_written, self.px_written + px_width, frame_dy)
    #     N = np.arange(self.n, self.n + len_data, frame_dn)
    #     # y = start_px
    #
    #     # Y = range(start_px, start_px + frame_dy * n_frames, frame_dy)
    #     # N = range(self.n, self.n + len_data, frame_dn)
    #     # with concurrent.futures.ThreadPoolExecutor() as pool:
    #
    #     # with concurrent.futures.ProcessPoolExecutor() as pool:
    #
    #     # t0 = time.time()
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=config.draw_threads) as pool:
    #         # return tuple(pool.map(self.make_frame, Y))
    #         # return tuple(pool.map(partial(make_frame, meta=self.track.meta, bg=self.bg, bg_bright=self.bg_bright), Y))
    #         args = [[y, n, self.track, self.bg, self.bg_bright, self.note_to_x, self.key_width, False] for y, n in zip(Y, N)]
    #         args[-1][-1] = True  # is_last_in_chunk
    #         # return tuple(pool.map(partial(make_frame, meta=self.track.meta, bg=self.bg, bg_bright=self.bg_bright), Y))
    #         return tuple(pool.map(make_frame, args))
    #
    #         # out = tuple(pool.map(make_frame, args))
    #     # dt = time.time() - t0
    #     # self.dt_hist.append(dt)
    #     # if random.random() < 0.05:
    #     #     print(np.array(self.dt_hist).mean())
    #     # print('dt', dt)
    #     # return out
    #     # frames = []
    #     # for frame in range(n_frames):
    #     #     y += frame_dy
    #     #     frames.append()
    #     # return frames

    def write(self, data: np.ndarray):
        len_data = len(data)
        seconds = len_data / config.sample_rate
        b = float32_to_int16(data).tobytes()

        # real_seconds = time.time() - self.t_start

        # if real_seconds < self.audio_seconds_written:
        # time.sleep(self.audio_seconds_written - real_seconds)

        self.q_audio.put(b, block=True)
        # self.q_audio.append(b)
        self.samples_written += len_data
        self.audio_seconds_written += seconds

        # n_frames = int(self.audio_seconds_written * config.fps) - self.frames_written
        # # assert n_frames > 0
        # # if n_frames == 0:
        # # if n_frames < 100:
        # if n_frames < config.video_queue_item_size:
        #     # if n_frames < 1:
        #     # if n_frames < 300:
        #     return
        # # print(n_frames)
        #
        # # px_width = int(self.audio_seconds_written * config.pxps) - self.px_written
        # px_width = seconds * config.pxps
        #
        #
        # #px_width = int(config.frame_height * len_data / self.track.n_samples)  # width of data in pixels
        # frames = self.make_frames(n_frames, px_width, len_data)
        # # n_frames = int(seconds * config.fps)# - frames_written
        # # print('fffffffffff', n_frames)
        #
        # for frame in frames:
        #     self.q_video.put(frame, block=True)
        #
        # # q_video.put(self.vbuff.getvalue(), block=True)
        # self.frames_written += n_frames
        # self.px_written += px_width
        # self.video_seconds_written += n_frames / config.fps

        # print('eeeeeeeeeeeeeeeeee', f'QA{self.q_audio.qsize()} QV{self.q_video.qsize()} {len(data)=} {seconds=} {n_frames=} {self.samples_written:} {self.frames_written=} ASW{self.audio_seconds_written:.2f} VSW{self.video_seconds_written:.2f} {real_seconds=}')
