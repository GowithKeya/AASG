import time
import json
import uuid
from shared.schemas import Session, Chunk, ToolCall, Verdict, LeakResult
from shared.config import layer_active, INJECTION_THRESHOLD, QUARANTINE_PLACEHOLDER
from shared.db import insert_session, insert_event, insert_decision, insert_approval
from detectors.injection import injection_score
from detectors.leak import leak_check
from guard.taint import apply_chunk_to_session
from guard.policy import is_tool_allowed, is_always_approve, is_sink, get_sink_destination, is_domain_allowed
from guard.explain import explain_decision

def ingest_user(session: Session, text: str) -> Chunk:
    insert_session(session.id, session.started_at, session.guard_mode, session.task)
    score = injection_score(text) if layer_active("injection") else 0.0
    if layer_active("injection") and score >= INJECTION_THRESHOLD:
        chunk = Chunk(
            id=str(uuid.uuid4())[:8],
            text=QUARANTINE_PLACEHOLDER,
            trust="untrusted",
            sensitivity="public",
            source="user",
            quarantined=True
        )
        apply_chunk_to_session(session, chunk)
        insert_event(
            session_id=session.id,
            event_type="input",
            tool=None,
            args_json=None,
            trust="untrusted",
            sensitivity="public",
            content_preview=f"[QUARANTINED score={score:.2f}] {text[:60]}"
        )
        return chunk

    chunk = Chunk(
        id=str(uuid.uuid4())[:8],
        text=text,
        trust="trusted",
        sensitivity="public",
        source="user",
        quarantined=False
    )
    apply_chunk_to_session(session, chunk)
    insert_event(
        session_id=session.id,
        event_type="input",
        tool=None,
        args_json=None,
        trust="trusted",
        sensitivity="public",
        content_preview=text[:100]
    )
    return chunk

def tag_result(session: Session, tool: str, output: str) -> Chunk:
    trust = "untrusted" if tool == "read_doc" else "trusted"
    if tool == "read_doc":
        out_lower = output.lower()
        sensitivity = "confidential" if "confidential" in out_lower or "secret" in out_lower else "internal"
    elif tool == "search_records":
        leak = leak_check(output)
        out_lower = output.lower()
        if leak.found or "ssn" in out_lower or "secret" in out_lower or "salary" in out_lower:
            sensitivity = "confidential"
        else:
            sensitivity = "internal"
    else:
        sensitivity = "internal"

    score = injection_score(output) if (layer_active("injection") and tool == "read_doc") else 0.0
    if layer_active("injection") and tool == "read_doc" and score >= INJECTION_THRESHOLD:
        quarantined = True
        text_val = QUARANTINE_PLACEHOLDER
        trust = "untrusted"
    else:
        quarantined = False
        text_val = output

    chunk = Chunk(
        id=str(uuid.uuid4())[:8],
        text=text_val,
        trust=trust,
        sensitivity=sensitivity,
        source=f"tool:{tool}",
        quarantined=quarantined
    )
    apply_chunk_to_session(session, chunk)
    preview = f"[QUARANTINED score={score:.2f}] {output[:60]}" if quarantined else output[:100]
    insert_event(
        session_id=session.id,
        event_type="result",
        tool=tool,
        args_json=None,
        trust=trust,
        sensitivity=sensitivity,
        content_preview=preview
    )
    return chunk

def decide(call: ToolCall, session: Session) -> Verdict:
    start_time = time.perf_counter()
    event_id = insert_event(
        session_id=session.id,
        event_type="tool_call",
        tool=call.tool,
        args_json=json.dumps(call.args),
        trust=None,
        sensitivity=None,
        content_preview=json.dumps(call.args)[:100]
    )

    action = "ALLOW"
    rule_id = "default_allow"
    evidence = {}
    dest = get_sink_destination(call.tool, call.args) if is_sink(call.tool) else None
    leak_res = leak_check(json.dumps(call.args)) if layer_active("leak") else LeakResult(found=False, matches=[], category=None)
    tainted = session.tainted and layer_active("taint")

    if layer_active("policy") and not is_tool_allowed(call.tool):
        action = "BLOCK"
        rule_id = "permission_denied"
        evidence = {"tool": call.tool}
    elif layer_active("policy") and is_always_approve(call.tool):
        action = "NEEDS_APPROVAL"
        rule_id = "always_approve"
        evidence = {"tool": call.tool}
    elif layer_active("policy") and is_sink(call.tool) and not is_domain_allowed(dest):
        action = "BLOCK"
        if leak_res.found:
            rule_id = "leak_to_external"
            evidence = {"destination": dest, "leak": leak_res.model_dump()}
        else:
            rule_id = "destination_not_allowed"
            evidence = {"destination": dest}
    elif is_sink(call.tool) and leak_res.found and tainted:
        action = "BLOCK"
        rule_id = "leak_while_tainted"
        evidence = {"leak": leak_res.model_dump(), "tainted": True}
    elif is_sink(call.tool) and tainted and session.highest_sensitivity == "confidential":
        action = "NEEDS_APPROVAL"
        rule_id = "untrusted_influence_on_sink"
        evidence = {"tainted": True, "sensitivity": session.highest_sensitivity}
    else:
        action = "ALLOW"
        rule_id = "default_allow"

    latency_ms = (time.perf_counter() - start_time) * 1000.0
    explanation = explain_decision(
        rule_id=rule_id,
        tool=call.tool,
        destination=dest,
        leak_found=leak_res.found,
        matches=leak_res.matches,
        tainted=tainted,
        highest_sensitivity=session.highest_sensitivity
    )

    dec_id = insert_decision(
        event_id=event_id,
        verdict=action,
        rule_id=rule_id,
        evidence_json=json.dumps(evidence),
        explanation=explanation,
        latency_ms=latency_ms
    )

    if action == "NEEDS_APPROVAL":
        insert_approval(decision_id=dec_id, status="pending")

    return Verdict(
        action=action,
        rule_id=rule_id,
        explanation=explanation,
        evidence=evidence,
        latency_ms=latency_ms
    )
