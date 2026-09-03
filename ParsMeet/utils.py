from typing import Dict, List, Union, Any
import time

class KeyboardBuilder:
    @staticmethod
    def create(rows: List[List[Union[tuple, dict]]]) -> Dict:
        keyboard = []
        for row in rows:
            buttons = []
            for btn in row:
                if isinstance(btn, tuple) and len(btn) == 2:
                    buttons.append({"text": btn[0], "callback_data": btn[1]})
                elif isinstance(btn, dict):
                    buttons.append(btn)
            keyboard.append(buttons)
        return {"inline_keyboard": keyboard}

    @staticmethod
    def btn_menu(text: str) -> Dict:
        return {"text": text, "callback_data": "menu"}

    @staticmethod
    def btn_click_menu(text: str, action: str) -> Dict:
        return {"text": text, "callback_data": action}

class Conversation:
    def __init__(self, name: str, steps: List[str]):
        self.name = name
        self.steps = steps
        self.current_step: int = 0
        self.data: Dict[str, str] = {}

    def next_step(self, user_input: str):
        self.data[self.steps[self.current_step]] = user_input
        self.current_step += 1
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None

class Menu:
    def __init__(self, title: str, rows: List[List[Union[tuple, dict]]]):
        self.title = title
        self.rows = rows
        self.keyboard = KeyboardBuilder.create(rows)

    def send(self, bot: Any, chat_id: str) -> None:
        bot.send_message(chat_id, self.title, reply_markup=self.keyboard)

class Cache:
    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value, ttl=None):
        if ttl:
            self._data[key] = {"value": value, "expire": time.time() + ttl}
        else:
            self._data[key] = {"value": value, "expire": None}
        return value

    def delete(self, key):
        self._data.pop(key, None)

    def clear(self):
        self._data.clear()

    def is_expired(self, key):
        item = self._data.get(key)
        if not item:
            return True
        if item["expire"] is None:
            return False
        return time.time() > item["expire"]

class RateLimit:
    def __init__(self, max_requests=5, time_window=1):
        self.max_requests = max_requests
        self.time_window = time_window
        self._requests = {}

    def check(self, user_id):
        now = time.time()
        if user_id not in self._requests:
            self._requests[user_id] = []
        self._requests[user_id] = [t for t in self._requests[user_id] if now - t < self.time_window]
        if len(self._requests[user_id]) >= self.max_requests:
            return False
        self._requests[user_id].append(now)
        return True