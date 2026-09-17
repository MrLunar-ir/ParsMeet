import time
import threading

class BroadcastQueue:
    def __init__(self, bot, delay=0.5):
        self.bot = bot
        self.delay = delay
        self._queue = []
        self._thread = None
        self._stop = False

    def add(self, chat_id, text, parse_mode="Markdown"):
        self._queue.append((chat_id, text, parse_mode))

    def add_many(self, chat_ids, text, parse_mode="Markdown"):
        for cid in chat_ids:
            self._queue.append((cid, text, parse_mode))

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True

    def _loop(self):
        while not self._stop:
            if not self._queue:
                time.sleep(0.5)
                continue
            chat_id, text, parse_mode = self._queue.pop(0)
            try:
                self.bot.send_message(chat_id, text, parse_mode)
            except Exception as e:
                print(f"Broadcast error: {e}")
            time.sleep(self.delay)

    def remaining(self):
        return len(self._queue)