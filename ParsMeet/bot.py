import asyncio
import httpx
import logging
import threading
import time
import re
import os
import random
import string
import importlib.util
from typing import Optional, Callable, Any, Dict, List
from .api.auth import AuthAPI
from .api.rooms import RoomsAPI
from .database import Database
from .utils import KeyboardBuilder, Conversation, Menu, Cache, RateLimit

logger = logging.getLogger("ParsMeet")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class Markdown:
    @staticmethod
    def bold(text: str) -> str:
        return f"**{text}**"
    @staticmethod
    def italic(text: str) -> str:
        return f"__{text}__"
    @staticmethod
    def code(text: str) -> str:
        return f"`{text}`"
    @staticmethod
    def spoiler(text: str) -> str:
        return f"||{text}||"
    @staticmethod
    def link(text: str, url: str) -> str:
        return f"[{text}]({url})"

YELLOW = "\033[93m"
RESET = "\033[0m"

class Bot:
    def __init__(self, token: str, base_url: str = "https://botapi.codemeet.chat", ai_key: Optional[str] = None):
        self.token = token
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._http = httpx.AsyncClient(base_url=base_url, timeout=None)
        self.auth = AuthAPI(self._http, token)
        self.rooms = RoomsAPI(self._http, token, self.loop)
        self.db = Database()
        self._handlers: Dict[str, List[Callable]] = {}
        self._console_commands: Dict[str, Callable] = {}
        self._custom_commands: Dict[str, Callable] = {}
        self._last_update: int = 0
        self._stop: bool = False
        self._paused: bool = False
        self._ads_on: bool = False
        self._ads_pattern = re.compile(r'(https?://|www\.|@\w+|codemeet\.chat|bit\.ly|tinyurl\.com|ads?|promo|discount|free|http://|t\.co)', re.IGNORECASE)
        self._bad_words_pattern = None
        self.ai_key = ai_key
        self.ai_model = "gpt-3.5-turbo"
        self.ai_history: Dict[str, List[Dict[str, str]]] = {}
        self.cache = Cache()
        self.rate_limit = RateLimit(max_requests=5, time_window=1)
        self._antispam_pattern = re.compile(r'(https?://|www\.|@\w+|codemeet\.chat|bit\.ly|tinyurl\.com|ads?|promo|discount|free|http://|t\.co|@)', re.IGNORECASE)
        self._ai_chat_users = set()
        self._load_custom_commands()

    def _run(self, coro):
        return self.loop.run_until_complete(coro)

    def _fire(self, event: str, data: Dict):
        for cb in self._handlers.get(event, []):
            cb(data)

    def _load_custom_commands(self):
        src_file = os.path.join(os.getcwd(), "custom_cmds.py")
        if os.path.exists(src_file):
            spec = importlib.util.spec_from_file_location("custom_cmds", src_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "setup"):
                module.setup(self)

    def on_message_all(self, func: Optional[Callable] = None):
        def wrap(f):
            self._handlers.setdefault("message", []).append(f)
            return f
        return wrap(func) if func else wrap

    def on_callback_query(self, func: Optional[Callable] = None):
        def wrap(f):
            self._handlers.setdefault("callback", []).append(f)
            return f
        return wrap(func) if func else wrap

    def on_askai(self, func: Optional[Callable] = None):
        def wrap(f):
            self._handlers.setdefault("askai", []).append(f)
            return f
        return wrap(func) if func else wrap

    def on_conversation(self, func: Optional[Callable] = None):
        def wrap(f):
            self._handlers.setdefault("conversation", []).append(f)
            return f
        return wrap(func) if func else wrap

    def command(self, name: str):
        def decorator(func):
            self._custom_commands[name] = func
            return func
        return decorator

    def console_command(self, name: str):
        def decorator(func):
            self._console_commands[name] = func
            return func
        return decorator

    def create_callback(self, text: str, data: str) -> Dict:
        return {"text": text, "callback_data": data}

    def btn_menu(self, text: str = "Menu") -> Dict:
        return KeyboardBuilder.btn_menu(text)

    def btn_click_menu(self, text: str, action: str) -> Dict:
        return KeyboardBuilder.btn_click_menu(text, action)

    def send_message(self, chat_id: str, text: str, parse_mode: str = "Markdown", reply_markup: Optional[Dict] = None) -> Dict:
        return self._run(self.rooms._send_message(chat_id, text, parse_mode, reply_markup))

    def reply_message(self, chat_id: str, msg_id: int, text: str, parse_mode: str = "Markdown") -> Dict:
        return self._run(self.rooms._reply_message(chat_id, msg_id, text, parse_mode))

    def edit_message(self, chat_id: str, msg_id: int, text: str, parse_mode: str = "Markdown", reply_markup: Optional[Dict] = None) -> Dict:
        return self._run(self.rooms._edit_message(chat_id, msg_id, text, parse_mode, reply_markup))

    def delete_message(self, chat_id: str, msg_id: int) -> Dict:
        return self._run(self.rooms._delete_message(chat_id, msg_id))

    def send_photo(self, chat_id: str, photo: str, caption: str = "") -> Dict:
        return self._run(self.rooms._send_photo(chat_id, photo, caption))

    def send_document(self, chat_id: str, doc: str, caption: str = "") -> Dict:
        return self._run(self.rooms._send_document(chat_id, doc, caption))

    def ban_user(self, chat_id: str, user_id: int) -> Dict:
        return self._run(self.rooms._ban_user(chat_id, user_id))

    def unban_user(self, chat_id: str, user_id: int) -> Dict:
        return self._run(self.rooms._unban_user(chat_id, user_id))

    def promote_user(self, chat_id: str, user_id: int) -> Dict:
        return self._run(self.rooms._promote_user(chat_id, user_id))

    def demote_user(self, chat_id: str, user_id: int) -> Dict:
        return self._run(self.rooms._demote_user(chat_id, user_id))

    def pin_message(self, chat_id: str, msg_id: int) -> Dict:
        return self._run(self.rooms._pin_message(chat_id, msg_id))

    def warn_user(self, chat_id: str, user_id: int, reason: str = "") -> Dict:
        count = self.db.add_warning(user_id)
        if count >= 3:
            self.ban_user(chat_id, user_id)
            self.db.clear_warnings(user_id)
            return {"status": "banned", "count": count}
        return {"status": "warned", "count": count}

    def mute_user(self, chat_id: str, user_id: int, duration: int = 60) -> Dict:
        return {"status": "muted", "duration": duration}

    def set_welcome(self, chat_id: str, message: str) -> Dict:
        self.db.set_welcome(chat_id, message)
        return {"status": "ok", "message": message}

    def set_custom_command(self, command: str, response: str) -> Dict:
        self.db.set_custom_command(command, response)
        return {"status": "ok"}

    def set_bad_words(self, words: List[str]):
        self._bad_words_pattern = re.compile("|".join(map(re.escape, words)), re.IGNORECASE)

    def set_commands(self, commands: List[Dict]) -> Dict:
        return self._run(self.rooms._set_my_commands(commands))

    def send_captcha(self, chat_id: str, user_id: int) -> None:
        if not PIL_AVAILABLE:
            self.send_message(chat_id, "Captcha requires Pillow library. Install it with pip install Pillow")
            return
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.cache.set(f"captcha_{user_id}", code, ttl=120)
        img = Image.new('RGB', (200, 100), color=(230, 230, 230))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        for _ in range(8):
            draw.line([(random.randint(0, 200), random.randint(0, 100)), (random.randint(0, 200), random.randint(0, 100))], fill=(200, 0, 0), width=1)
        draw.text((20, 30), code, font=font, fill=(0, 0, 0))
        img.save('/tmp/captcha.png')
        self.send_photo(chat_id, '/tmp/captcha.png', caption="Enter the code shown in the image:")

    async def ask_ai_async(self, prompt: str, system_prompt: str = "", user_id: Optional[str] = None) -> str:
        if self.ai_key:
            if user_id and user_id in self.ai_history:
                history = self.ai_history[user_id]
            else:
                history = []
            messages = [{"role": "system", "content": system_prompt or "You are a helpful assistant."}] + history + [{"role": "user", "content": prompt}]
            try:
                response = await self._http.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {self.ai_key}"}, json={"model": self.ai_model, "messages": messages, "max_tokens": 1000}, timeout=60)
                if response.status_code == 200:
                    answer = response.json()["choices"][0]["message"]["content"].strip()
                    if user_id:
                        self.ai_history[user_id] = history + [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}]
                    return answer
                return f"Error: {response.status_code}"
            except Exception as e:
                return f"AI request failed: {str(e)}"
        else:
            services = [
                {"name": "keylessai", "url": "https://keylessai.thryx.workers.dev/v1/chat/completions"},
                {"name": "pollinations", "url": None},
                {"name": "airforce", "url": "https://api.airforce/chat/completions"},
                {"name": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions"}
            ]
            for service in services:
                try:
                    if service["name"] == "keylessai":
                        response = await self._http.post(service["url"], headers={"Content-Type": "application/json"}, json={"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}, timeout=60)
                        if response.status_code == 200:
                            return response.json()["choices"][0]["message"]["content"].strip()
                    elif service["name"] == "pollinations":
                        url = f"https://api.pollinations.ai/prompt/{prompt}"
                        if system_prompt:
                            url += f"?system={system_prompt}"
                        response = await self._http.get(url, timeout=30)
                        if response.status_code == 200:
                            return response.text.strip()
                    elif service["name"] == "airforce":
                        response = await self._http.post(service["url"], headers={"Content-Type": "application/json"}, json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}, timeout=60)
                        if response.status_code == 200:
                            return response.json()["choices"][0]["message"]["content"].strip()
                    elif service["name"] == "openrouter":
                        response = await self._http.post(service["url"], headers={"Content-Type": "application/json"}, json={"model": "openrouter/auto", "messages": [{"role": "user", "content": prompt}], "max_tokens": 1000}, timeout=60)
                        if response.status_code == 200:
                            return response.json()["choices"][0]["message"]["content"].strip()
                except Exception as e:
                    logger.warning(f"AI service {service['name']} failed: {e}")
                    continue
            return "AI services are currently unavailable. Please try again later."

    def ask_ai(self, prompt: str, system_prompt: str = "", user_id: Optional[str] = None) -> str:
        return self._run(self.ask_ai_async(prompt, system_prompt, user_id))

    def broadcast(self, text: str, parse_mode: str = "Markdown", role: Optional[str] = None) -> int:
        ids = self.db.get_all_chat_ids()
        count = 0
        for cid in ids:
            if role and cid not in self.cache.get(f"role_{role}", []):
                continue
            try:
                self.send_message(cid, text, parse_mode)
                count += 1
            except:
                pass
        return count

    def send_to_user(self, user_id: str, text: str, parse_mode: str = "Markdown") -> Dict:
        if not self.db.user_exists(user_id):
            raise ValueError("User not found")
        return self.send_message(user_id, text, parse_mode)

    def enable_ads_filter(self):
        self._ads_on = True

    def disable_ads_filter(self):
        self._ads_on = False

    def auto_send(self, interval: int, func: Callable):
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

    def stop(self):
        self.off()

    async def _get_updates(self, timeout: int = 5):
        if self._paused:
            await asyncio.sleep(1)
            return []
        for attempt in range(3):
            try:
                response = await self._http.get(f"/bot{self.token}/getUpdates", params={"timeout": timeout, "offset": self._last_update + 1})
                if response.status_code == 200:
                    return response.json().get("result", [])
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError, httpx.RemoteProtocolError):
                if attempt == 2:
                    return []
                await asyncio.sleep(1)
            except Exception:
                return []
        return []

    def check_reminders(self):
        reminders = self.db.get_due_reminders()
        for reminder in reminders:
            if not self.cache.get(f"reminder_{reminder[0]}"):
                self.send_message(reminder[1], reminder[3])
                self.cache.set(f"reminder_{reminder[0]}", True)
                self.db.delete_reminder(reminder[0])

    def run(self, timeout: int = 5):
        print(f"Bot {self.get_me()} is running...")
        print("Commands: /<custom>, bot.off(), bot.stop(), bot.pause(), bot.on(), broadcast <msg>, send <id> <msg>, ask <q>, bot.add_new_custom_cmds()")
        threading.Thread(target=self._console, daemon=True).start()
        while not self._stop:
            self.check_reminders()
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
                    user_id = msg.get("from", {}).get("id", 0)
                    if not self.rate_limit.check(user_id):
                        self.send_message(chat_id, "Rate limit exceeded. Slow down!")
                        continue
                    if self._ads_on and self._antispam_pattern.search(text):
                        try:
                            self.delete_message(chat_id, msg["message_id"])
                            self.warn_user(chat_id, user_id)
                            self.send_message(chat_id, "Spam detected! Warning added.")
                        except:
                            pass
                    if self._bad_words_pattern and self._bad_words_pattern.search(text):
                        try:
                            self.warn_user(chat_id, user_id)
                            self.delete_message(chat_id, msg["message_id"])
                        except:
                            pass
                    if text in self._custom_commands:
                        self._custom_commands[text]({"chat_id": chat_id, "text": text, "username": username, "user_id": user_id})
                    else:
                        saved_captcha = self.cache.get(f"captcha_{user_id}")
                        if saved_captcha:
                            if text.strip().upper() == saved_captcha:
                                self.cache.delete(f"captcha_{user_id}")
                                self.send_message(chat_id, "You have been verified.")
                            else:
                                self.send_message(chat_id, "Wrong captcha. Try again.")
                        elif user_id in self._ai_chat_users:
                            if text == "/stop":
                                self._ai_chat_users.discard(user_id)
                                self.send_message(chat_id, "Chat with AI stopped.")
                            else:
                                ai_response = self.ask_ai(text, user_id=user_id)
                                self.send_message(chat_id, ai_response)
                        else:
                            self.db.save_message(chat_id, text, username)
                            self._fire("message", {"chat_id": chat_id, "text": text, "username": username})
                            if "askai" in self._handlers:
                                for handler in self._handlers["askai"]:
                                    try:
                                        result = handler(chat_id, text, username)
                                        if result:
                                            ai_response = self.ask_ai(result, user_id=chat_id)
                                            self.send_message(chat_id, ai_response)
                                    except Exception as e:
                                        logger.error(f"AI error: {e}")
                elif "callback_query" in upd:
                    cb = upd["callback_query"]
                    self._last_update = upd["update_id"]
                    chat_id = cb["message"]["chat"]["id"]
                    msg_id = cb["message"]["message_id"]
                    data = cb.get("data", "")
                    username = cb.get("from", {}).get("username", "Unknown")
                    user_id = cb.get("from", {}).get("id", 0)
                    if data == "not_robot":
                        self.send_captcha(chat_id, user_id)
                    elif data == "ai_chat":
                        self._ai_chat_users.add(user_id)
                        self.send_message(chat_id, "You are now in AI chat mode. Send any text to get AI response. Type /stop to exit.")
                    else:
                        self._fire("callback", {"chat_id": chat_id, "message_id": msg_id, "data": data, "username": username})
        self.close()
        print("Bot stopped.")

    def _console(self):
        while not self._stop:
            try:
                cmd = input(f"{YELLOW}bot Console >>>{RESET} ").strip()
                if not cmd:
                    continue
                if cmd == "bot.add_new_custom_cmds()":
                    self._add_new_custom_cmd()
                elif cmd.startswith("/"):
                    command_name = cmd[1:].split()[0].lower()
                    if command_name in self._custom_commands:
                        args = cmd[len(cmd.split()[0]):].strip()
                        self._custom_commands[command_name](args)
                    else:
                        print("Command not found")
                elif cmd.startswith("bot."):
                    if cmd in ("bot.off()", "bot.stop()"):
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
                    else:
                        print("Invalid bot command")
                elif cmd.startswith("broadcast"):
                    msg = cmd[10:].strip()
                    if msg:
                        self.broadcast(msg)
                elif cmd.startswith("send"):
                    parts = cmd.split(" ", 2)
                    if len(parts) >= 3:
                        try:
                            self.send_to_user(parts[1], parts[2])
                        except Exception as e:
                            print(e)
                elif cmd.startswith("ask"):
                    print(self.ask_ai(cmd[4:].strip()))
                else:
                    handled = False
                    for cmd_name, cmd_func in self._console_commands.items():
                        if cmd == cmd_name or cmd.startswith(cmd_name + " "):
                            args = cmd[len(cmd_name):].strip()
                            cmd_func(args)
                            handled = True
                            break
                    if not handled:
                        print("Command not found")
            except:
                break

    def _add_new_custom_cmd(self):
        print("Enter the command name (English letters only):")
        cmd_name = input().strip()
        if not cmd_name:
            print("Command name cannot be empty.")
            return
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', cmd_name):
            print("Only English letters and digits are supported. No slash or punctuation.")
            return
        file_path = os.path.join(os.getcwd(), "custom_cmds.py")
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("def setup(bot):\n")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"\n    @bot.command('{cmd_name}')\n")
            f.write(f"    def {cmd_name}_command(data):\n")
            f.write(f"        pass\n")
        print(f"Command '{cmd_name}' added to custom_cmds.py")
        self._load_custom_commands()

    def get_me(self):
        return self._run(self.auth._login())

    def close(self):
        self.db.close()
        self._run(self._http.aclose())
        self.loop.close()