import time

class KeyboardBuilder:
    @staticmethod
    def create(rows):
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
    def btn_menu(text="Menu"):
        return {"text": text, "callback_data": "menu"}

    @staticmethod
    def btn_click_menu(text, action):
        return {"text": text, "callback_data": action}

class Menu:
    def __init__(self, title, rows):
        self.title = title
        self.rows = rows
        self.keyboard = KeyboardBuilder.create(rows)

    def send(self, bot, chat_id):
        bot.send_message(chat_id, self.title, reply_markup=self.keyboard)

class Cache:
    def __init__(self):
        self._data = {}

    def get(self, key):
        item = self._data.get(key)
        if not item:
            return None
        if item["expire"] and time.time() > item["expire"]:
            del self._data[key]
            return None
        return item["value"]

    def set(self, key, value, ttl=None):
        expire = time.time() + ttl if ttl else None
        self._data[key] = {"value": value, "expire": expire}
        return value

    def delete(self, key):
        self._data.pop(key, None)

    def clear(self):
        self._data.clear()

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