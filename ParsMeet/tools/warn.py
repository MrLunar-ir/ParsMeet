class WarnSystem:
    def __init__(self, db, max_warns=3):
        self.db = db
        self.max_warns = max_warns

    def warn(self, bot, chat_id, user_id):
        count = self.db.add_warning(user_id)
        if count >= self.max_warns:
            bot.ban_user(chat_id, user_id)
            self.db.clear_warnings(user_id)
            return {"status": "banned", "count": count}
        return {"status": "warned", "count": count}

    def reset(self, user_id):
        self.db.clear_warnings(user_id)

    def get_count(self, user_id):
        return self.db.get_warning_count(user_id)