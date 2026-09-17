import sqlite3
import os
import sys
from datetime import datetime

class Database:
    def __init__(self, db_path="ParsMeetSaveMessage.db"):
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv else os.getcwd()
        self.path = os.path.join(base_dir, db_path)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS messages (chat_id TEXT, text TEXT, timestamp TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT, xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1, warns INTEGER DEFAULT 0)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS chats (chat_id TEXT PRIMARY KEY, welcome_message TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, user_id TEXT, message TEXT, remind_at TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS custom_commands (command TEXT PRIMARY KEY, response TEXT)")
        self.conn.commit()

    def save_message(self, chat_id, text, username=None):
        ts = datetime.now().isoformat()
        self.cursor.execute("INSERT INTO messages (chat_id, text, timestamp) VALUES (?, ?, ?)", (chat_id, text, ts))
        if username:
            self.cursor.execute("INSERT OR IGNORE INTO users (user_id, username, xp, level, warns) VALUES (?, ?, 0, 1, 0)", (chat_id, username))
        self.cursor.execute("INSERT OR IGNORE INTO chats (chat_id) VALUES (?)", (chat_id,))
        self.conn.commit()

    def get_recent_messages(self, chat_id, limit=50):
        self.cursor.execute("SELECT chat_id, text, timestamp FROM messages WHERE chat_id = ? ORDER BY id DESC LIMIT ?", (chat_id, limit))
        rows = self.cursor.fetchall()
        return [{"chat_id": r[0], "text": r[1], "timestamp": r[2]} for r in reversed(rows)]

    def get_all_chat_ids(self):
        self.cursor.execute("SELECT DISTINCT chat_id FROM chats")
        return [row[0] for row in self.cursor.fetchall()]

    def user_exists(self, user_id):
        self.cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone() is not None

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()

    def add_xp(self, user_id, username, amount=10):
        if not self.user_exists(user_id):
            self.cursor.execute("INSERT INTO users (user_id, username, xp, level, warns) VALUES (?, ?, ?, 1, 0)", (user_id, username, amount))
        else:
            self.cursor.execute("UPDATE users SET xp = xp + ?, username = ? WHERE user_id = ?", (amount, username, user_id))
        self.conn.commit()
        return self.get_user(user_id)

    def add_warning(self, user_id):
        self.cursor.execute("UPDATE users SET warns = warns + 1 WHERE user_id = ?", (user_id,))
        self.conn.commit()
        self.cursor.execute("SELECT warns FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        return row[0] if row else 0

    def get_warning_count(self, user_id):
        self.cursor.execute("SELECT warns FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        return row[0] if row else 0

    def clear_warnings(self, user_id):
        self.cursor.execute("UPDATE users SET warns = 0 WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def add_reminder(self, chat_id, user_id, message, remind_at):
        self.cursor.execute("INSERT INTO reminders (chat_id, user_id, message, remind_at) VALUES (?, ?, ?, ?)", (chat_id, user_id, message, remind_at))
        self.conn.commit()

    def get_due_reminders(self):
        now = datetime.now().isoformat()
        self.cursor.execute("SELECT * FROM reminders WHERE remind_at <= ?", (now,))
        return self.cursor.fetchall()

    def delete_reminder(self, reminder_id):
        self.cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        self.conn.commit()

    def set_welcome(self, chat_id, message):
        self.cursor.execute("INSERT OR REPLACE INTO chats (chat_id, welcome_message) VALUES (?, ?)", (chat_id, message))
        self.conn.commit()

    def get_welcome(self, chat_id):
        self.cursor.execute("SELECT welcome_message FROM chats WHERE chat_id = ?", (chat_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def set_custom_command(self, command, response):
        self.cursor.execute("INSERT OR REPLACE INTO custom_commands (command, response) VALUES (?, ?)", (command, response))
        self.conn.commit()

    def get_custom_command(self, command):
        self.cursor.execute("SELECT response FROM custom_commands WHERE command = ?", (command,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def close(self):
        self.conn.close()