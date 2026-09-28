from typing import Dict, List
from app.models import LeadState


class SessionMemory:
    def __init__(self):
        self.conversations: Dict[str, List[dict]] = {}
        self.lead_states: Dict[str, LeadState] = {}

    def get_history(self, session_id: str) -> List[dict]:
        if session_id not in self.conversations:
            self.conversations[session_id] = []

        return self.conversations[session_id]

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:
        history = self.get_history(session_id)

        history.append({
            "role": role,
            "content": content
        })

    def get_lead_state(self, session_id: str) -> LeadState:
        if session_id not in self.lead_states:
            self.lead_states[session_id] = LeadState()

        return self.lead_states[session_id]

    def update_lead_state(
        self,
        session_id: str,
        state: LeadState
    ) -> None:
        self.lead_states[session_id] = state

    def clear_session(self, session_id: str) -> None:
        self.conversations.pop(session_id, None)
        self.lead_states.pop(session_id, None)


memory = SessionMemory()