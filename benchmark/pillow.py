import json
import random
import string
import sys
import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from benchmark.ffmpeg import make_ffmpeg
from musictools import config
from musictools import util


def render(n_frames):
    font = ImageFont.truetype('static/fonts/SFMono-Semibold.otf', 20)
    layer = Image.new('RGBA', (config.frame_width, config.frame_height), (255, 255, 255, 0))
    text_color = (0, 0, 0)

    background = Image.new('RGBA', layer.size, (200, 200, 200))
    background_draw = ImageDraw.Draw(background)

    meta = {
        'bassline': (util.rel_to_abs(0.28, 0), '101001010100101001'),
        'rhythm_score': (util.rel_to_abs(0, 0), '0.42'),
        'bass_decay': (util.rel_to_abs(0, 0.125), 'bass_decay0.42'),
        'chords': (util.rel_to_abs(0, 0.25), '\n'.join(str(i) * 8 for i in range(4))),
        'tuning': (util.rel_to_abs(0.47, 0.125), 'tuning440Hz'),
        'root_scale': (util.rel_to_abs(0, 0.66), 'root scale: C major'),
        'dist': (util.rel_to_abs(0.58, 0.25), 'dist42'),
        'website': (util.rel_to_abs(0, 0.83), 'tandav.me'),
        'platform': (util.rel_to_abs(0.47, 0.85), sys.platform),
    }

    colors = [util.hex_to_rgb(config.scale_colors[scale]) for scale in config.diatonic]
    chunk_width = config.frame_width
    frame_dx = chunk_width // n_frames
    x = 0
    chord_length = config.frame_width / 4
    t0 = time.time()

    with make_ffmpeg() as ffmpeg:
        for frame in range(n_frames):
            x += frame_dx
            chord_i = int(x / chord_length)
            chord_start_px = int(chord_i * chord_length)
            background_color = random.choice(colors)
            background_draw.rectangle((chord_start_px, 0, x + frame_dx, config.frame_height), fill=background_color)
            out = Image.alpha_composite(layer, background)
            q = ImageDraw.Draw(out)

            q.text(*meta['bassline'], font=font, fill=text_color)
            q.text(*meta['rhythm_score'], font=font, fill=text_color)
            q.text(*meta['bass_decay'], font=font, fill=text_color)
            q.text(*meta['chords'], font=font, fill=text_color)
            q.text(*meta['tuning'], font=font, fill=text_color)
            q.text(*meta['root_scale'], font=font, fill=text_color)
            q.text(*meta['dist'], font=font, fill=text_color)
            q.text(*meta['website'], font=font, fill=text_color)
            q.text(*meta['platform'], font=font, fill=text_color)
            q.text((chord_start_px, util.rel_to_abs_h(0.75)), 'scale', font=font, fill=text_color)
            q.text((random.randrange(config.frame_width), random.randrange(config.frame_height)), random.choice(string.ascii_letters), font=font, fill=text_color)
            ffmpeg.stdin.write(out.tobytes())

    dt = time.time() - t0
    fps = n_frames / dt
    speed = fps / config.fps
    return json.dumps({'backend': __name__.split('.')[1], 'dt': dt, 'fps': config.fps, 'actual_fps': fps, 'speed': speed, 'n_frames': n_frames, 'resolution': f'{config.frame_width}x{config.frame_height}', })
