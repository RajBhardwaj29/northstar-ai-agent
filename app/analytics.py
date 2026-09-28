from app.models import LeadState
from app.memory import memory


def calculate_lead_score(state: LeadState) -> int:
    score = 0

    if state.configuration:
        score += 20

    if state.budget:
        score += 20

    if (
        state.purchase_purpose
        and state.purchase_purpose != "unknown"
    ):
        score += 15

    if state.timeline:
        score += 15

    if state.site_visit_requested:
        score += 15

    if state.site_visit_status == "booked":
        score += 15

    if state.do_not_contact:
        score = 0

    return min(score, 100)


def get_interest_label(score: int) -> str:
    if score >= 70:
        return "high"

    if score >= 40:
        return "medium"

    return "low"


def generate_analytics(session_id: str) -> dict:
    state = memory.get_lead_state(session_id)
    history = memory.get_history(session_id)

    score = calculate_lead_score(state)

    return {
        "session_id": session_id,

        "lead": {
            "name": state.name,
            "configuration": state.configuration,
            "budget": state.budget,
            "purchase_purpose": state.purchase_purpose,
            "timeline": state.timeline,
        },

        "qualification": {
            "lead_score": score,
            "interest_level": get_interest_label(score),
        },

        "conversation": {
            "language": state.language,
            "message_count": len(history),
            "conversation_ended": state.conversation_ended,
        },

        "site_visit": {
            "requested": state.site_visit_requested,
            "status": state.site_visit_status,
            "date": state.site_visit_date,
            "time": state.site_visit_time,
            "booking_id": state.booking_id,
        },

        "follow_up": {
            "required": state.follow_up_required,
            "preferred_time": state.follow_up_time,
        },

        "compliance": {
            "do_not_contact": state.do_not_contact,
            "human_escalation_required": (
                state.human_escalation_required
            ),
        },
    }