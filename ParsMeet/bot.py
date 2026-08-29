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
    def bold(text):
        return f"**{text}**"
    @staticmethod
    def italic(text):
        return f"__{text}__"
    @staticmethod
    def code(text):
        return f"`{text}`"
    @staticmethod
    def spoiler(text):
        return f"||{text}||"
    @staticmethod
    def link(text, url):
        return f"[{text}]({url})"

YELLOW = "\033[93m"
RESET = "\033[0m"

class Bot:
    def __init__(self, token, base_url="https://botapi.codemeet.chat", ai_key=None):
        self.token = token
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._http = httpx.AsyncClient(base_url=base_url, headers={"Authorization": f"Bearer {token}"}, timeout=None)
        self.auth = AuthAPI(self._http, token)
        self.rooms = RoomsAPI(self._http, token, self.loop)
        self.db = Database()
        self._handlers = {}
        self._last_update = 0
        self._stop = False
        self._paused = False
        self._ads_on = False
        self._ads_pattern = re.compile(r'(https?://|@\w+|telegram\.me|bit\.ly|tinyurl\.com|ads?|promo|discount|free)', re.I)
        self.ai_key = ai_key
        self.ai_model = "gpt-3.5-turbo"

    def _run(self, coro):
        return self.loop.run_until_complete(coro)

    def _fire(self, event, data):
        for cb in self._handlers.get(event, []):
            cb(data)

    def on_message_all(self, func=None):
        def wrap(f):
            self._handlers.setdefault("message", []).append(f)
            return f
        return wrap(func) if func else wrap

    def on_callback_query(self, func=None):
        def wrap(f):
            self._handlers.setdefault("callback", []).append(f)
            return f
        return wrap(func) if func else wrap

    def on_askai(self, func=None):
        def wrap(f):
            self._handlers.setdefault("askai", []).append(f)
            return f
        return wrap(func) if func else wrap

    def create_callback(self, text, data):
        return {"text": text, "callback_data": data}

    def send_message(self, chat_id, text, parse_mode="Markdown", reply_markup=None):
        return self._run(self.rooms._send_message(chat_id, text, parse_mode, reply_markup))

    def reply_message(self, chat_id, msg_id, text, parse_mode="Markdown"):
        return self._run(self.rooms._reply_message(chat_id, msg_id, text, parse_mode))

    def edit_message(self, chat_id, msg_id, text, parse_mode="Markdown", reply_markup=None):
        return self._run(self.rooms._edit_message(chat_id, msg_id, text, parse_mode, reply_markup))

    def delete_message(self, chat_id, msg_id):
        return self._run(self.rooms._delete_message(chat_id, msg_id))

    def send_photo(self, chat_id, photo, caption=""):
        return self._run(self.rooms._send_photo(chat_id, photo, caption))

    def send_document(self, chat_id, doc, caption=""):
        return self._run(self.rooms._send_document(chat_id, doc, caption))

    def ban_user(self, chat_id, user_id):
        return self._run(self.rooms._ban_user(chat_id, user_id))

    def unban_user(self, chat_id, user_id):
        return self._run(self.rooms._unban_user(chat_id, user_id))

    def promote_user(self, chat_id, user_id):
        return self._run(self.rooms._promote_user(chat_id, user_id))

    def demote_user(self, chat_id, user_id):
        return self._run(self.rooms._demote_user(chat_id, user_id))

    def pin_message(self, chat_id, msg_id):
        return self._run(self.rooms._pin_message(chat_id, msg_id))

    def set_commands(self, commands):
        return self._run(self.rooms._set_my_commands(commands))

    def ask_ai(self, prompt, system_prompt=""):
        if self.ai_key:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.ai_key}", "Content-Type": "application/json"}
            data = {
                "model": self.ai_model,
                "messages": [
                    {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500
            }
            try:
                resp = requests.post(url, headers=headers, json=data, timeout=30)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"].strip()
                return f"Error: {resp.status_code} - {resp.text}"
            except Exception as e:
                return f"AI request failed: {str(e)}"
        else:
            url = f"https://api.pollinations.ai/prompt/{prompt}"
            if system_prompt:
                url += f"?system={system_prompt}"
            try:
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200:
                    return resp.text.strip()
                return f"Error: {resp.status_code}"
            except Exception as e:
                return f"AI request failed: {str(e)}"

    def broadcast(self, text, parse_mode="Markdown"):
        ids = self.db.get_all_chat_ids()
        count = 0
        for cid in ids:
            try:
                self.send_message(cid, text, parse_mode)
                count += 1
            except:
                pass
        return count

    def send_to_user(self, user_id, text, parse_mode="Markdown"):
        if not self.db.user_exists(user_id):
            raise ValueError("User not found")
        return self.send_message(user_id, text, parse_mode)

    def enable_ads_filter(self):
        self._ads_on = True

    def disable_ads_filter(self):
        self._ads_on = False

    def auto_send(self, interval, func):
        def loop_auto():
            while not self._stop:
                time.sleep(interval)
                if self._stop:
                    break
                data = func()
                if data:
                    self.send_message(data["chat_id"], data["text"], data.get("parse_mode", "Markdown"))
        threading.Thread(target=loop_auto, daemon=True).start()

    def off(self):
        self._stop = True

    async def _get_updates(self, timeout=5):
        if self._paused:
            await asyncio.sleep(1)
            return []
        resp = await self._http.get(f"/bot{self.token}/getUpdates", params={"timeout": timeout, "offset": self._last_update + 1})
        if resp.status_code == 200:
            return resp.json().get("result", [])
        return []

    def run(self, timeout=5):
        print(f"Bot {self.get_me()} is running...")
        print("Commands: bot.off(), bot.pause(), bot.on(), broadcast <msg>, send <id> <msg>, ask <q>")
        threading.Thread(target=self._console, daemon=True).start()
        while not self._stop:
            updates = self._run(self._get_updates(timeout))
            for upd in updates:
                if "message" in upd:
                    msg = upd["message"]
                    if msg.get("from", {}).get("is_bot", False) or msg.get("from", {}).get("username") == self.get_me():
                        self._last_update = upd["update_id"]
                        continue
                    self._last_update = upd["update_id"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    username = msg.get("from", {}).get("username", "Unknown")
                    if self._ads_on and self._ads_pattern.search(text):
                        try:
                            self.delete_message(chat_id, msg["message_id"])
                        except:
                            pass
                    self.db.save_message(chat_id, text)
                    self._fire("message", {"chat_id": chat_id, "text": text, "username": username})
                    if "askai" in self._handlers:
                        for handler in self._handlers["askai"]:
                            try:
                                result = handler(chat_id, text, username)
                                if result:
                                    ai_response = self.ask_ai(result)
                                    self.send_message(chat_id, ai_response)
                            except Exception as e:
                                print(f"AI error: {e}")
                elif "callback_query" in upd:
                    cb = upd["callback_query"]
                    self._last_update = upd["update_id"]
                    chat_id = cb["message"]["chat"]["id"]
                    msg_id = cb["message"]["message_id"]
                    data = cb.get("data", "")
                    username = cb.get("from", {}).get("username", "Unknown")
                    self._fire("callback", {"chat_id": chat_id, "message_id": msg_id, "data": data, "username": username})
        self.close()
        print("Bot stopped.")

    def _console(self):
        while not self._stop:
            try:
                cmd = input(f"{YELLOW}bot Console >>>{RESET} ").strip().lower()
                if cmd == "bot.off()":
                    self.off()
                    break
                elif cmd == "bot.pause()":
                    self._paused = True
                elif cmd == "bot.on()":
                    self._paused = False
                elif cmd == "bot.filter.on()":
                    self.enable_ads_filter()
                elif cmd == "bot.filter.off()":
                    self.disable_ads_filter()
                elif cmd.startswith("broadcast "):
                    self.broadcast(cmd[10:].strip())
                elif cmd.startswith("send "):
                    parts = cmd.split(" ", 2)
                    if len(parts) >= 3:
                        try:
                            self.send_to_user(parts[1], parts[2])
                        except Exception as e:
                            print(e)
                elif cmd.startswith("ask "):
                    print(self.ask_ai(cmd[4:].strip()))
                else:
                    print("Invalid")
            except:
                break

    def get_me(self):
        return self._run(self.auth._login())

    def close(self):
        self.db.close()
        self._run(self._http.aclose())
        self.loop.close()