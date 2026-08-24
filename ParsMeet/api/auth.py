import httpx
import asyncio
from ..exceptions import ParsMeetAuthError

class AuthAPI:
    def __init__(self, client: httpx.AsyncClient, token: str):
        self.client = client
        self.token = token

    async def _login(self) -> str:
        url = f"/bot{self.token}/getMe"
        response = await self.client.get(url)
        if response.status_code == 200:
            return response.json().get("result", {}).get("username", "unknown")
        raise ParsMeetAuthError("Invalid credentials")

    def login(self) -> str:
        return asyncio.run(self._login())