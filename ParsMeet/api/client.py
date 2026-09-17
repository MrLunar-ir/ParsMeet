import httpx
import asyncio
from ..exceptions import NetworkError

class APIClient:
    def __init__(self, base_url, token, timeout=30, retries=3, backoff=2.0):
        self.token = token
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self.http = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def request(self, method, path, **kwargs):
        url = f"/bot{self.token}{path}"
        last_error = None
        for attempt in range(self.retries):
            try:
                response = await self.http.request(method, url, **kwargs)
                if response.status_code < 500:
                    return response
                last_error = f"Server error: {response.status_code}"
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError, httpx.RemoteProtocolError) as e:
                last_error = str(e)
            if attempt < self.retries - 1:
                await asyncio.sleep(self.backoff ** attempt)
        raise NetworkError(f"Request failed: {last_error}")

    async def close(self):
        await self.http.aclose()