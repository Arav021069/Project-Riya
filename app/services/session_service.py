from app.db.manager import DatabaseManager

class SessionService:
    def __init__(self):
        self.db = DatabaseManager()

    def create_new_session(self, session_id: str, title: str):
        """Creates a new chat session entry in the database."""
        self.db.create_session(session_id, title)

    def list_all_sessions(self):
        """Retrieves all stored chat sessions."""
        return self.db.get_all_sessions()

    def get_session_history(self, session_id: str):
        """Retrieves the message history for a specific session."""
        return self.db.get_messages(session_id)

    def save_message(self, session_id: str, role: str, content: str):
        """Saves a single message to a session."""
        self.db.add_message(session_id, role, content)

    def remove_session(self, session_id: str):
        """Deletes a session and all its associated messages."""
        self.db.delete_session(session_id)
