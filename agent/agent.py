import time
import uuid
from datetime import datetime, timezone
from shared.schemas import Session, Chunk, ExecutedCall, RunResult, Verdict
from shared.db import insert_session
from agent.llm import chat
from agent.tools import execute_tool, TOOL_REGISTRY
from guard.core import ingest_user, tag_result, decide

def run_agent(task: str, guard_on: bool, approval_mode: str = "auto_deny", doc: str | None = None) -> RunResult:
    start_time = time.perf_counter()
    session_id = f"sess_{uuid.uuid4().hex[:10]}"
    started_at = datetime.now(timezone.utc).isoformat()
    guard_mode = "guard_on" if guard_on else "guard_off"

    session = Session(
        id=session_id,
        started_at=started_at,
        guard_mode=guard_mode,
        task=task,
        tainted=False,
        highest_sensitivity="public",
        history=[]
    )
    insert_session(session.id, session.started_at, session.guard_mode, session.task)

    full_prompt = f"{task}\nDocument: {doc}" if doc else task

    if guard_on:
        user_chunk = ingest_user(session, full_prompt)
    else:
        user_chunk = Chunk(
            id=str(uuid.uuid4())[:8],
            text=full_prompt,
            trust="untrusted" if doc else "trusted",
            sensitivity="public",
            source="user"
        )
        session.history.append(user_chunk)

    executed_calls: list[ExecutedCall] = []
    final_output = ""
    tools_schema = [{"name": name} for name in TOOL_REGISTRY]

    for _ in range(5):
        messages = [{"role": "user", "content": user_chunk.text}]
        for ec in executed_calls:
            messages.append({
                "role": "assistant",
                "content": f"Calling {ec.tool} with args {ec.args}",
                "name": ec.tool
            })
            messages.append({
                "role": "tool",
                "name": ec.tool,
                "content": ec.output or ""
            })

        reply = chat(messages=messages, tools=tools_schema)

        if not reply.tool_calls:
            final_output = reply.content or "Task completed."
            break

        for call in reply.tool_calls:
            if guard_on:
                verdict = decide(call, session)
                if verdict.action == "ALLOW":
                    can_run = True
                elif verdict.action == "NEEDS_APPROVAL":
                    can_run = (approval_mode == "auto_approve")
                else:
                    can_run = False
            else:
                verdict = Verdict(
                    action="ALLOW",
                    rule_id="guard_off",
                    explanation="Firewall disabled",
                    evidence={},
                    latency_ms=0.0
                )
                can_run = True

            if can_run:
                try:
                    output = execute_tool(call.tool, call.args)
                    executed = True
                except Exception as e:
                    output = str(e)
                    executed = False
            else:
                output = f"[BLOCKED] {verdict.explanation}"
                executed = False

            ec = ExecutedCall(
                tool=call.tool,
                args=call.args,
                executed=executed,
                output=output,
                verdict=verdict
            )
            executed_calls.append(ec)

            if guard_on:
                tag_result(session, call.tool, output)
            else:
                out_chunk = Chunk(
                    id=str(uuid.uuid4())[:8],
                    text=output,
                    trust="untrusted" if call.tool == "read_doc" else "trusted",
                    sensitivity="confidential" if "ssn" in output.lower() else "internal",
                    source=f"tool:{call.tool}"
                )
                session.history.append(out_chunk)
                if call.tool == "read_doc":
                    session.tainted = True

    total_latency_ms = (time.perf_counter() - start_time) * 1000.0
    return RunResult(
        session_id=session.id,
        task=task,
        final_output=final_output,
        executed_calls=executed_calls,
        tainted=session.tainted,
        guard_on=guard_on,
        latency_ms=total_latency_ms
    )
