import httpx
import asyncio
import time
from datetime import datetime
from ..models import Room
from ..exceptions import ParsMeetNetworkError

class RoomsAPI:
    def __init__(self, client, token, loop):
        self.client = client
        self.token = token
        self.loop = loop

    def _run(self, coro):
        return self.loop.run_until_complete(coro)

    async def _request(self, method, path, retries=3, base_delay=1, **kwargs):
        for attempt in range(retries):
            try:
                response = await self.client.request(method, f"/bot{self.token}{path}", **kwargs)
                if response.status_code < 500:
                    return response
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError):
                if attempt == retries - 1:
                    raise ParsMeetNetworkError("Connection failed")
                await asyncio.sleep(base_delay * (2 ** attempt))
        return None

    async def _create_room(self, name):
        return Room(id="mock_room_id", name=name, created_at=datetime.now())

    def create_room(self, name):
        return self._run(self._create_room(name))

    async def _send_message(self, chat_id, text, parse_mode="Markdown", reply_markup=None):
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = await self._request("POST", "/sendMessage", json=payload)
        if response and response.status_code == 200:
            return response.json()
        return {"error": "Failed to send message"}

    def send_message(self, chat_id, text, parse_mode="Markdown", reply_markup=None):
        return self._run(self._send_message(chat_id, text, parse_mode, reply_markup))

    async def _reply_message(self, chat_id, msg_id, text, parse_mode="Markdown"):
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "reply_to_message_id": msg_id}
        response = await self._request("POST", "/sendMessage", json=payload)
        if response and response.status_code == 200:
            return response.json()
        return {"error": "Failed to reply"}

    def reply_message(self, chat_id, msg_id, text, parse_mode="Markdown"):
        return self._run(self._reply_message(chat_id, msg_id, text, parse_mode))

    async def _edit_message(self, chat_id, msg_id, text, parse_mode="Markdown", reply_markup=None):
        payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = await self._request("POST", "/editMessageText", json=payload)
        if response and response.status_code == 200:
            return response.json()
        return {"error": "Failed to edit"}

    def edit_message(self, chat_id, msg_id, text, parse_mode="Markdown", reply_markup=None):
        return self._run(self._edit_message(chat_id, msg_id, text, parse_mode, reply_markup))

    async def _delete_message(self, chat_id, msg_id):
        response = await self._request("POST", "/deleteMessage", json={"chat_id": chat_id, "message_id": msg_id})
        if response and response.status_code == 200:
            return response.json()
        return {"error": "Failed to delete"}

    def delete_message(self, chat_id, msg_id):
        return self._run(self._delete_message(chat_id, msg_id))

    async def _send_photo(self, chat_id, photo, caption=""):
        response = await self._request("POST", "/sendPhoto", json={"chat_id": chat_id, "photo": photo, "caption": caption})
        if response and response.status_code == 200:
            return response.json()
        return {"error": "Failed to send photo"}

    def send_photo(self, chat_id, photo, caption=""):
        return self._run(self._send_photo(chat_id, photo, caption))

    async def _send_document(self, chat_id, doc, caption=""):
        response = await self._request("POST", "/sendDocument", json={"chat_id": chat_id, "document": doc, "caption": caption})
        if response and response.status_code == 200:
            return response.json()
        return {"error": "Failed to send document"}

    def send_document(self, chat_id, doc, caption=""):
        return self._run(self._send_document(chat_id, doc, caption))

    async def _ban_user(self, chat_id, user_id):
        response = await self._request("POST", "/banChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return response.json() if response and response.status_code == 200 else {"error": "Failed to ban"}

    def ban_user(self, chat_id, user_id):
        return self._run(self._ban_user(chat_id, user_id))

    async def _unban_user(self, chat_id, user_id):
        response = await self._request("POST", "/unbanChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return response.json() if response and response.status_code == 200 else {"error": "Failed to unban"}

    def unban_user(self, chat_id, user_id):
        return self._run(self._unban_user(chat_id, user_id))

    async def _promote_user(self, chat_id, user_id):
        response = await self._request("POST", "/promoteChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return response.json() if response and response.status_code == 200 else {"error": "Failed to promote"}

    def promote_user(self, chat_id, user_id):
        return self._run(self._promote_user(chat_id, user_id))

    async def _demote_user(self, chat_id, user_id):
        response = await self._request("POST", "/demoteChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return response.json() if response and response.status_code == 200 else {"error": "Failed to demote"}

    def demote_user(self, chat_id, user_id):
        return self._run(self._demote_user(chat_id, user_id))

    async def _pin_message(self, chat_id, msg_id):
        response = await self._request("POST", "/pinChatMessage", json={"chat_id": chat_id, "message_id": msg_id})
        return response.json() if response and response.status_code == 200 else {"error": "Failed to pin"}

    def pin_message(self, chat_id, msg_id):
        return self._run(self._pin_message(chat_id, msg_id))

    async def _set_my_commands(self, commands):
        response = await self._request("POST", "/setMyCommands", json={"commands": commands})
        return response.json() if response and response.status_code == 200 else {"error": "Failed to set commands"}

    def set_my_commands(self, commands):
        return self._run(self._set_my_commands(commands))