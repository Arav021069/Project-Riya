import sqlite3
# import os
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_folder = Path.home() / ".riya"
        self.db_folder.mkdir(parents=True, exist_ok=True)
        
        filename = db_path if db_path else "riya.db"
        self.db_path = str(self.db_folder / filename)

    def _get_connection(self):
        """Creates a connection with foreign key support enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        """Initializes the database with necessary tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Table for chat sessions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Table for messages, linked to sessions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
        )
        """)
        
        conn.commit()
        conn.close()

    def create_session(self, session_id: str, title: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO sessions (id, title) VALUES (?, ?)",
            (session_id, title)
        )
        conn.commit()
        conn.close()

    def get_all_sessions(self):
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, timestamp FROM sessions ORDER BY timestamp DESC")
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sessions

    def get_messages(self, session_id: str):
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,)
        )
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return messages

    def add_message(self, session_id: str, role: str, content: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()
        conn.close()

    def delete_session(self, session_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()
