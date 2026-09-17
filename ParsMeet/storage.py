import json
import os

class Storage:
    def __init__(self, path="parsmeet_storage.json"):
        self.path = path
        self._data = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _key(self, user_id, key):
        return f"{user_id}:{key}"

    def set(self, user_id, key, value):
        self._data[self._key(user_id, key)] = value
        self._save()

    def get(self, user_id, key, default=None):
        return self._data.get(self._key(user_id, key), default)

    def delete(self, user_id, key):
        self._data.pop(self._key(user_id, key), None)
        self._save()

    def increment(self, user_id, key, amount=1):
        current = self.get(user_id, key, 0)
        new = current + amount
        self.set(user_id, key, new)
        return new