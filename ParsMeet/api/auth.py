import httpx
import asyncio
from ..exceptions import ParsMeetAuthError

class AuthAPI:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def _login(self, username: str, password: str) -> str:
        token = self.client.headers.get('Authorization', '').replace('Bearer ', '')
        url = f"/bot{token}/getMe"
        response = await self.client.get(url)
        if response.status_code == 200:
            return response.json().get("result", {}).get("username", "unknown")
        raise ParsMeetAuthError("Invalid credentials")

    def login(self, username: str, password: str) -> str:
        return asyncio.run(self._login(username, password))