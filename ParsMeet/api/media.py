class MediaAPI:
    def __init__(self, client):
        self.client = client

    async def send_photo(self, chat_id, photo, caption=""):
        response = await self.client.request("POST", "/sendPhoto", json={"chat_id": chat_id, "photo": photo, "caption": caption})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def send_document(self, chat_id, doc, caption=""):
        response = await self.client.request("POST", "/sendDocument", json={"chat_id": chat_id, "document": doc, "caption": caption})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def send_video(self, chat_id, video, caption=""):
        response = await self.client.request("POST", "/sendVideo", json={"chat_id": chat_id, "video": video, "caption": caption})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def send_audio(self, chat_id, audio, caption=""):
        response = await self.client.request("POST", "/sendAudio", json={"chat_id": chat_id, "audio": audio, "caption": caption})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def send_voice(self, chat_id, voice, caption=""):
        response = await self.client.request("POST", "/sendVoice", json={"chat_id": chat_id, "voice": voice, "caption": caption})
        return response.json() if response.status_code == 200 else {"error": "Failed"}