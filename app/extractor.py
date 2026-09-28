import re
from app.models import LeadState


def detect_language(message: str) -> str:
    if re.search(r"[\u0900-\u097F]", message):
        return "hindi"

    text = message.lower()

    hinglish_words = [
        "chahiye",
        "kya",
        "hai",
        "ka",
        "ki",
        "mein",
        "mera",
        "meri",
        "mujhe",
        "dekh",
        "karna",
        "nahi",
        "khud",
        "liye",
        "budget",
        "crore",
        "lakh",
    ]

    matches = sum(
        1
        for word in hinglish_words
        if re.search(rf"\b{re.escape(word)}\b", text)
    )

    return "hinglish" if matches >= 2 else "english"


def extract_budget(message: str):
    text = message.lower().replace(",", "")

    crore_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:crore|crores|cr)\b",
        text
    )

    if crore_match:
        value = float(crore_match.group(1))
        return int(value * 10_000_000)

    lakh_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs)\b",
        text
    )

    if lakh_match:
        value = float(lakh_match.group(1))
        return int(value * 100_000)

    return None


def update_state_from_message(
    state: LeadState,
    message: str
) -> LeadState:

    text = message.lower().strip()

    # -----------------------------------
    # LANGUAGE
    # -----------------------------------

    state.language = detect_language(message) # type: ignore

    # -----------------------------------
    # CONFIGURATION
    # -----------------------------------

    if re.search(r"\b2\s*bhk\b", text):
        state.configuration = "2_bhk"

    elif re.search(r"\b3\s*bhk\b", text):
        state.configuration = "3_bhk"

    # -----------------------------------
    # BUDGET
    # -----------------------------------

    budget = extract_budget(message)

    if budget is not None:
        state.budget = budget

    # -----------------------------------
    # PURCHASE PURPOSE
    # -----------------------------------

    investment_terms = [
        "investment",
        "invest",
        "investing",
        "for investment",
        "rental income",
        "rental purpose",
        "rental",
    ]

    end_use_terms = [
        "self use",
        "self-use",
        "own use",
        "my own use",
        "for my own use",
        "for own use",
        "end use",
        "end-use",
        "for myself",
        "for my family",
        "personal use",
        "khud ke liye",
        "khud ke use ke liye",
        "family ke liye",
        "rehne ke liye",
    ]

    if any(term in text for term in investment_terms):
        state.purchase_purpose = "investment"

    elif any(term in text for term in end_use_terms):
        state.purchase_purpose = "end_use"

    # -----------------------------------
    # DO NOT CONTACT
    # -----------------------------------

    dnc_terms = [
        "stop calling",
        "stop messaging",
        "don't call",
        "do not call",
        "dont call",
        "don't message",
        "do not message",
        "dont message",
        "don't contact",
        "do not contact",
        "dont contact",
        "remove my number",
        "call mat karna",
        "message mat karna",
        "contact mat karna",
        "dobara call mat karna",
        "dobara contact mat karna",
    ]

    if any(term in text for term in dnc_terms):
        state.do_not_contact = True
        state.conversation_ended = True
        state.interest_level = "low"

        return state

    # -----------------------------------
    # UNINTERESTED
    # -----------------------------------

    negative_terms = [
        "not interested",
        "no interest",
        "i am not interested",
        "interested nahi",
        "nahi chahiye",
    ]

    if any(term in text for term in negative_terms):
        state.interest_level = "low"
        state.conversation_ended = True

    # -----------------------------------
    # SITE VISIT INTENT
    # -----------------------------------

    site_visit_terms = [
        "site visit",
        "book a visit",
        "book visit",
        "schedule a visit",
        "schedule visit",
        "want to visit",
        "would like to visit",
        "like to visit",
        "i want to visit",
        "i'd like to visit",
        "visit the project",
        "visit project",
        "visit the property",
        "visit property",
        "come and see",
        "see the property",
        "see the project",
        "visit karna",
        "dekhne aana",
        "property dekhna",
        "project dekhna",
    ]

    if any(term in text for term in site_visit_terms):
        state.site_visit_requested = True

        if state.site_visit_status in [
            "not_requested",
            "failed"
        ]:
            state.site_visit_status = "pending"

    # -----------------------------------
    # SITE VISIT DATE
    # -----------------------------------

    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        "today",
        "tomorrow",
    ]

    for day in days:
        if re.search(rf"\b{day}\b", text):
            state.site_visit_date = day.capitalize()
            break

    # -----------------------------------
    # SITE VISIT TIME
    # -----------------------------------

    time_match = re.search(
        r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b",
        text
    )

    if time_match:
        hour = time_match.group(1)
        minute = time_match.group(2)
        period = time_match.group(3).upper()

        if minute:
            state.site_visit_time = f"{hour}:{minute} {period}"
        else:
            state.site_visit_time = f"{hour} {period}"

    # -----------------------------------
    # BUSY / FOLLOW-UP
    # -----------------------------------

    busy_terms = [
        "call later",
        "contact later",
        "message later",
        "busy",
        "i am busy",
        "i'm busy",
        "in a meeting",
        "meeting mein",
        "baad mein call",
        "later call",
    ]

    if any(term in text for term in busy_terms):
        state.follow_up_required = True

    follow_up_patterns = [
        r"tomorrow(?:\s+\w+)?",
        r"today(?:\s+\w+)?",
        r"after\s+\d+(?::\d+)?\s*(?:am|pm)?",
        r"next week",
        r"this weekend",
        r"weekend",
        r"kal(?:\s+\w+)?",
        r"shaam(?:\s+\w+)?",
        r"subah(?:\s+\w+)?",
    ]

    for pattern in follow_up_patterns:
        match = re.search(pattern, text)

        if match:
            state.follow_up_required = True
            state.follow_up_time = match.group(0)
            break

    # -----------------------------------
    # HUMAN ESCALATION
    # -----------------------------------

    human_terms = [
        "human",
        "real person",
        "salesperson",
        "sales person",
        "sales executive",
        "talk to a person",
        "speak to a person",
        "talk to someone",
        "someone from your team",
        "agent se baat",
        "person se baat",
    ]

    if any(term in text for term in human_terms):
        state.human_escalation_required = True

    # -----------------------------------
    # INTEREST LEVEL
    # -----------------------------------

    if state.do_not_contact or state.conversation_ended:
        state.interest_level = "low"

    elif state.site_visit_requested:
        state.interest_level = "high"

    elif (
        state.configuration is not None
        and state.budget is not None
        and state.purchase_purpose not in [None, "unknown"]
    ):
        state.interest_level = "high"

    elif (
        state.configuration is not None
        and state.budget is not None
    ):
        state.interest_level = "medium"

    elif (
        state.configuration is not None
        or state.budget is not None
    ):
        state.interest_level = "medium"

    return state