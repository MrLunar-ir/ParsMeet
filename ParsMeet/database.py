import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="ParsMeetSaveMessage.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
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
        timestamp = datetime.now().isoformat()
        self.cursor.execute("INSERT INTO messages (chat_id, text, timestamp) VALUES (?, ?, ?)", (chat_id, text, timestamp))
        self.conn.commit()

    def get_all_messages(self):
        self.cursor.execute("SELECT * FROM messages ORDER BY id DESC")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()