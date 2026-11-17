from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any
from app.security.session import session_manager
from app.mcp.server import mcp_server

router = APIRouter(prefix="/api/mcp", tags=["Model Context Protocol"])

def verify_session():
    if session_manager.is_locked():
        raise HTTPException(status_code=401, detail="Sessione bloccata.")

@router.get("/tools", dependencies=[Depends(verify_session)])
def get_mcp_tools():
    return {"tools": mcp_server.list_tools()}

@router.post("/rpc", dependencies=[Depends(verify_session)])
async def mcp_json_rpc(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Formato JSON-RPC non valido.")
    response = await mcp_server.handle_json_rpc(body)
    return response
