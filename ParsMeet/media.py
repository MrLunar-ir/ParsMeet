class MediaClient:
    def __init__(self, http, token, loop):
        self.http = http
        self.token = token
        self.loop = loop

    def _run(self, coro):
        return self.loop.run_until_complete(coro)

    async def _send_photo(self, chat_id, photo, caption="", parse_mode="Markdown"):
        response = await self.http.post(f"/bot{self.token}/sendPhoto", json={"chat_id": chat_id, "photo": photo, "caption": caption, "parse_mode": parse_mode})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    def send_photo(self, chat_id, photo, caption="", parse_mode="Markdown"):
        return self._run(self._send_photo(chat_id, photo, caption, parse_mode))

    async def _send_document(self, chat_id, document, caption="", parse_mode="Markdown"):
        response = await self.http.post(f"/bot{self.token}/sendDocument", json={"chat_id": chat_id, "document": document, "caption": caption, "parse_mode": parse_mode})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    def send_document(self, chat_id, document, caption="", parse_mode="Markdown"):
        return self._run(self._send_document(chat_id, document, caption, parse_mode))

    async def _send_video(self, chat_id, video, caption=""):
        response = await self.http.post(f"/bot{self.token}/sendVideo", json={"chat_id": chat_id, "video": video, "caption": caption})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    def send_video(self, chat_id, video, caption=""):
        return self._run(self._send_video(chat_id, video, caption))

    async def _send_voice(self, chat_id, voice, caption=""):
        response = await self.http.post(f"/bot{self.token}/sendVoice", json={"chat_id": chat_id, "voice": voice, "caption": caption})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    def send_voice(self, chat_id, voice, caption=""):
        return self._run(self._send_voice(chat_id, voice, caption))