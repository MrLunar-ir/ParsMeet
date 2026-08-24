import httpx
import asyncio
from .api.auth import AuthAPI
from .api.rooms import RoomsAPI

class Client:
    def __init__(self, api_key: str, base_url: str = "https://botapi.codemeet.chat"):
        self.api_key = api_key
        self.base_url = base_url
        self._http_client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        self.auth = AuthAPI(self._http_client)
        self.rooms = RoomsAPI(self._http_client)

    def _run(self, coro):
        return asyncio.run(coro)

    def close(self):
        return self._run(self._http_client.aclose())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()