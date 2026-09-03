import httpx
import asyncio
import time
from ..exceptions import ParsMeetAuthError, ParsMeetNetworkError

class AuthAPI:
    def __init__(self, client, token):
        self.client = client
        self.token = token

    async def _login(self):
        url = f"/bot{self.token}/getMe"
        for attempt in range(3):
            try:
                response = await self.client.get(url)
                if response.status_code == 200:
                    return response.json().get("result", {}).get("username", "unknown")
                if response.status_code == 401:
                    raise ParsMeetAuthError("Invalid token")
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError):
                if attempt == 2:
                    raise ParsMeetNetworkError("Connection failed")
                time.sleep(1)
        raise ParsMeetNetworkError("Unexpected error")

    def login(self):
        return asyncio.run(self._login())