import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from shared.schemas import Session, ToolCall, Chunk, Verdict
from shared.db import get_joined_events, get_pending_approvals, resolve_approval
from guard.core import ingest_user, tag_result, decide
from redteam.metrics import compute_metrics

app = FastAPI(title="Agent Firewall API")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")

@app.get("/", response_class=FileResponse)
def serve_landing():
    if os.path.exists(INDEX_PATH):
        return FileResponse(INDEX_PATH)
    return {"status": "ok", "service": "Agent Firewall L7 API", "docs": "/docs"}


class ApprovalRequest(BaseModel):
    approve: bool

class GuardInputRequest(BaseModel):
    session: Session
    text: str

class GuardToolCallRequest(BaseModel):
    session: Session
    call: ToolCall

class GuardResultRequest(BaseModel):
    session: Session
    tool: str
    output: str

@app.get("/events")
def list_events():
    return get_joined_events()

@app.get("/approvals")
def list_approvals():
    return get_pending_approvals()

@app.post("/approvals/{approval_id}")
def decide_approval(approval_id: int, req: ApprovalRequest):
    success = resolve_approval(approval_id=approval_id, approve=req.approve)
    if not success:
        raise HTTPException(status_code=404, detail="Approval not found")
    return {
        "success": True,
        "id": approval_id,
        "status": "approved" if req.approve else "denied"
    }

@app.get("/metrics")
def get_metrics(batch_id: str | None = None):
    return compute_metrics(batch_id=batch_id)

@app.post("/guard/input", response_model=Chunk)
def guard_input(req: GuardInputRequest):
    return ingest_user(session=req.session, text=req.text)

@app.post("/guard/tool_call", response_model=Verdict)
def guard_tool_call(req: GuardToolCallRequest):
    return decide(call=req.call, session=req.session)

@app.post("/guard/result", response_model=Chunk)
def guard_result(req: GuardResultRequest):
    return tag_result(session=req.session, tool=req.tool, output=req.output)
