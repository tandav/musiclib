import functools
import random
import time
from collections import deque
from threading import Event
from threading import Thread

from musictool import config

API_REQUESTS_QUOTA_PER_DAY = 10_000
SECONDS_IN_DAY = 60 * 60 * 24
# SECONDS_IN_DAY / QUOTA_PER_DAY # 8.64
API_TIME_LAG = 10  # only if 1 region, if 2 (US, RU) : use 20 seconds
# TIME_LAG = 60


def parse_chords(message_text: str):
    if not message_text.startswith('chords '):
        return
    prefix, space, chords = message_text.partition(' ')
    if space == '':
        return
    if len(chords) != config.bars_per_screen:
        return
    if any(c not in config.chromatic_notes for c in chords):
        return
    return chords


@functools.cache
def find_progression(chords: str):
    options = config.progressions_search_cache[chords]
    # options = [
    #     p for p in config.progressions
    #     if all(a == b.root for a, b in zip(chords, p[0]))
    # ]
    if len(options) == 0:
        return
    return random.choice(options)


class YoutubeMessages(Thread):
    def __init__(self):
        super().__init__()
        import credentials
        from musictool.youtube import api
        self.api = api
        self.api_key = credentials.api_key
        self.video_id = credentials.video_id
        self.liveChatId = self.api.get_liveChatId(self.video_id, self.api_key)
        print('YoutubeMessages')
        config.messages = deque(maxlen=5)
        self.stream_finished = Event()
        self.seen = set()
        self.sleep_time = API_TIME_LAG

    def run(self) -> None:
        while not self.stream_finished.is_set():
            messages, pollingIntervalMillis = self.api.get_chat_messages(self.liveChatId, self.api_key)
            todo = []
            for message in messages:
                if message['id'] not in self.seen:
                    if chords := parse_chords(message['text']):
                        if progression := find_progression(chords):
                            config.progressions_queue.append(progression)
                            message['text'] += f' QUEUED {len(config.progressions_queue)}'
                        else:
                            message['text'] += ' chords not found!'
                    todo.append(message)
                    print(message['displayName'], message['text'])
                    self.seen.add(message['id'])
            if todo:
                config.messages.extend(todo)
            # time.sleep(pollingIntervalMillis / 1e3)
            time.sleep(API_TIME_LAG)
