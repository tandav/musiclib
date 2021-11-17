import time
from collections import deque
from threading import Event
from threading import Thread

from musictools import config

API_REQUESTS_QUOTA_PER_DAY = 10_000
SECONDS_IN_DAY = 60 * 60 * 24
# SECONDS_IN_DAY / QUOTA_PER_DAY # 8.64
API_TIME_LAG = 10  # only if 1 region, if 2 (US, RU) : use 20 seconds
# TIME_LAG = 60


class YoutubeMessages(Thread):
    def __init__(self):
        super().__init__()
        import credentials
        from musictools.youtube import api
        self.api = api
        self.api_key = credentials.api_key
        self.video_id = credentials.video_id
        print('YoutubeMessages')
        config.messages = deque(maxlen=5)
        self.stream_finished = Event()
        self.seen = set()
        self.sleep_time = API_TIME_LAG

    def run(self) -> None:
        while not self.stream_finished.is_set():
            liveChatId = self.api.get_liveChatId(self.video_id, self.api_key)
            messages, pollingIntervalMillis = self.api.get_chat_messages(liveChatId, self.api_key)

            todo = []
            for message in messages:
                if message['id'] not in self.seen:
                    todo.append(message)
                    self.seen.add(message['id'])
            # print(messages, pollingIntervalMillis)
            print(todo)
            config.messages.extend(todo)
            # time.sleep(pollingIntervalMillis / 1e3)
            time.sleep(API_TIME_LAG)
