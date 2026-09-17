class MessagesAPI:
    def __init__(self, client):
        self.client = client

    async def send(self, chat_id, text, parse_mode="Markdown", reply_markup=None):
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = await self.client.request("POST", "/sendMessage", json=payload)
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def reply(self, chat_id, message_id, text, parse_mode="Markdown"):
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "reply_to_message_id": message_id}
        response = await self.client.request("POST", "/sendMessage", json=payload)
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def edit(self, chat_id, message_id, text, parse_mode="Markdown", reply_markup=None):
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = await self.client.request("POST", "/editMessageText", json=payload)
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def delete(self, chat_id, message_id):
        response = await self.client.request("POST", "/deleteMessage", json={"chat_id": chat_id, "message_id": message_id})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def forward(self, chat_id, from_chat_id, message_id):
        response = await self.client.request("POST", "/forwardMessage", json={"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id})
        return response.json() if response.status_code == 200 else {"error": "Failed"}