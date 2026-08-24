import asyncio
import httpx
import threading
import time
import re
import requests
from .api.auth import AuthAPI
from .api.rooms import RoomsAPI
from .database import Database

class Markdown:
    @staticmethod
    def bold(text): return f"**{text}**"
    @staticmethod
    def italic(text): return f"__{text}__"
    @staticmethod
    def code(text): return f"`{text}`"
    @staticmethod
    def spoiler(text): return f"||{text}||"
    @staticmethod
    def link(text, url): return f"[{text}]({url})"

YELLOW = "\033[93m"
RESET = "\033[0m"

class Bot:
    def __init__(self, token: str, base_url: str = "https://botapi.codemeet.chat"):
        self.token = token
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._http_client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=None
        )
        self.auth = AuthAPI(self._http_client, token)
        self.rooms = RoomsAPI(self._http_client, token, self.loop)
        self._handlers = {}
        self.db = Database()
        self._last_update_id = 0
        self._auto_task = None
        self._stop_auto = False
        self._stop = False
        self._paused = False
        self._input_thread = None
        self._ads_filter_enabled = False
        self._ads_pattern = re.compile(
            r'(https?://|www\.|t\.me/|@\w+|telegram\.me|bit\.ly|tinyurl\.com|'
            r'@[a-zA-Z0-9_]{4,}|[0-9]{5,}|joinchat|/join/|ads?|promo|'
            r'\b(?:ad|sponsor|buy now|click here|offer|discount|free)\b)',
            re.IGNORECASE
        )

    def _run(self, coro):
        return self.loop.run_until_complete(coro)

    def _trigger(self, event_name, data):
        for handler in self._handlers.get(event_name, []):
            handler(data)

    def message(self, func=None):
        def decorator(actual_func):
            self._handlers.setdefault("message", []).append(actual_func)
            return actual_func
        return decorator(func) if func else decorator

    def callback(self, func=None):
        def decorator(actual_func):
            self._handlers.setdefault("callback", []).append(actual_func)
            return actual_func
        return decorator(func) if func else decorator

    def send_message(self, chat_id, text, parse_mode="Markdown", reply_markup=None):
        result = self._run(self.rooms._send_message(chat_id, text, parse_mode, reply_markup))
        self._trigger("send_message", {"chat_id": chat_id, "text": text})
        return result

    def edit_message(self, chat_id, message_id, text, parse_mode="Markdown", reply_markup=None):
        return self._run(self.rooms._edit_message(chat_id, message_id, text, parse_mode, reply_markup))

    def delete_message(self, chat_id, message_id):
        return self._run(self.rooms._delete_message(chat_id, message_id))

    def reply_message(self, chat_id, message_id, text, parse_mode="Markdown"):
        return self._run(self.rooms._reply_message(chat_id, message_id, text, parse_mode))

    def send_photo(self, chat_id, photo, caption="", parse_mode="Markdown"):
        return self._run(self.rooms._send_photo(chat_id, photo, caption, parse_mode))

    def send_document(self, chat_id, document, caption="", parse_mode="Markdown"):
        return self._run(self.rooms._send_document(chat_id, document, caption, parse_mode))

    def set_my_commands(self, commands):
        return self._run(self.rooms._set_my_commands(commands))

    def ask_ai(self, prompt, system_prompt=""):
        url = f"https://api.pollinations.ai/prompt/{prompt}"
        if system_prompt:
            url += f"?system={system_prompt}"
        response = requests.get(url)
        return response.text

    def broadcast_message(self, text, parse_mode="Markdown"):
        chat_ids = self.db.get_all_chat_ids()
        sent_count = 0
        for chat_id in chat_ids:
            try:
                self.send_message(chat_id, text, parse_mode)
                sent_count += 1
            except Exception:
                pass
        return {"sent": sent_count, "total": len(chat_ids)}

    def send_to_user(self, user_id, text, parse_mode="Markdown"):
        if not self.db.user_exists(user_id):
            raise Exception("User not found")
        return self.send_message(user_id, text, parse_mode)

    def enable_ads_filter(self):
        self._ads_filter_enabled = True
        print("Ads filter enabled.")

    def disable_ads_filter(self):
        self._ads_filter_enabled = False
        print("Ads filter disabled.")

    def auto_send(self, interval, callback_func):
        def run_auto():
            while not self._stop_auto:
                time.sleep(interval)
                if self._stop_auto:
                    break
                result = callback_func()
                if result:
                    self.send_message(result["chat_id"], result["text"], result.get("parse_mode", "Markdown"))
        self._auto_task = threading.Thread(target=run_auto, daemon=True)
        self._auto_task.start()

    def stop_auto_send(self):
        self._stop_auto = True

    def _listen_input(self):
        while not self._stop:
            try:
                cmd = input(f"{YELLOW}bot Console >>>{RESET} ").strip().lower()
                if cmd == "bot.off()":
                    self.off()
                    break
                elif cmd == "bot.pause()":
                    self._paused = True
                    print("Bot paused.")
                elif cmd == "bot.on()":
                    if self._paused:
                        self._paused = False
                        print("Bot resumed.")
                    else:
                        print("Bot is already running!")
                elif cmd == "bot.filter.on()":
                    self.enable_ads_filter()
                elif cmd == "bot.filter.off()":
                    self.disable_ads_filter()
                elif cmd == "ask ":
                    prompt = cmd[4:].strip()
                    if prompt:
                        answer = self.ask_ai(prompt)
                        print(f"AI: {answer}")
                    else:
                        print("Usage: ask <question>")
                elif cmd.startswith("broadcast "):
                    msg = cmd[10:].strip()
                    if msg:
                        result = self.broadcast_message(msg)
                        print(f"Broadcast sent to {result['sent']} of {result['total']} users.")
                    else:
                        print("Usage: broadcast <message>")
                elif cmd.startswith("send "):
                    parts = cmd.split(" ", 2)
                    if len(parts) < 3:
                        print("Usage: send <user_id> <message>")
                        continue
                    user_id, msg = parts[1], parts[2].strip()
                    try:
                        self.send_to_user(user_id, msg)
                        print(f"Message sent to {user_id}.")
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print("Invalid command. Valid: bot.off(), bot.pause(), bot.on(), bot.filter.on(), bot.filter.off(), ask <question>, broadcast <message>, send <user_id> <message>")
            except EOFError:
                break

    def off(self):
        self._stop = True
        self.stop_auto_send()
        self._paused = False

    def _check_ads(self, text):
        return bool(self._ads_filter_enabled and self._ads_pattern.search(text))

    async def _get_updates(self, timeout=5):
        if self._paused:
            await asyncio.sleep(1)
            return []
        url = f"/bot{self.token}/getUpdates"
        params = {"timeout": timeout, "offset": self._last_update_id + 1}
        try:
            response = await self._http_client.get(url, params=params)
            if response.status_code == 200:
                return response.json().get("result", [])
        except Exception:
            return []
        return []

    def run(self, timeout=5):
        print(f"Bot {self.get_me()} is running...")
        print("Type 'bot.off()' to stop, 'bot.pause()' to pause, 'bot.on()' to resume.")
        print("Type 'ask <question>' to ask AI, 'broadcast <message>' to send to all, 'send <user_id> <message>' to send to one.")
        self._input_thread = threading.Thread(target=self._listen_input, daemon=True)
        self._input_thread.start()
        while not self._stop:
            updates = self._run(self._get_updates(timeout))
            for update in updates:
                if "message" in update:
                    msg = update["message"]
                    if msg.get("from", {}).get("is_bot", False) or msg.get("from", {}).get("username") == self.get_me():
                        self._last_update_id = update["update_id"]
                        continue
                    self._last_update_id = update["update_id"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    username = msg.get("from", {}).get("username", "Unknown")
                    if self._check_ads(text):
                        try:
                            self.delete_message(chat_id, msg["message_id"])
                            print(f"Deleted ad message from {username}: {text}")
                        except Exception:
                            pass
                    self.db.save_message(chat_id, text)
                    self._trigger("message", {"chat_id": chat_id, "text": text, "username": username})
                elif "callback_query" in update:
                    cb = update["callback_query"]
                    self._last_update_id = update["update_id"]
                    chat_id = cb["message"]["chat"]["id"]
                    message_id = cb["message"]["message_id"]
                    callback_data = cb.get("data", "")
                    username = cb.get("from", {}).get("username", "Unknown")
                    self._trigger("callback", {"chat_id": chat_id, "message_id": message_id, "data": callback_data, "username": username})
        self.close()
        print("Bot stopped.")

    def get_me(self):
        return self._run(self.auth._login())

    def close(self):
        self.stop_auto_send()
        self.db.close()
        self._run(self._http_client.aclose())
        self.loop.close()