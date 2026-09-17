class AdminAPI:
    def __init__(self, client):
        self.client = client

    async def set_commands(self, commands):
        response = await self.client.request("POST", "/setMyCommands", json={"commands": commands})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def get_commands(self):
        response = await self.client.request("GET", "/getMyCommands")
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def delete_commands(self):
        response = await self.client.request("POST", "/deleteMyCommands")
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def set_name(self, name):
        response = await self.client.request("POST", "/setMyName", json={"name": name})
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def set_description(self, description):
        response = await self.client.request("POST", "/setMyDescription", json={"description": description})
        return response.json() if response.status_code == 200 else {"error": "Failed"}