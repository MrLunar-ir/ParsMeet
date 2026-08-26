import httpx
import asyncio
from datetime import datetime
from ..models import Room

class RoomsAPI:
    def __init__(self, client, token, loop):
        self.client = client
        self.token = token
        self.loop = loop

    def _run(self, coro):
        return self.loop.run_until_complete(coro)

    async def _send_message(self, chat_id, text, parse_mode="Markdown", reply_markup=None):
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        if reply_markup: payload["reply_markup"] = reply_markup
        r = await self.client.post(f"/bot{self.token}/sendMessage", json=payload)
        return r.json() if r.status_code == 200 else {"error": r.text}

    def send_message(self, chat_id, text, parse_mode="Markdown", reply_markup=None):
        return self._run(self._send_message(chat_id, text, parse_mode, reply_markup))

    async def _reply_message(self, chat_id, msg_id, text, parse_mode="Markdown"):
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "reply_to_message_id": msg_id}
        r = await self.client.post(f"/bot{self.token}/sendMessage", json=payload)
        return r.json() if r.status_code == 200 else {"error": r.text}

    def reply_message(self, chat_id, msg_id, text, parse_mode="Markdown"):
        return self._run(self._reply_message(chat_id, msg_id, text, parse_mode))

    async def _edit_message(self, chat_id, msg_id, text, parse_mode="Markdown", reply_markup=None):
        payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": parse_mode}
        if reply_markup: payload["reply_markup"] = reply_markup
        r = await self.client.post(f"/bot{self.token}/editMessageText", json=payload)
        return r.json() if r.status_code == 200 else {"error": r.text}

    def edit_message(self, chat_id, msg_id, text, parse_mode="Markdown", reply_markup=None):
        return self._run(self._edit_message(chat_id, msg_id, text, parse_mode, reply_markup))

    async def _delete_message(self, chat_id, msg_id):
        r = await self.client.post(f"/bot{self.token}/deleteMessage", json={"chat_id": chat_id, "message_id": msg_id})
        return r.json() if r.status_code == 200 else {"error": r.text}

    def delete_message(self, chat_id, msg_id):
        return self._run(self._delete_message(chat_id, msg_id))

    async def _send_photo(self, chat_id, photo, caption=""):
        r = await self.client.post(f"/bot{self.token}/sendPhoto", json={"chat_id": chat_id, "photo": photo, "caption": caption})
        return r.json() if r.status_code == 200 else {"error": r.text}

    def send_photo(self, chat_id, photo, caption=""):
        return self._run(self._send_photo(chat_id, photo, caption))

    async def _send_document(self, chat_id, doc, caption=""):
        r = await self.client.post(f"/bot{self.token}/sendDocument", json={"chat_id": chat_id, "document": doc, "caption": caption})
        return r.json() if r.status_code == 200 else {"error": r.text}

    def send_document(self, chat_id, doc, caption=""):
        return self._run(self._send_document(chat_id, doc, caption))

    async def _send_action(self, chat_id, action):
        r = await self.client.post(f"/bot{self.token}/sendChatAction", json={"chat_id": chat_id, "action": action})
        return r.json() if r.status_code == 200 else {"error": r.text}

    def send_action(self, chat_id, action):
        return self._run(self._send_action(chat_id, action))

    async def _ban_user(self, chat_id, user_id):
        r = await self.client.post(f"/bot{self.token}/banChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return r.json() if r.status_code == 200 else {"error": r.text}

    def ban_user(self, chat_id, user_id):
        return self._run(self._ban_user(chat_id, user_id))

    async def _unban_user(self, chat_id, user_id):
        r = await self.client.post(f"/bot{self.token}/unbanChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return r.json() if r.status_code == 200 else {"error": r.text}

    def unban_user(self, chat_id, user_id):
        return self._run(self._unban_user(chat_id, user_id))

    async def _promote_user(self, chat_id, user_id):
        r = await self.client.post(f"/bot{self.token}/promoteChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return r.json() if r.status_code == 200 else {"error": r.text}

    def promote_user(self, chat_id, user_id):
        return self._run(self._promote_user(chat_id, user_id))

    async def _demote_user(self, chat_id, user_id):
        r = await self.client.post(f"/bot{self.token}/demoteChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return r.json() if r.status_code == 200 else {"error": r.text}

    def demote_user(self, chat_id, user_id):
        return self._run(self._demote_user(chat_id, user_id))

    async def _pin_message(self, chat_id, msg_id):
        r = await self.client.post(f"/bot{self.token}/pinChatMessage", json={"chat_id": chat_id, "message_id": msg_id})
        return r.json() if r.status_code == 200 else {"error": r.text}

    def pin_message(self, chat_id, msg_id):
        return self._run(self._pin_message(chat_id, msg_id))

    async def _set_my_commands(self, commands):
        r = await self.client.post(f"/bot{self.token}/setMyCommands", json={"commands": commands})
        return r.json() if r.status_code == 200 else {"error": r.text}

    def set_my_commands(self, commands):
        return self._run(self._set_my_commands(commands))