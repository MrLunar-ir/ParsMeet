import asyncio
import httpx

class UpdatesAPI:
    def __init__(self, client):
        self.client = client

    async def get_updates(self, offset=0, timeout=30, limit=100, allowed_updates=None):
        params = {"timeout": timeout, "offset": offset, "limit": limit}
        if allowed_updates:
            params["allowed_updates"] = allowed_updates
        response = await self.client.request("GET", "/getUpdates", params=params)
        if response.status_code == 200:
            return response.json().get("result", [])
        return []

    async def get_updates_safe(self, offset=0, timeout=30, limit=100, max_retries=3):
        last_error = None
        for attempt in range(max_retries):
            try:
                return await self.get_updates(offset, timeout, limit)
            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError, httpx.RemoteProtocolError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                last_error = e
                await asyncio.sleep(1)
        return []

    async def set_webhook(self, url, secret=None):
        payload = {"url": url}
        if secret:
            payload["secret_token"] = secret
        response = await self.client.request("POST", "/setWebhook", json=payload)
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def delete_webhook(self):
        response = await self.client.request("POST", "/deleteWebhook")
        return response.json() if response.status_code == 200 else {"error": "Failed"}

    async def get_webhook_info(self):
        response = await self.client.request("GET", "/getWebhookInfo")
        return response.json() if response.status_code == 200 else {"error": "Failed"}