from shared.schemas import Session, Chunk
from shared.config import layer_active

RANK = {"public": 0, "internal": 1, "confidential": 2}
INV_RANK = {0: "public", 1: "internal", 2: "confidential"}

def escalate_sensitivity(current: str, new_val: str) -> str:
    r1 = RANK.get(current, 0)
    r2 = RANK.get(new_val, 0)
    return INV_RANK[max(r1, r2)]

def apply_chunk_to_session(session: Session, chunk: Chunk) -> None:
    session.history.append(chunk)
    session.highest_sensitivity = escalate_sensitivity(session.highest_sensitivity, chunk.sensitivity)
    if layer_active("taint") and chunk.trust == "untrusted":
        session.tainted = True
