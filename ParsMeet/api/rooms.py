import httpx
from datetime import datetime
from ..models import Room

class RoomsAPI:
    def __init__(self, client: httpx.AsyncClient, loop):
        self.client = client
        self.loop = loop

    def _run(self, coro):
        return self.loop.run_until_complete(coro)

    async def _create_room(self, name: str) -> Room:
        return Room(id="mock_room_id", name=name, created_at=datetime.now())

    def create_room(self, name: str) -> Room:
        return self._run(self._create_room(name))

    async def _send_message(self, chat_id: str, text: str, parse_mode: str = "Markdown", reply_markup: dict = None) -> dict:
        url = f"/bot{self.client.headers.get('Authorization', '').split(' ')[-1]}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = await self.client.post(url, json=payload)
        return response.json() if response.status_code == 200 else {"error": response.text}

    def send_message(self, chat_id: str, text: str, parse_mode: str = "Markdown", reply_markup: dict = None) -> dict:
        return self._run(self._send_message(chat_id, text, parse_mode, reply_markup))

    async def _edit_message(self, chat_id: str, message_id: int, text: str, parse_mode: str = "Markdown", reply_markup: dict = None) -> dict:
        url = f"/bot{self.client.headers.get('Authorization', '').split(' ')[-1]}/editMessageText"
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = await self.client.post(url, json=payload)
        return response.json() if response.status_code == 200 else {"error": response.text}

    def edit_message(self, chat_id: str, message_id: int, text: str, parse_mode: str = "Markdown", reply_markup: dict = None) -> dict:
        return self._run(self._edit_message(chat_id, message_id, text, parse_mode, reply_markup))

    async def _delete_message(self, chat_id: str, message_id: int) -> dict:
        url = f"/bot{self.client.headers.get('Authorization', '').split(' ')[-1]}/deleteMessage"
        payload = {"chat_id": chat_id, "message_id": message_id}
        response = await self.client.post(url, json=payload)
        return response.json() if response.status_code == 200 else {"error": response.text}

    def delete_message(self, chat_id: str, message_id: int) -> dict:
        return self._run(self._delete_message(chat_id, message_id))

    async def _send_photo(self, chat_id: str, photo: str, caption: str = "", parse_mode: str = "Markdown", reply_markup: dict = None) -> dict:
        url = f"/bot{self.client.headers.get('Authorization', '').split(' ')[-1]}/sendPhoto"
        payload = {"chat_id": chat_id, "photo": photo, "caption": caption, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = await self.client.post(url, json=payload)
        return response.json() if response.status_code == 200 else {"error": response.text}

    def send_photo(self, chat_id: str, photo: str, caption: str = "", parse_mode: str = "Markdown", reply_markup: dict = None) -> dict:
        return self._run(self._send_photo(chat_id, photo, caption, parse_mode, reply_markup))

    async def _send_document(self, chat_id: str, document: str, caption: str = "", parse_mode: str = "Markdown", reply_markup: dict = None) -> dict:
        url = f"/bot{self.client.headers.get('Authorization', '').split(' ')[-1]}/sendDocument"
        payload = {"chat_id": chat_id, "document": document, "caption": caption, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = await self.client.post(url, json=payload)
        return response.json() if response.status_code == 200 else {"error": response.text}

    def send_document(self, chat_id: str, document: str, caption: str = "", parse_mode: str = "Markdown", reply_markup: dict = None) -> dict:
        return self._run(self._send_document(chat_id, document, caption, parse_mode, reply_markup))

    async def _set_my_commands(self, commands: list) -> dict:
        url = f"/bot{self.client.headers.get('Authorization', '').split(' ')[-1]}/setMyCommands"
        response = await self.client.post(url, json={"commands": commands})
        return response.json() if response.status_code == 200 else {"error": response.text}

    def set_my_commands(self, commands: list) -> dict:
        return self._run(self._set_my_commands(commands))