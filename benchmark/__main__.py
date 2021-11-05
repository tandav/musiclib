from benchmark import pillow
from benchmark import vips
from musictools import config

n_frames = 60 * 5


for fps in 30, 60:
    config.fps = fps
    for w, h in [
        (426, 240),
        (640, 360),
        (854, 480),
        (1280, 720),
        (1920, 1080),
    ]:
        config.frame_width = w
        config.frame_height = h

        for backend in (vips, pillow):
            with open('logs/benchmark.jsonl', 'a') as log: print(backend.render(n_frames), file=log)
