import queue
from threading import Event
from threading import Thread


class PipeWriter(Thread):
    def __init__(self, pipe, q: queue.Queue):
        # def __init__(self, pipe, q: collections.deque):
        super().__init__()
        self.pipe = pipe
        self.q = q
        self.stream_finished = Event()
        # self.log = open(f'logs/{self.pipe}_log.jsonl', 'w')

    def run(self) -> None:
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
