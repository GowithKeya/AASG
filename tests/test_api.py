from fastapi.testclient import TestClient
from guard.api import app
from shared.schemas import Session, ToolCall

client = TestClient(app)

def test_api_events_endpoint():
    res = client.get("/events")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_api_approvals_endpoint():
    res = client.get("/approvals")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_api_metrics_endpoint():
    res = client.get("/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "attack_prevention_rate" in data
    assert "benign_completion_rate" in data

def test_api_guard_input():
    session = Session(
        id="api_test_sess",
        started_at="2026-10-23T00:00:00Z",
        guard_mode="guard_on",
        task="Api test",
        tainted=False,
        highest_sensitivity="public",
        history=[]
    )
    res = client.post("/guard/input", json={"session": session.model_dump(), "text": "Hello world"})
    assert res.status_code == 200
    assert res.json()["trust"] == "trusted"

def test_api_guard_tool_call():
    session = Session(
        id="api_test_sess",
        started_at="2026-10-23T00:00:00Z",
        guard_mode="guard_on",
        task="Api test",
        tainted=False,
        highest_sensitivity="public",
        history=[]
    )
    call = ToolCall(tool="unauthorized_exec", args={"cmd": "ls"})
    res = client.post("/guard/tool_call", json={"session": session.model_dump(), "call": call.model_dump()})
    assert res.status_code == 200
    assert res.json()["action"] == "BLOCK"
