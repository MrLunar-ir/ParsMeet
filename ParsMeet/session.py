import time

class Session:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.data = {}
        self.step = None
        self.created_at = time.time()

    def set(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def clear(self):
        self.data.clear()
        self.step = None

class SessionManager:
    def __init__(self, ttl=3600):
        self.sessions = {}
        self.ttl = ttl

    def get(self, chat_id):
        self._cleanup()
        if chat_id not in self.sessions:
            self.sessions[chat_id] = Session(chat_id)
        return self.sessions[chat_id]

    def delete(self, chat_id):
        self.sessions.pop(chat_id, None)

    def _cleanup(self):
        now = time.time()
        expired = [cid for cid, s in self.sessions.items() if now - s.created_at > self.ttl]
        for cid in expired:
            del self.sessions[cid]