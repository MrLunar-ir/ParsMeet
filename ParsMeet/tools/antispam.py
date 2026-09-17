import time

class AntiSpam:
    def __init__(self, max_messages=5, time_window=1):
        self.max_messages = max_messages
        self.time_window = time_window
        self.user_messages = {}

    def check(self, user_id):
        now = time.time()
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        self.user_messages[user_id] = [t for t in self.user_messages[user_id] if now - t < self.time_window]
        if len(self.user_messages[user_id]) >= self.max_messages:
            return False
        self.user_messages[user_id].append(now)
        return True