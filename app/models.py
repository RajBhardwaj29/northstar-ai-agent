from typing import Optional, Literal
from pydantic import BaseModel, Field


class LeadState(BaseModel):
    name: Optional[str] = None

    language: Literal[
        "english",
        "hindi",
        "hinglish",
        "unknown"
    ] = "unknown"

    configuration: Optional[Literal[
        "2_bhk",
        "3_bhk"
    ]] = None

    budget: Optional[int] = None

    purchase_purpose: Optional[Literal[
        "end_use",
        "investment",
        "unknown"
    ]] = None

    timeline: Optional[str] = None

    interest_level: Literal[
        "low",
        "medium",
        "high",
        "unknown"
    ] = "unknown"

    site_visit_requested: bool = False

    site_visit_status: Literal[
        "not_requested",
        "pending",
        "booked",
        "failed"
    ] = "not_requested"

    site_visit_date: Optional[str] = None
    site_visit_time: Optional[str] = None
    booking_id: Optional[str] = None

    follow_up_required: bool = False
    follow_up_time: Optional[str] = None

    do_not_contact: bool = False

    human_escalation_required: bool = False

    conversation_ended: bool = False


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    response: str
    session_id: str
    lead_state: LeadState