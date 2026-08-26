import sqlite3
import os
import sys
from datetime import datetime

class Database:
    def __init__(self, name="ParsMeetSaveMessage.db"):
        base = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv else os.getcwd()
        self.path = os.path.join(base, name)
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS msgs (id INTEGER PRIMARY KEY, chat TEXT, text TEXT, ts TEXT)")
        self.conn.commit()

    def save(self, chat, text):
        self.c.execute("INSERT INTO msgs (chat, text, ts) VALUES (?,?,?)", (chat, text, datetime.now().isoformat()))
        self.conn.commit()

    def chats(self):
        self.c.execute("SELECT DISTINCT chat FROM msgs")
        return [r[0] for r in self.c.fetchall()]

    def has(self, chat):
        self.c.execute("SELECT 1 FROM msgs WHERE chat=? LIMIT 1", (chat,))
        return self.c.fetchone() is not None

    def close(self):
        self.conn.close()