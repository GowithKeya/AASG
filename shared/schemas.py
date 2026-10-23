from typing import Any, Literal
from pydantic import BaseModel, Field

Trust = Literal["trusted", "untrusted"]
Sensitivity = Literal["public", "internal", "confidential"]
Action = Literal["ALLOW", "BLOCK", "NEEDS_APPROVAL"]

class Chunk(BaseModel):
    id: str
    text: str
    trust: str
    sensitivity: str
    source: str
    quarantined: bool = False

class Session(BaseModel):
    id: str
    started_at: str
    guard_mode: str
    task: str
    tainted: bool = False
    highest_sensitivity: str = "public"
    history: list[Chunk] = Field(default_factory=list)

class ToolCall(BaseModel):
    tool: str
    args: dict[str, Any]
    call_id: str | None = None

class Verdict(BaseModel):
    action: str
    rule_id: str
    explanation: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0

class LeakResult(BaseModel):
    found: bool
    matches: list[str] = Field(default_factory=list)
    category: str | None = None

class ExecutedCall(BaseModel):
    tool: str
    args: dict[str, Any]
    executed: bool
    output: str | None = None
    verdict: Verdict | None = None

class RunResult(BaseModel):
    session_id: str
    task: str
    final_output: str
    executed_calls: list[ExecutedCall] = Field(default_factory=list)
    tainted: bool = False
    guard_on: bool = True
    latency_ms: float = 0.0

class LLMReply(BaseModel):
    content: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)

class Event(BaseModel):
    id: int | None = None
    session_id: str
    ts: str
    type: str
    tool: str | None = None
    args_json: str | None = None
    trust: str | None = None
    sensitivity: str | None = None
    content_preview: str | None = None

class Decision(BaseModel):
    id: int | None = None
    event_id: int
    verdict: str
    rule_id: str
    evidence_json: str | None = None
    explanation: str
    latency_ms: float = 0.0

class Approval(BaseModel):
    id: int | None = None
    decision_id: int
    status: str
    created_at: str
    resolved_at: str | None = None

class RunRecord(BaseModel):
    id: int | None = None
    batch_id: str
    item_id: str
    kind: str
    guard_mode: str
    attack_succeeded: int
    task_completed: int
    any_block: int
    latency_ms: float
    layers: str
