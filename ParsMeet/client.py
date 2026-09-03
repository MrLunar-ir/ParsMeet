import asyncio
import httpx
from .api.auth import AuthAPI
from .api.rooms import RoomsAPI

class Client:
    def __init__(self, token, base_url="https://botapi.codemeet.chat"):
        self.token = token
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._http = httpx.AsyncClient(base_url=base_url, headers={"Authorization": f"Bearer {token}"}, timeout=None)
        self.auth = AuthAPI(self._http, token)
        self.rooms = RoomsAPI(self._http, token, self.loop)

    def _run(self, coro):
        return self.loop.run_until_complete(coro)

    def close(self):
        self._run(self._http.aclose())
        self.loop.close()