import os
import httpx
from shared.db import get_joined_events, get_pending_approvals, resolve_approval as db_resolve_approval
from redteam.metrics import compute_metrics
from redteam.runner import run_suite as runner_run_suite
from agent.agent import run_agent

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def fetch_events() -> list[dict]:
    try:
        res = httpx.get(f"{API_URL}/events", timeout=2.0)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return get_joined_events()

def fetch_approvals() -> list[dict]:
    try:
        res = httpx.get(f"{API_URL}/approvals", timeout=2.0)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return get_pending_approvals()

def submit_approval(approval_id: int, approve: bool) -> bool:
    try:
        res = httpx.post(f"{API_URL}/approvals/{approval_id}", json={"approve": approve}, timeout=2.0)
        if res.status_code == 200:
            return True
    except Exception:
        pass
    return db_resolve_approval(approval_id=approval_id, approve=approve)

def fetch_metrics(batch_id: str | None = None) -> dict:
    try:
        params = {"batch_id": batch_id} if batch_id else {}
        res = httpx.get(f"{API_URL}/metrics", params=params, timeout=2.0)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return compute_metrics(batch_id=batch_id)

def trigger_suite(guard_on: bool) -> str:
    return runner_run_suite(guard_on=guard_on)

def run_task(task: str, guard_on: bool, doc: str | None = None):
    return run_agent(task=task, guard_on=guard_on, doc=doc)
