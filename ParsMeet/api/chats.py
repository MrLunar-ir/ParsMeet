class ChatsAPI:
    def __init__(self, client):
        self.client = client

    async def ban_user(self, chat_id, user_id):
        response = await self.client.request("POST", "/banChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def unban_user(self, chat_id, user_id):
        response = await self.client.request("POST", "/unbanChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def promote_user(self, chat_id, user_id):
        response = await self.client.request("POST", "/promoteChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def demote_user(self, chat_id, user_id):
        response = await self.client.request("POST", "/demoteChatMember", json={"chat_id": chat_id, "user_id": user_id})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def get_member(self, chat_id, user_id):
        response = await self.client.request("GET", "/getChatMember", params={"chat_id": chat_id, "user_id": user_id})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def get_admins(self, chat_id):
        response = await self.client.request("GET", "/getChatAdministrators", params={"chat_id": chat_id})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def pin(self, chat_id, message_id):
        response = await self.client.request("POST", "/pinChatMessage", json={"chat_id": chat_id, "message_id": message_id})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def unpin(self, chat_id, message_id):
        response = await self.client.request("POST", "/unpinChatMessage", json={"chat_id": chat_id, "message_id": message_id})
        return response.json() if response.status_code == 200 else {"error": "Failed"}