import time

class Cooldown:
    def __init__(self, seconds=3):
        self.seconds = seconds
        self._last = {}

    def check(self, user_id):
        now = time.time()
        last = self._last.get(user_id, 0)
        if now - last < self.seconds:
            return False
        self._last[user_id] = now
        return True

    def remaining(self, user_id):
        now = time.time()
        last = self._last.get(user_id, 0)
        return max(0, self.seconds - (now - last))