from ..exceptions import AuthError

class AuthAPI:
    def __init__(self, client):
        self.client = client

    async def get_me(self):
        response = await self.client.request("GET", "/getMe")
        if response.status_code == 200:
            return response.json().get("result", {})
        if response.status_code == 401:
            raise AuthError("Invalid token")
        return {}

    async def log_out(self):
        response = await self.client.request("POST", "/logOut")
        return response.json() if response.status_code == 200 else {"error": "Failed"}