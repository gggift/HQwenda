import uuid


class SessionManager:
    def __init__(self, max_rounds: int = 20):
        self._sessions: dict[str, list[dict]] = {}
        self._max_rounds = max_rounds

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = []
        return session_id

    def get_history(self, session_id: str) -> list[dict]:
        return list(self._sessions.get(session_id, []))

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({"role": role, "content": content})
        max_messages = self._max_rounds * 2
        if len(self._sessions[session_id]) > max_messages:
            self._sessions[session_id] = self._sessions[session_id][-max_messages:]

    def delete_session(self, session_id: str):
        self._sessions.pop(session_id, None)
