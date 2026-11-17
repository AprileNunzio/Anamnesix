from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.security.session import session_manager
from app.rag.clinical_rag import clinical_rag_engine

router = APIRouter(prefix="/api/chat", tags=["Chat Clinica RAG"])

def verify_session():
    if session_manager.is_locked():
        raise HTTPException(status_code=401, detail="Sessione bloccata.")

class ChatQueryRequest(BaseModel):
    query: str
    profile_id: Optional[str] = None

@router.post("/query", dependencies=[Depends(verify_session)])
async def clinical_chat_query(req: ChatQueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Domanda vuota.")
    try:
        response = await clinical_rag_engine.answer_query(
            query=req.query,
            profile_id=req.profile_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore elaborazione query RAG: {str(e)}")
