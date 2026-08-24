import sqlite3
import os
import sys
from datetime import datetime

class Database:
    def __init__(self, db_name="ParsMeetSaveMessage.db"):
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv else os.getcwd()
        self.path = os.path.join(base_dir, db_name)
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT,
                text TEXT,
                timestamp TEXT
            )
        """)
        self.conn.commit()

    def save_message(self, chat_id, text):
        ts = datetime.now().isoformat()
        self.cursor.execute("INSERT INTO messages (chat_id, text, timestamp) VALUES (?, ?, ?)", (chat_id, text, ts))
        self.conn.commit()

    def get_all_chat_ids(self):
        self.cursor.execute("SELECT DISTINCT chat_id FROM messages")
        return [row[0] for row in self.cursor.fetchall()]

    def user_exists(self, chat_id):
        self.cursor.execute("SELECT 1 FROM messages WHERE chat_id = ? LIMIT 1", (chat_id,))
        return self.cursor.fetchone() is not None

    def close(self):
        self.conn.close()