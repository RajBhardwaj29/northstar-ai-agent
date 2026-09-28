from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent import generate_response
from app.memory import memory
from app.models import ChatRequest, ChatResponse
from app.analytics import generate_analytics
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="Northstar AI Sales Agent",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return FileResponse(
        "static/index.html"
    )


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = generate_response(
        session_id=request.session_id,
        user_message=request.message
    )

    state = memory.get_lead_state(
        request.session_id
    )

    return ChatResponse(
        response=response,
        session_id=request.session_id,
        lead_state=state
    )


@app.get("/session/{session_id}")
def get_session(session_id: str):
    return {
        "session_id": session_id,
        "lead_state": memory.get_lead_state(session_id),
        "history": memory.get_history(session_id)
    }


@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    memory.clear_session(session_id)

    return {
        "status": "cleared",
        "session_id": session_id
    }
@app.get("/analytics/{session_id}")
def analytics(session_id: str):
    return generate_analytics(session_id)