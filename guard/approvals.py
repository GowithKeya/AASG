from shared.db import insert_approval, get_pending_approvals, resolve_approval

def create_approval(decision_id: int) -> int:
    return insert_approval(decision_id=decision_id, status="pending")

def list_pending_approvals() -> list[dict]:
    return get_pending_approvals()

def submit_approval(approval_id: int, approve: bool) -> bool:
    return resolve_approval(approval_id=approval_id, approve=approve)
