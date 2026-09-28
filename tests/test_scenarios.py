from app.models import LeadState
from app.extractor import update_state_from_message
from app.tools import book_site_visit


def test_3bhk_extraction():
    state = LeadState()

    state = update_state_from_message(
        state,
        "I am looking for a 3 BHK"
    )

    assert state.configuration == "3_bhk"
    assert state.language == "english"


def test_budget_extraction():
    state = LeadState()

    state = update_state_from_message(
        state,
        "My budget is around 2 crore"
    )

    assert state.budget == 20_000_000


def test_hinglish_lead():
    state = LeadState()

    state = update_state_from_message(
        state,
        "3 BHK chahiye, mera budget 2 crore hai aur khud ke liye dekh raha hoon"
    )

    assert state.language == "hinglish"
    assert state.configuration == "3_bhk"
    assert state.budget == 20_000_000
    assert state.purchase_purpose == "end_use"
    assert state.interest_level == "high"


def test_multi_turn_memory_extraction():
    state = LeadState()

    state = update_state_from_message(
        state,
        "I am looking for a 3 BHK"
    )

    state = update_state_from_message(
        state,
        "My budget is around 2 crore"
    )

    state = update_state_from_message(
        state,
        "It is for my own use"
    )

    state = update_state_from_message(
        state,
        "I want to visit on Saturday at 11 AM"
    )

    assert state.configuration == "3_bhk"
    assert state.budget == 20_000_000
    assert state.purchase_purpose == "end_use"

    assert state.site_visit_requested is True
    assert state.site_visit_status == "pending"
    assert state.site_visit_date == "Saturday"
    assert state.site_visit_time == "11 AM"

    assert state.interest_level == "high"


def test_site_visit_intent():
    state = LeadState()

    state = update_state_from_message(
        state,
        "I want to visit on Saturday at 11 AM"
    )

    assert state.site_visit_requested is True
    assert state.site_visit_status == "pending"
    assert state.site_visit_date == "Saturday"
    assert state.site_visit_time == "11 AM"


def test_successful_booking():
    result = book_site_visit(
        "Saturday",
        "11 AM"
    )

    assert result["success"] is True
    assert result["status"] == "booked"
    assert result["booking_id"] is not None


def test_failed_booking():
    result = book_site_visit(
        "Saturday",
        "4 PM"
    )

    assert result["success"] is False
    assert result["status"] == "failed"


def test_do_not_contact():
    state = LeadState()

    state = update_state_from_message(
        state,
        "Please do not call me again"
    )

    assert state.do_not_contact is True
    assert state.conversation_ended is True
    assert state.interest_level == "low"


def test_hinglish_do_not_contact():
    state = LeadState()

    state = update_state_from_message(
        state,
        "Mujhe dobara call mat karna"
    )

    assert state.do_not_contact is True
    assert state.conversation_ended is True


def test_human_escalation():
    state = LeadState()

    state = update_state_from_message(
        state,
        "I want to speak to a real person"
    )

    assert state.human_escalation_required is True


def test_busy_followup():
    state = LeadState()

    state = update_state_from_message(
        state,
        "I'm busy, call later"
    )

    assert state.follow_up_required is True