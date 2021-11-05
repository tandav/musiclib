from benchmark import pillow
from benchmark import vips

n_frames = 60 * 5


for backend in (vips, pillow):
    with open('logs/benchmark.jsonl', 'a') as log: print(backend.render(n_frames), file=log)
