import asyncio
import httpx
import logging
import threading
import time
import re
import os
import importlib.util
from typing import Optional, Callable, Any, Dict, List
from .config import Config
from .logger import setup_logger
from .api import APIClient, AuthAPI, MessagesAPI, ChatsAPI, UpdatesAPI, MediaAPI, AdminAPI
from .database import Database
from .storage import Storage
from .exceptions import ParsMeetError
from .filters import Filter, Filters
from .middleware import BaseMiddleware, Recovery
from .keyboard import Button, InlineKeyboard, ReplyKeyboard
from .session import SessionManager
from .cooldown import Cooldown
from .scheduler import Scheduler
from .i18n import I18n
from .fsm import Conversation, ConversationManager
from .broadcast import BroadcastQueue
from .plugins import PluginManager
from .tools import AntiLink, AntiSpam, ProfanityFilter, Captcha, WarnSystem, MaintenanceMode
from .ai import AIManager, AITools
from .utils import Cache, RateLimit

logger = logging.getLogger("ParsMeet")

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
    def __init__(self, token=None, config: Optional[Config] = None, **kwargs):
        if config is None:
            config = Config(token=token or "", **kwargs)
        self.config = config
        self.token = config.token
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.logger = setup_logger("ParsMeet", config.log_level, config.log_file)

        self.api = APIClient(config.base_url, config.token, config.timeout, config.retries, config.retry_backoff)
        self.auth = AuthAPI(self.api)
        self.messages = MessagesAPI(self.api)
        self.chats = ChatsAPI(self.api)
        self.updates = UpdatesAPI(self.api)
        self.media = MediaAPI(self.api)
        self.admin = AdminAPI(self.api)

        self.db = Database(config.database_path)
        self.storage = Storage(config.storage_path)
        self.cache = Cache()
        self.session = SessionManager()
        self.cooldown = Cooldown(seconds=config.cooldown_seconds)
        self.rate_limit = RateLimit(max_requests=config.rate_limit_max, time_window=config.rate_limit_window)
        self.scheduler = Scheduler()
        self.i18n = I18n()
        self.fsm = ConversationManager()
        self.broadcast_queue = BroadcastQueue(self, delay=0.5)
        self.plugins = PluginManager(self)

        self.ai = AIManager(provider=config.ai_provider, api_key=config.ai_key, model=config.ai_model, memory_enabled=config.ai_memory)
        self.ai_tools = AITools(self.ai)

        self.anti_link = AntiLink()
        self.anti_spam = AntiSpam()
        self.profanity = ProfanityFilter()
        self.captcha = Captcha(self.cache)
        self.warn_system = WarnSystem(self.db)
        self.maintenance = MaintenanceMode()

        self._handlers = []
        self._console_commands = {}
        self._custom_commands = {}
        self._middlewares = []
        self._recovery = Recovery()
        self._last_update = 0
        self._stop = False
        self._paused = False
        self._ads_on = False
        self._ai_chat_users = set()
        self._commands_help = {}
        self._started_at = time.time()
        self._load_custom_commands()

    def _run(self, coro):
        return self.loop.run_until_complete(coro)

    def _load_custom_commands(self):
        src_file = os.path.join(os.getcwd(), "custom_cmds.py")
        if os.path.exists(src_file):
            try:
                spec = importlib.util.spec_from_file_location("custom_cmds", src_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "setup"):
                    module.setup(self)
            except Exception as e:
                logger.error(f"Custom commands load error: {e}")

    def use(self, middleware):
        self._middlewares.append(middleware)
        return self

    def on_message(self, filter=None, func=None):
        def wrap(f):
            self._handlers.append(("message", filter or Filters.custom(lambda d: True), f))
            return f
        return wrap(func) if func else wrap

    def on_callback_query(self, filter=None, func=None):
        def wrap(f):
            self._handlers.append(("callback", filter or Filters.custom(lambda d: True), f))
            return f
        return wrap(func) if func else wrap

    def on_askai(self, func=None):
        def wrap(f):
            self._handlers.append(("askai", Filters.custom(lambda d: True), f))
            return f
        return wrap(func) if func else wrap

    def on_message_all(self, func=None):
        return self.on_message(Filters.custom(lambda d: True), func)

    def command(self, name):
        def decorator(func):
            self._custom_commands[name] = func
            return func
        return decorator

    def console_command(self, name):
        def decorator(func):
            self._console_commands[name] = func
            return func
        return decorator

    def register_command(self, name, description):
        self._commands_help[name] = description

    def generate_help(self):
        lines = ["Available commands:"]
        for name, desc in self._commands_help.items():
            lines.append(f"/{name} - {desc}")
        return "\n".join(lines)

    def create_callback(self, text, data):
        return {"text": text, "callback_data": data}

    def create_button(self, text, callback_data=None, url=None):
        return Button(text, callback_data, url)

    def create_keyboard(self):
        return InlineKeyboard()

    def get_session(self, chat_id):
        return self.session.get(chat_id)

    def set_locale(self, user_id, locale):
        self.i18n.set_locale(user_id, locale)

    def text(self, key, user_id=None, **kwargs):
        return self.i18n.text(key, user_id, **kwargs)

    def send_message(self, chat_id, text, parse_mode="Markdown", reply_markup=None):
        if isinstance(reply_markup, (InlineKeyboard, ReplyKeyboard)):
            reply_markup = reply_markup.to_dict()
        return self._run(self.messages.send(chat_id, text, parse_mode, reply_markup))

    def reply_message(self, chat_id, msg_id, text, parse_mode="Markdown"):
        return self._run(self.messages.reply(chat_id, msg_id, text, parse_mode))

    def edit_message(self, chat_id, msg_id, text, parse_mode="Markdown", reply_markup=None):
        if isinstance(reply_markup, (InlineKeyboard, ReplyKeyboard)):
            reply_markup = reply_markup.to_dict()
        return self._run(self.messages.edit(chat_id, msg_id, text, parse_mode, reply_markup))

    def delete_message(self, chat_id, msg_id):
        return self._run(self.messages.delete(chat_id, msg_id))

    def forward_message(self, chat_id, from_chat_id, msg_id):
        return self._run(self.messages.forward(chat_id, from_chat_id, msg_id))

    def send_photo(self, chat_id, photo, caption=""):
        return self._run(self.media.send_photo(chat_id, photo, caption))

    def send_document(self, chat_id, doc, caption=""):
        return self._run(self.media.send_document(chat_id, doc, caption))

    def send_video(self, chat_id, video, caption=""):
        return self._run(self.media.send_video(chat_id, video, caption))

    def send_voice(self, chat_id, voice, caption=""):
        return self._run(self.media.send_voice(chat_id, voice, caption))

    def ban_user(self, chat_id, user_id):
        return self._run(self.chats.ban_user(chat_id, user_id))

    def unban_user(self, chat_id, user_id):
        return self._run(self.chats.unban_user(chat_id, user_id))

    def promote_user(self, chat_id, user_id):
        return self._run(self.chats.promote_user(chat_id, user_id))

    def demote_user(self, chat_id, user_id):
        return self._run(self.chats.demote_user(chat_id, user_id))

    def pin_message(self, chat_id, msg_id):
        return self._run(self.chats.pin(chat_id, msg_id))

    def get_chat_member(self, chat_id, user_id):
        return self._run(self.chats.get_member(chat_id, user_id))

    def warn_user(self, chat_id, user_id):
        return self.warn_system.warn(self, chat_id, user_id)

    def set_welcome(self, chat_id, message):
        self.db.set_welcome(chat_id, message)
        return {"status": "ok"}

    def set_bad_words(self, words):
        self.profanity.set_words(words)

    def ask_ai(self, prompt, system_prompt="", user_id=None):
        return self._run(self._ask_ai_async(prompt, system_prompt, user_id))

    async def _ask_ai_async(self, prompt, system_prompt="", user_id=None):
        uid = user_id or "default"
        return await self.ai.chat(uid, prompt, system_prompt)

    def set_ai_provider(self, name, api_key=None, model=None):
        self.ai.set_provider(name, api_key, model)

    def clear_ai_memory(self, user_id):
        self.ai.clear_memory(user_id)

    def ai_summarize(self, chat_id, messages):
        return self._run(self.ai_tools.summarize(chat_id, messages))

    def ai_translate(self, chat_id, text, target_lang):
        return self._run(self.ai_tools.translate(chat_id, text, target_lang))

    def ai_detect_spam(self, chat_id, text):
        return self._run(self.ai_tools.detect_spam(chat_id, text))

    def ai_classify(self, chat_id, text, categories):
        return self._run(self.ai_tools.classify(chat_id, text, categories))

    def storage_set(self, user_id, key, value):
        self.storage.set(user_id, key, value)

    def storage_get(self, user_id, key, default=None):
        return self.storage.get(user_id, key, default)

    def storage_increment(self, user_id, key, amount=1):
        return self.storage.increment(user_id, key, amount)

    def add_state(self, conv_name, state_name, handler, next_state=None):
        if conv_name not in self.fsm.conversations:
            self.fsm.register(Conversation(conv_name))
        self.fsm.conversations[conv_name].add_state(state_name, handler, next_state)

    def start_conversation(self, user_id, conv_name, data=None):
        return self.fsm.start(user_id, conv_name, data)

    def stop_conversation(self, user_id):
        self.fsm.stop(user_id)

    def is_in_conversation(self, user_id):
        return self.fsm.is_active(user_id)

    def broadcast(self, text, parse_mode="Markdown"):
        ids = self.db.get_all_chat_ids()
        count = 0
        for cid in ids:
            try:
                self.send_message(cid, text, parse_mode)
                count += 1
            except Exception:
                pass
        return count

    def queued_broadcast(self, text, parse_mode="Markdown"):
        ids = self.db.get_all_chat_ids()
        self.broadcast_queue.add_many(ids, text, parse_mode)
        self.broadcast_queue.start()
        return len(ids)

    def load_plugins(self, folder="plugins"):
        count = self.plugins.load_from_folder(folder)
        print(f"Loaded {count} plugins.")
        return count

    def register_plugin(self, plugin):
        return self.plugins.register(plugin)

    def list_plugins(self):
        return self.plugins.list_plugins()

    def enable_webhook(self, port=8443, secret=None):
        from .webhook import WebhookServer
        self.webhook = WebhookServer(self, port=port, secret=secret)
        self.webhook.start()

    def enable_dashboard(self, port=8080):
        from .dashboard import start_dashboard
        start_dashboard(self, port=port)

    def off(self):
        self._stop = True

    def stop(self):
        self.off()

    def _process_update(self, update):
        if "message" in update:
            msg = update["message"]
            if msg.get("from", {}).get("is_bot", False):
                return
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")
            username = msg.get("from", {}).get("username", "Unknown")
            user_id = msg.get("from", {}).get("id", 0)
            if self.maintenance.check():
                self.send_message(chat_id, self.maintenance.message)
                return
            if not self.rate_limit.check(user_id):
                self.send_message(chat_id, "Rate limit exceeded.")
                return
            if self._ads_on and self.anti_link.check(text):
                try:
                    self.delete_message(chat_id, msg.get("message_id", 0))
                except Exception:
                    pass
            if self.profanity.check(text):
                try:
                    self.warn_system.warn(self, chat_id, user_id)
                    self.delete_message(chat_id, msg.get("message_id", 0))
                except Exception:
                    pass
            if self.fsm.is_active(str(user_id)):
                data = {"chat_id": chat_id, "text": text, "username": username, "user_id": user_id, "message_id": msg.get("message_id", 0)}
                self.fsm.handle(str(user_id), data)
                return
            data = {
                "chat_id": chat_id,
                "text": text,
                "username": username,
                "user_id": user_id,
                "chat_type": msg.get("chat", {}).get("type", "private"),
                "message_id": msg.get("message_id", 0),
                "reply_to_message": msg.get("reply_to_message"),
                "is_admin": msg.get("from", {}).get("is_admin", False),
                "raw": msg
            }
            self.db.save_message(chat_id, text, username)
            if text in self._custom_commands:
                try:
                    self._custom_commands[text](data)
                except Exception as e:
                    logger.error(f"Custom command error: {e}")
            else:
                self._dispatch("message", data)
                for ev_type, _, handler in self._handlers:
                    if ev_type == "askai":
                        try:
                            result = handler(chat_id, text, username)
                            if result:
                                self.send_message(chat_id, self.ask_ai(result, user_id=chat_id))
                        except Exception as e:
                            logger.error(f"AI error: {e}")
        elif "callback_query" in update:
            cb = update["callback_query"]
            chat_id = cb["message"]["chat"]["id"]
            msg_id = cb["message"]["message_id"]
            data = {
                "chat_id": chat_id,
                "message_id": msg_id,
                "data": cb.get("data", ""),
                "username": cb.get("from", {}).get("username", "Unknown"),
                "user_id": cb.get("from", {}).get("id", 0),
                "raw": cb
            }
            self._dispatch("callback", data)

    def _dispatch(self, event_type, data):
        for mw in self._middlewares:
            try:
                data = mw.process(data) or data
            except Exception as e:
                logger.error(f"Middleware error: {e}")
        if data.get("_blocked"):
            return
        for ev_type, filter_obj, handler in self._handlers:
            if ev_type != event_type:
                continue
            try:
                if filter_obj(data):
                    handler(data)
            except Exception as e:
                logger.error(f"Handler error: {e}")
                self._recovery.on_error(data, e)

    async def _get_updates(self, timeout=30):
        if self._paused:
            await asyncio.sleep(1)
            return []
        try:
            return await self.updates.get_updates_safe(
                offset=self._last_update + 1,
                timeout=timeout,
                limit=self.config.polling_limit,
                max_retries=self.config.polling_max_retries
            )
        except Exception as e:
            logger.debug(f"Update fetch error: {e}")
            return []

    def run(self, timeout=None):
        if timeout is None:
            timeout = self.config.polling_timeout
        try:
            bot_username = self._run(self.auth.get_me()).get("username", "unknown")
        except Exception as e:
            print(f"Failed to connect: {e}")
            return
        print(f"Bot @{bot_username} is running...")
        print(f"Polling timeout: {timeout}s | Retries: {self.config.polling_max_retries}")
        print("Commands: bot.off(), bot.stop(), bot.pause(), bot.on(), broadcast <msg>, ask <q>")
        self.scheduler.start()
        self.broadcast_queue.start()
        threading.Thread(target=self._console, daemon=True).start()
        consecutive_errors = 0
        while not self._stop:
            try:
                updates = self._run(self._get_updates(timeout))
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Run loop error: {e}")
                updates = []
            if updates:
                consecutive_errors = 0
                for upd in updates:
                    update_id = upd.get("update_id", 0)
                    if update_id <= self._last_update:
                        continue
                    self._last_update = update_id
                    try:
                        self._process_update(upd)
                    except Exception as e:
                        logger.error(f"Processing error: {e}")
            else:
                consecutive_errors += 1
                if consecutive_errors > 10:
                    logger.warning("Too many empty responses, sleeping 30s...")
                    time.sleep(30)
                    consecutive_errors = 0
        self.close()
        print("Bot stopped.")

    def _console(self):
        while not self._stop:
            try:
                cmd = input(f"{YELLOW}bot Console >>>{RESET} ").strip()
                if not cmd:
                    continue
                if cmd in ("bot.off()", "bot.stop()"):
                    self.off()
                    break
                elif cmd == "bot.pause()":
                    self._paused = True
                    print("Bot paused.")
                elif cmd == "bot.on()":
                    self._paused = False
                    print("Bot resumed.")
                elif cmd == "bot.filter.on()":
                    self._ads_on = True
                    print("Ads filter enabled.")
                elif cmd == "bot.filter.off()":
                    self._ads_on = False
                    print("Ads filter disabled.")
                elif cmd.startswith("broadcast "):
                    count = self.broadcast(cmd[10:].strip())
                    print(f"Broadcast sent to {count} users.")
                elif cmd.startswith("ask "):
                    print(self.ask_ai(cmd[4:].strip()))
                else:
                    handled = False
                    for name, func in self._console_commands.items():
                        if cmd == name or cmd.startswith(name + " "):
                            func(cmd[len(name):].strip())
                            handled = True
                            break
                    if not handled:
                        print("Command not found")
            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                logger.error(f"Console error: {e}")

    def get_me(self):
        return self._run(self.auth.get_me())

    def close(self):
        try:
            self.scheduler.stop()
        except Exception:
            pass
        try:
            self.broadcast_queue.stop()
        except Exception:
            pass
        try:
            self._run(self.ai.close())
        except Exception:
            pass
        try:
            self.db.close()
        except Exception:
            pass
        try:
            self._run(self.api.close())
        except Exception:
            pass
        try:
            self.loop.close()
        except Exception:
            pass