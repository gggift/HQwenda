from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.core import run_agent
from app.agent.context import assemble_context
from app.session.manager import SessionManager
from app.knowledge.loader import KnowledgeLoader

router = APIRouter()

session_manager = SessionManager()
knowledge_loader = KnowledgeLoader("app/knowledge/docs")


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    session_id: str


class SessionResponse(BaseModel):
    session_id: str


# Use sync def (not async def) so FastAPI runs it in a threadpool.
# run_agent and assemble_context make blocking HTTP calls to DeepSeek/Tushare.
@router.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    system_prompt, messages = assemble_context(
        req.message, req.session_id, session_manager, knowledge_loader
    )
    reply = run_agent(system_prompt, messages)

    # Save to session history
    session_manager.add_message(req.session_id, "user", req.message)
    session_manager.add_message(req.session_id, "assistant", reply)

    return ChatResponse(reply=reply, session_id=req.session_id)


@router.post("/api/session/new")
def new_session():
    session_id = session_manager.create_session()
    return SessionResponse(session_id=session_id)


@router.delete("/api/session/{session_id}")
def delete_session(session_id: str):
    session_manager.delete_session(session_id)
    return {"status": "ok"}
