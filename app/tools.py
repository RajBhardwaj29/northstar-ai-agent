import uuid
from typing import Optional


def book_site_visit(
    preferred_date: str,
    preferred_time: str
) -> dict:
    """
    Simulated site-visit booking tool.

    We intentionally make some slots fail so that
    the agent can demonstrate booking-failure handling.
    """

    normalized_time = preferred_time.lower().strip()

    # Simulated failure slots
    failure_slots = [
        "4 pm",
        "4pm",
        "16:00",
    ]

    if normalized_time in failure_slots:
        return {
            "success": False,
            "status": "failed",
            "reason": "Selected slot could not be confirmed.",
            "date": preferred_date,
            "time": preferred_time,
        }

    booking_id = f"NS-{str(uuid.uuid4())[:6].upper()}"

    return {
        "success": True,
        "status": "booked",
        "booking_id": booking_id,
        "date": preferred_date,
        "time": preferred_time,
    }


def request_human_escalation(
    reason: Optional[str] = None
) -> dict:
    return {
        "success": True,
        "status": "requested",
        "reason": reason or "Customer requested human assistance."
    }