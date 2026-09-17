import logging
import time

logger = logging.getLogger("ParsMeet")

class BaseMiddleware:
    def process(self, data):
        return data

class Logging(BaseMiddleware):
    def process(self, data):
        logger.info(f"Message from {data.get('username')}: {data.get('text')}")
        return data

class Recovery(BaseMiddleware):
    def process(self, data):
        return data

    def on_error(self, data, error):
        logger.error(f"Handler error: {error}")
        return True

class Timing(BaseMiddleware):
    def process(self, data):
        data["_start_time"] = time.time()
        return data

class AntiFlood(BaseMiddleware):
    def __init__(self, max_requests=5, window=1):
        self.max_requests = max_requests
        self.window = window
        self._users = {}

    def process(self, data):
        user_id = data.get("user_id", 0)
        now = time.time()
        if user_id not in self._users:
            self._users[user_id] = []
        self._users[user_id] = [t for t in self._users[user_id] if now - t < self.window]
        if len(self._users[user_id]) >= self.max_requests:
            data["_blocked"] = True
            return data
        self._users[user_id].append(now)
        data["_blocked"] = False
        return data