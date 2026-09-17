import time

class ConversationMemory:
    def __init__(self, max_history=10, ttl=3600):
        self.max_history = max_history
        self.ttl = ttl
        self._memory = {}

    def add(self, user_id, role, content):
        self._cleanup()
        if user_id not in self._memory:
            self._memory[user_id] = {"history": [], "updated_at": time.time()}
        self._memory[user_id]["history"].append({"role": role, "content": content})
        self._memory[user_id]["history"] = self._memory[user_id]["history"][-self.max_history * 2:]
        self._memory[user_id]["updated_at"] = time.time()

    def get(self, user_id):
        self._cleanup()
        if user_id not in self._memory:
            return []
        return list(self._memory[user_id]["history"])

    def clear(self, user_id):
        self._memory.pop(user_id, None)

    def clear_all(self):
        self._memory.clear()

    def set_system(self, user_id, system_prompt):
        if user_id not in self._memory:
            self._memory[user_id] = {"history": [], "updated_at": time.time()}
        self._memory[user_id]["system"] = system_prompt

    def get_system(self, user_id):
        if user_id not in self._memory:
            return ""
        return self._memory[user_id].get("system", "")

    def _cleanup(self):
        now = time.time()
        expired = [uid for uid, m in self._memory.items() if now - m["updated_at"] > self.ttl]
        for uid in expired:
            del self._memory[uid]