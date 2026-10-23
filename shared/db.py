import sqlite3
import json
from datetime import datetime, timezone
from shared.config import DB_PATH

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        started_at TEXT,
        guard_mode TEXT,
        task TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        ts TEXT,
        type TEXT,
        tool TEXT,
        args_json TEXT,
        trust TEXT,
        sensitivity TEXT,
        content_preview TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        verdict TEXT,
        rule_id TEXT,
        evidence_json TEXT,
        explanation TEXT,
        latency_ms REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        decision_id INTEGER,
        status TEXT,
        created_at TEXT,
        resolved_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT,
        item_id TEXT,
        kind TEXT,
        guard_mode TEXT,
        attack_succeeded INTEGER,
        task_completed INTEGER,
        any_block INTEGER,
        latency_ms REAL,
        layers TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_session(session_id: str, started_at: str, guard_mode: str, task: str, db_path: str = DB_PATH) -> None:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO sessions (id, started_at, guard_mode, task) VALUES (?, ?, ?, ?)",
        (session_id, started_at, guard_mode, task)
    )
    conn.commit()
    conn.close()

def insert_event(session_id: str, event_type: str, tool: str | None, args_json: str | None,
                 trust: str | None, sensitivity: str | None, content_preview: str | None,
                 db_path: str = DB_PATH) -> int:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    ts = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "INSERT INTO events (session_id, ts, type, tool, args_json, trust, sensitivity, content_preview) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (session_id, ts, event_type, tool, args_json, trust, sensitivity, content_preview)
    )
    event_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(event_id)

def insert_decision(event_id: int, verdict: str, rule_id: str, evidence_json: str | None,
                    explanation: str, latency_ms: float, db_path: str = DB_PATH) -> int:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO decisions (event_id, verdict, rule_id, evidence_json, explanation, latency_ms) VALUES (?, ?, ?, ?, ?, ?)",
        (event_id, verdict, rule_id, evidence_json, explanation, latency_ms)
    )
    dec_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(dec_id)

def insert_approval(decision_id: int, status: str = "pending", db_path: str = DB_PATH) -> int:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    created_at = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "INSERT INTO approvals (decision_id, status, created_at, resolved_at) VALUES (?, ?, ?, NULL)",
        (decision_id, status, created_at)
    )
    app_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(app_id)

def resolve_approval(approval_id: int, approve: bool, db_path: str = DB_PATH) -> bool:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    status = "approved" if approve else "denied"
    resolved_at = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "UPDATE approvals SET status = ?, resolved_at = ? WHERE id = ?",
        (status, resolved_at, approval_id)
    )
    updated = cur.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def get_joined_events(db_path: str = DB_PATH) -> list[dict]:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
    SELECT 
        e.id as id,
        e.session_id,
        e.ts,
        e.type,
        e.tool,
        e.args_json,
        e.trust,
        e.sensitivity,
        e.content_preview,
        d.id as decision_id,
        d.verdict,
        d.rule_id,
        d.evidence_json,
        d.explanation,
        d.latency_ms,
        a.id as approval_id,
        a.status as approval_status,
        a.created_at as approval_created_at,
        a.resolved_at as approval_resolved_at
    FROM events e
    LEFT JOIN decisions d ON d.event_id = e.id
    LEFT JOIN approvals a ON a.decision_id = d.id
    ORDER BY e.id DESC
    """)
    rows = cur.fetchall()
    results = []
    for r in rows:
        item = {
            "id": r["id"],
            "session_id": r["session_id"],
            "ts": r["ts"],
            "type": r["type"],
            "tool": r["tool"],
            "args": json.loads(r["args_json"]) if r["args_json"] else None,
            "trust": r["trust"],
            "sensitivity": r["sensitivity"],
            "content_preview": r["content_preview"],
            "decision": None,
            "approval": None
        }
        if r["decision_id"] is not None:
            item["decision"] = {
                "verdict": r["verdict"],
                "rule_id": r["rule_id"],
                "evidence": json.loads(r["evidence_json"]) if r["evidence_json"] else None,
                "explanation": r["explanation"],
                "latency_ms": r["latency_ms"]
            }
        if r["approval_id"] is not None:
            item["approval"] = {
                "id": r["approval_id"],
                "status": r["approval_status"],
                "created_at": r["approval_created_at"],
                "resolved_at": r["approval_resolved_at"]
            }
        results.append(item)
    conn.close()
    return results

def get_pending_approvals(db_path: str = DB_PATH) -> list[dict]:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
    SELECT 
        a.id as approval_id,
        a.decision_id,
        a.status,
        a.created_at,
        d.rule_id,
        d.explanation,
        e.id as event_id,
        e.session_id,
        e.tool,
        e.args_json
    FROM approvals a
    JOIN decisions d ON d.id = a.decision_id
    JOIN events e ON e.id = d.event_id
    WHERE a.status = 'pending'
    ORDER BY a.id DESC
    """)
    rows = cur.fetchall()
    results = []
    for r in rows:
        results.append({
            "id": r["approval_id"],
            "decision_id": r["decision_id"],
            "event_id": r["event_id"],
            "session_id": r["session_id"],
            "tool": r["tool"],
            "args": json.loads(r["args_json"]) if r["args_json"] else {},
            "rule_id": r["rule_id"],
            "explanation": r["explanation"],
            "status": r["status"],
            "created_at": r["created_at"]
        })
    conn.close()
    return results

def insert_run(batch_id: str, item_id: str, kind: str, guard_mode: str,
               attack_succeeded: int, task_completed: int, any_block: int,
               latency_ms: float, layers: str, db_path: str = DB_PATH) -> int:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO runs (batch_id, item_id, kind, guard_mode, attack_succeeded,
                             task_completed, any_block, latency_ms, layers)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (batch_id, item_id, kind, guard_mode, attack_succeeded, task_completed, any_block, latency_ms, layers)
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(run_id)

def get_runs(batch_id: str | None = None, db_path: str = DB_PATH) -> list[dict]:
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()
    if batch_id:
        cur.execute("SELECT * FROM runs WHERE batch_id = ? ORDER BY id ASC", (batch_id,))
    else:
        cur.execute("SELECT * FROM runs ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
