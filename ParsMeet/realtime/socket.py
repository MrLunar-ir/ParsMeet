import websockets

class RealtimeClient:
    def __init__(self, room_id: str, token: str):
        self.room_id = room_id
        self.token = token

    async def connect(self):
        uri = f"wss://botapi.codemeet.chat/ws/{self.room_id}?token={self.token}"
        async with websockets.connect(uri) as websocket:
            print(f"Connected to room {self.room_id}")