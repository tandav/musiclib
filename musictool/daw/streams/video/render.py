import sys
import threading

import cv2
import numpy as np

from musictool import config
from musictool.util import image as imageutil

font = cv2.FONT_HERSHEY_SIMPLEX

# bg = np.full(shape=(config.frame_height, config.frame_width, 4), fill_value=255, dtype=np.uint8)
bg = np.zeros((config.frame_height, config.frame_width, 4), dtype=np.uint8)
bg[:, :, -1] = 255


class VideoRender(threading.Thread):
    def __init__(self, track, q_video, n_frames: int, render_pool):
        super().__init__()
        self.track = track
        self.n_frames = n_frames
        self.key_width = config.frame_width // len(config.note_range)
        self.q_video = q_video
        self.render_pool = render_pool

    def run(self) -> None:

        self.extra_note_space = None
        if (extra_space := config.frame_width % self.key_width):
            extra_note = config.note_range[-1] + 1
            if extra_note.is_black:  # if it white there is nothing extra to do
                self.extra_note_space = extra_note, extra_space

        self.make_background(self.track)
        frame_dy = config.frame_height / self.n_frames

        # self.playing_notes = set()
        # self.releasing_notes = set()
        # self.done_notes = set()
        # self.drawn_not_complete_notes = set()

        self.notes_draw_done = set()

        Y = np.arange(0, config.frame_height, frame_dy)

        args = []
        for y in Y:
            done = set()
            notes_to_render = set()
            for note in self.track.notes - self.notes_draw_done:
                # if note.trackname == 'bass':
                # print('------>', note.trackname, note.sample_on)
                if note.px_on < y:
                    notes_to_render.add(note)
                    if not note.smooth_rendering:
                        done.add(note)
                if note.px_off <= y:  # maybe should be <
                    done.add(note)
            # print([(note.trackname, note.px_on) for note in done])
            # print([(note.trackname, note.px_on) for note in notes_to_render])
            self.notes_draw_done |= done
            args.append((y, self.track, self.bg, self.bg_bright, self.note_to_x, self.key_width, notes_to_render))
            # self.q_video.put(self.make_frame(y, self.track, self.bg, self.bg_bright, self.note_to_x, self.key_width, notes_to_render), block=True)

        for frame in self.render_pool.map(self.make_frame, args):
            self.q_video.put(frame)
            # self.q_video.put(frame, block=True)
            # self.frames_written += n_frames
            # self.px_written += px_width
            # self.video_seconds_written += n_frames / config.fps
        # t0 = time.time()
        # with concurrent.futures.ThreadPoolExecutor(max_workers=config.draw_threads) as pool:
            # return tuple(pool.map(self.make_frame, Y))
            # return tuple(pool.map(partial(make_frame, meta=self.track.meta, bg=self.bg, bg_bright=self.bg_bright), Y))
            # args = [[y, n, self.track, self.bg, self.bg_bright, self.note_to_x, self.key_width, False] for y, n in zip(Y, N)]
            # args[-1][-1] = True  # is_last_in_chunk
            # return tuple(pool.map(partial(make_frame, meta=self.track.meta, bg=self.bg, bg_bright=self.bg_bright), Y))
            # return tuple(pool.map(make_frame, args))

    def make_background(self, track):
        # self.piano = piano.copy()
        # self.progress = piano.copy()

        chord_rects = np.empty_like(bg)

        # self.bg = bg.copy()
        # overlay = bg.copy()
        chord_px_int = int(config.chord_px)
        for y, chord in zip(range(0, config.frame_height, chord_px_int), track.meta['progression']):
            background_color = track.meta['scale'].note_colors[chord.root]
            cv2.rectangle(chord_rects, pt1=(0, y), pt2=(config.frame_width, y + chord_px_int), color=background_color, thickness=cv2.FILLED)
            cv2.putText(chord_rects, f"{chord.root.name} {chord.abstract.name} | {track.meta['scale'].note_scales[chord.root]}", (imageutil.rel_to_abs_w(0.82), (y + imageutil.rel_to_abs_h(0.01))), font, fontScale=1, color=(210, 210, 210), thickness=2, lineType=cv2.LINE_AA, bottomLeftOrigin=True)

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
                thickness = 2 if note.abstract == 'B' else 1
                cv2.line(self.bg, (x + self.key_width, 0), (x + self.key_width, config.frame_height), (0, 0, 0, 255), thickness=thickness)

        if self.extra_note_space:
            extra_note, extra_space = self.extra_note_space
            x += self.key_width
            self.bg = imageutil.overlay_rect(self.bg, pt1=(x, 0), pt2=(x + extra_space, config.frame_height), color=(0, 0, 0), alpha=0.5)

        # vertical 16th grid
        for i, y in enumerate(np.arange(0, config.frame_height, config.frame_height / (16 * config.bars_per_screen)).astype(int)):
            thickness = 2 if i % 16 == 0 else 1
            cv2.line(self.bg, (0, y), (config.frame_width, y), (0, 0, 0, 50), thickness=thickness)

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

    # def make_frame(self, y, track, bg, bg_bright, note_to_x, key_width, notes_to_render):

    def make_frame(self, args):
        y, track, bg, bg_bright, note_to_x, key_width, notes_to_render = args
    # def make_frame(args):
    #     y, n, track, bg, bg_bright, note_to_x, key_width, is_last_in_chunk = args
        # print('zed')
        chord_i = int(y / config.chord_px)
        chord_start_px = int(chord_i * config.chord_px)
        chord = track.meta['progression'][chord_i]

        for note in notes_to_render:
            x0 = note_to_x[note.note]
            x1 = x0 + key_width
            y0 = note.px_on
            y1 = note.px_off - 1
            if note.smooth_rendering:
                y1 = min(y1, int(y))
            cv2.rectangle(bg_bright, pt1=(x0, y0), pt2=(x1, y1), color=note.color, thickness=cv2.FILLED)
            cv2.line(bg_bright, (x0, y0), (x1, y0), config.BLACK, thickness=1)

        # background_color = track.meta['scale'].note_colors[chord.root]

        # self.background_draw.rectangle((chord_start_px, 0, x + frame_dx, config.frame_height), fill=background_color)
        # self.background_draw = self.background_draw.draw_rect(background_color, chord_start_px, 0, x + frame_dx - chord_start_px, config.frame_height, fill=True)
        # self.background_draw = self.background_draw.draw_rect(background_color, chord_start_px, 0, x - chord_start_px, config.frame_height, fill=True)
        # ..method:: draw_rect(ink, left, top, width, height, fill=bool)

        # cv2.rectangle(im, pt1=(chord_start_px, 0), pt2=(x, config.frame_height), color=background_color, thickness=cv2.FILLED)
        # cv2.rectangle(self.progress, pt1=(0, chord_start_px), pt2=(config.frame_width, y), color=background_color, thickness=cv2.FILLED)

        # print(f'{len(track.drawn_not_complete_notes)=}')
        # w_space, w_bar = 2, 2

        # for note_sound in self.drawn_not_complete_notes:
        #     #y0 = int(note_sound.n_px - note_sound.px_rendered)
        #     y0 = int(note_sound.px_on)
        #     y1 = int(note_sound.px_off - 1)
        #
        #     # print(f'completing {note_sound.px_on=} {note_sound.px_off=} {note_sound.n_px=} {note_sound.px_rendered=} {y0=} {y1=}')
        #
        #     # x0 = note_to_x[note_sound.note]
        #     # x1 = x0 + key_width
        #
        #     x0 = note_to_x[note_sound.note]
        #     x1 = x0 + key_width
        #     bg_bright = imageutil.overlay_rect(bg_bright, pt1=(x0, y0), pt2=(x1, y1), color=note_sound.color, alpha=0.5)
        #     # cv2.rectangle(bg_bright, pt1=(x0, y0), pt2=(x1, y1), color=track.note_colors[note_sound], thickness=cv2.FILLED)
        #     cv2.line(bg_bright, (x0 - 1, y0), (x0 + 1, y0), (0, 255, 0, 255), thickness=1)
        #     note_sound.px_rendered = int(note_sound.px_off - note_sound.px_on)
        #
        # self.drawn_not_complete_notes.clear()
        # # with lock:
        # #     track.drawn_not_complete_notes.clear() # if many threads: can lead to  RuntimeError: Set changed size during iteration
        #
        # note_count = Counter()
        # for note_sound in self.playing_notes:
        #     y0 = int(note_sound.px_on)
        #     if y < y0:
        #         continue
        #     y1 = int(min(note_sound.px_off - 1, y))
        #     # print(y, y1)
        #     note_count[note_sound.note]  += 1
        #     w_space = 2
        #     w_bar = 2
        #     w = (w_bar + w_space) * note_count[note_sound.note]
        #
        #     # x0 = note_to_x[note_sound.note] - w
        #     # x1 = x0 + w_bar
        #     x0 = note_to_x[note_sound.note]
        #     x1 = x0 + key_width
        #
        #
        #     # y0 = config.frame_height * note_sound.sample_on // track.n_samples
        #     # y0 = note_sound.px_on
        #
        #     # if note_sound.note == SpecificNote('f', 3):
        #     #     print(note_sound.px_on, note_sound.px_off)
        #     # print(x0, y0, y0, y1, track.note_colors[note_sound])
        #
        #     # cv2.rectangle(bg_bright, pt1=(x0, y0), pt2=(x1, min(y, note_sound.px_off)), color=config.WHITE, thickness=cv2.FILLED)
        #     # cv2.line(bg_bright, (x0, y0), (x1, y0), config.BLACK, thickness=1)
        #     bg_bright = imageutil.overlay_rect(bg_bright, pt1=(x0, y0), pt2=(x1, y1), color=note_sound.color, alpha=0.5)
        #     # cv2.rectangle(bg_bright, pt1=(x0, y0), pt2=(x1, y1), color=track.note_colors[note_sound], thickness=cv2.FILLED)
        #     cv2.line(bg_bright, (x0 - 1, y0), (x0 + 1, y0), (0, 255, 0, 255), thickness=1)
        #     note_sound.px_rendered += y1 - y0

        # for note in chord.notes_ascending:
        #     cv2.rectangle(bg_bright, pt1=(note_to_x[note], chord_start_px), pt2=(note_to_x[note] + key_width, y), color=background_color, thickness=cv2.FILLED)

        # if is_last_in_chunk:
        #     cv2.line(bg_bright, (0, y), (config.frame_width, y), config.WHITE, thickness=1)

        # cv2.rectangle(bg_bright, pt1=(0, chord_start_px), pt2=(config.frame_width, y), color=background_color, thickness=cv2.FILLED)

        im = imageutil.overlay_image(bg, bg_bright, alpha=1.0)
        im = cv2.flip(im, 0)
        for note in chord.notes_ascending:
            cv2.putText(im, repr(note), (note_to_x[note], config.frame_height - (chord_start_px + imageutil.rel_to_abs_h(0.007))), font, fontScale=0.75, color=config.BLACK, thickness=1, lineType=cv2.LINE_AA)

        for note in chord.root_specific:
            cv2.putText(im, 'r', (note_to_x[note], config.frame_height - (chord_start_px + imageutil.rel_to_abs_h(0.03))), font, fontScale=0.75, color=config.BLACK, thickness=1, lineType=cv2.LINE_AA)

        # print('kek')
        # for _ in range(1):
        # cv2.rectangle(im, pt1=util.random_xy(), pt2=util.random_xy(), color=util.random_color(), thickness=1)
        # cv2.rectangle(im, pt1=util.random_xy(), pt2=util.random_xy(), color=(0,0,0), thickness=1)

        cv2.putText(im, track.meta['message'], imageutil.rel_to_abs(0, 0.03), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, track.meta['bassline'], imageutil.rel_to_abs(0, 0.07), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, track.meta['rhythm_score'], imageutil.rel_to_abs(0, 0.1), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, track.meta['bass_decay'], imageutil.rel_to_abs(0, 0.13), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, track.meta['tuning'], imageutil.rel_to_abs(0, 0.16), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, track.meta['dist'], imageutil.rel_to_abs(0, 0.19), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, track.meta['root_scale'], imageutil.rel_to_abs(0, 0.22), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, f'sys.platform {sys.platform}', imageutil.rel_to_abs(0, 0.25), font, fontScale=1, color=(config.WHITE), thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, f'bpm {config.beats_per_minute}', imageutil.rel_to_abs(0, 0.28), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, f'sample_rate {config.sample_rate}', imageutil.rel_to_abs(0, 0.31), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, f'fps {config.fps}', imageutil.rel_to_abs(0, 0.34), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, f'draw_threads {config.draw_threads}', imageutil.rel_to_abs(0, 0.37), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, f'chunk_size {config.chunk_size}', imageutil.rel_to_abs(0, 0.4), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, f'GOP {config.gop}', imageutil.rel_to_abs(0, 0.43), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, f'keyframe_seconds {config.keyframe_seconds}', imageutil.rel_to_abs(0, 0.46), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, f'quality {config.frame_height}p', imageutil.rel_to_abs(0, 0.49), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)

        cv2.putText(im, f"{chord.root.name} {chord.abstract.name} | {track.meta['scale'].note_scales[chord.root]}", (imageutil.rel_to_abs_w(0.82), config.frame_height - (chord_start_px + imageutil.rel_to_abs_h(0.01))), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)

        if not track.meta['muted']['closed_hat']:
            for _ in range(2):
                cv2.putText(im, '*', imageutil.random_xy(), font, fontScale=1, color=config.WHITE, thickness=1, lineType=cv2.LINE_AA)
        cv2.putText(im, 'tandav.me', imageutil.rel_to_abs(0.8, 0.07), font, fontScale=2, color=config.BLACK, thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(im, 'tandav.me', imageutil.rel_to_abs(0.802, 0.072), font, fontScale=2, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)

        h = imageutil.rel_to_abs_h(0.5)

        for message in list(config.messages):
            ph, pw = h, 0
            profileImage = message['profileImage']
            im[ph:ph + profileImage.shape[0], pw:pw + profileImage.shape[1]] = profileImage
            h += 30
            cv2.putText(im, message['displayName'], (profileImage.shape[0], h), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
            # h += 0.03
            h += imageutil.rel_to_abs_h(0.03)
            cv2.putText(im, message['text'], (profileImage.shape[0], h), font, fontScale=1, color=config.WHITE, thickness=2, lineType=cv2.LINE_AA)
            # h += 0.04
            h += profileImage.shape[0] // 2

        return im.tobytes()
