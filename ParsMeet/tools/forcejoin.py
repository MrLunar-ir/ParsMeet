class ForceJoin:
    def __init__(self, required_chats=None):
        self.required_chats = required_chats or []

    def add(self, chat_id):
        if chat_id not in self.required_chats:
            self.required_chats.append(chat_id)

    def remove(self, chat_id):
        if chat_id in self.required_chats:
            self.required_chats.remove(chat_id)

    def check(self, bot, user_id):
        for chat in self.required_chats:
            try:
                result = bot.get_chat_member(chat, user_id)
                status = result.get("result", {}).get("status", "")
                if status not in ["member", "administrator", "creator"]:
                    return False
            except Exception:
                return False
        return True