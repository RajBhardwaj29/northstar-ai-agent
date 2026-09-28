import os

from dotenv import load_dotenv
from openai import OpenAI

from app.prompts import load_system_prompt
from app.memory import memory
from app.models import LeadState
from app.extractor import update_state_from_message
from app.tools import book_site_visit


# -----------------------------------
# Environment
# -----------------------------------

load_dotenv()


# -----------------------------------
# OpenRouter Client
# -----------------------------------

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


# -----------------------------------
# System Prompt
# -----------------------------------

SYSTEM_PROMPT = load_system_prompt()


# -----------------------------------
# Helper: Structured State Context
# -----------------------------------

def build_state_instruction(state: LeadState) -> str:
    return f"""
Current structured lead state:

{state.model_dump_json(indent=2)}

Use this structured state as conversation memory.

Important rules:
- Do not ask again for information that is already known.
- If the customer changes a preference, use the latest explicit value.
- Never invent information that is not verified.
- Match the language and writing script of the customer's latest message.
- Ask at most one primary question at a time.
"""


# -----------------------------------
# Save helper
# -----------------------------------

def save_exchange(
    session_id: str,
    user_message: str,
    assistant_response: str
) -> None:
    memory.add_message(
        session_id,
        "user",
        user_message
    )

    memory.add_message(
        session_id,
        "assistant",
        assistant_response
    )


# -----------------------------------
# Main Agent
# -----------------------------------

def generate_response(
    session_id: str,
    user_message: str
) -> str:

    # -----------------------------------
    # 1. Read memory
    # -----------------------------------

    history = memory.get_history(session_id)
    state = memory.get_lead_state(session_id)

    # -----------------------------------
    # 2. Extract structured state
    # -----------------------------------

    state = update_state_from_message(
        state,
        user_message
    )

    memory.update_lead_state(
        session_id,
        state
    )

    # -----------------------------------
    # 3. Do Not Contact
    # -----------------------------------

    if state.do_not_contact:

        state.conversation_ended = True

        memory.update_lead_state(
            session_id,
            state
        )

        if state.language == "hinglish":
            assistant_response = (
                "Understood. Main aage aapse contact continue nahi karunga. "
                "Thank you for your time."
            )

        elif state.language == "hindi":
            assistant_response = (
                "समझ गया। आगे आपसे संपर्क जारी नहीं किया जाएगा। धन्यवाद।"
            )

        else:
            assistant_response = (
                "Understood. I won't continue further communication. "
                "Thank you for your time."
            )

        save_exchange(
            session_id,
            user_message,
            assistant_response
        )

        return assistant_response

    # -----------------------------------
    # 4. Existing confirmed booking guard
    # -----------------------------------

    if (
        state.site_visit_status == "booked"
        and state.booking_id
    ):

        if state.language == "hinglish":
            assistant_response = (
                f"Aapka site visit {state.site_visit_date} "
                f"at {state.site_visit_time} confirm hai. "
                f"Booking reference: {state.booking_id}."
            )

        elif state.language == "hindi":
            assistant_response = (
                f"आपका साइट विज़िट {state.site_visit_date} "
                f"{state.site_visit_time} पर कन्फर्म है। "
                f"बुकिंग रेफरेंस: {state.booking_id}।"
            )

        else:
            assistant_response = (
                f"Your site visit is confirmed for "
                f"{state.site_visit_date} at "
                f"{state.site_visit_time}. "
                f"Your booking reference is {state.booking_id}."
            )

        save_exchange(
            session_id,
            user_message,
            assistant_response
        )

        return assistant_response

    # -----------------------------------
    # 5. Site Visit Booking
    # -----------------------------------

    if (
        state.site_visit_requested
        and state.site_visit_status == "pending"
        and state.site_visit_date
        and state.site_visit_time
    ):

        booking_result = book_site_visit(
            state.site_visit_date,
            state.site_visit_time
        )

        # -----------------------------------
        # Booking Success
        # -----------------------------------

        if booking_result["success"]:

            state.site_visit_status = "booked"
            state.booking_id = booking_result["booking_id"]
            state.conversation_ended = True

            memory.update_lead_state(
                session_id,
                state
            )

            if state.language == "hinglish":
                assistant_response = (
                    f"Aapka site visit {booking_result['date']} "
                    f"at {booking_result['time']} confirm ho gaya hai. "
                    f"Booking reference: {booking_result['booking_id']}."
                )

            elif state.language == "hindi":
                assistant_response = (
                    f"आपका साइट विज़िट {booking_result['date']} "
                    f"{booking_result['time']} पर कन्फर्म हो गया है। "
                    f"बुकिंग रेफरेंस: {booking_result['booking_id']}।"
                )

            else:
                assistant_response = (
                    f"Your site visit is confirmed for "
                    f"{booking_result['date']} at "
                    f"{booking_result['time']}. "
                    f"Your booking reference is "
                    f"{booking_result['booking_id']}."
                )

            save_exchange(
                session_id,
                user_message,
                assistant_response
            )

            return assistant_response

        # -----------------------------------
        # Booking Failure
        # -----------------------------------

        state.site_visit_status = "failed"

        memory.update_lead_state(
            session_id,
            state
        )

        if state.language == "hinglish":
            assistant_response = (
                f"Main {booking_result['date']} at "
                f"{booking_result['time']} ka slot confirm nahi kar paya. "
                f"Kya aap koi doosra time try karna chahenge?"
            )

        elif state.language == "hindi":
            assistant_response = (
                f"{booking_result['date']} को "
                f"{booking_result['time']} का स्लॉट कन्फर्म नहीं हो पाया। "
                f"क्या आप कोई दूसरा समय ट्राय करना चाहेंगे?"
            )

        else:
            assistant_response = (
                f"I couldn't confirm the "
                f"{booking_result['date']} at "
                f"{booking_result['time']} slot right now. "
                f"Would you like to try another time?"
            )

        save_exchange(
            session_id,
            user_message,
            assistant_response
        )

        return assistant_response

    # -----------------------------------
    # 6. Build LLM messages
    # -----------------------------------

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": build_state_instruction(state)
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # -----------------------------------
    # 7. Generate natural conversation
    # -----------------------------------

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=messages, # type: ignore
            temperature=0.2,
        )

        assistant_response = (
            response.choices[0].message.content
            or "I'm sorry, I couldn't generate a response."
        )

    except Exception as exc:

        print(f"LLM ERROR: {exc}")

        assistant_response = (
            "I'm having trouble responding right now. "
            "Please try again in a moment."
        )

    # -----------------------------------
    # 8. Save conversation
    # -----------------------------------

    save_exchange(
        session_id,
        user_message,
        assistant_response
    )

    return assistant_response