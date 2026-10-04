"""Plumbing tests with a fake LLM client (no API key needed)."""
import json
from types import SimpleNamespace as NS
from fastapi.testclient import TestClient
from app import agent, tools
from app.main import app


class FakeClient:
    def __init__(self):
        self.messages = self
        self.calls = 0

    def create(self, **kw):
        self.calls += 1
        if self.calls == 1:
            blk = NS(type="tool_use", id="t1", name="get_tracking_events", input={"awb": "AWB1002"})
            return NS(stop_reason="tool_use", content=[blk])
        out = {"root_cause": "customer_unavailable", "confidence": 0.9,
               "summary": "Two failed attempts.", "recommended_action": "Call customer."}
        return NS(stop_reason="end_turn", content=[NS(type="text", text=json.dumps(out))])


def test_tools():
    assert tools.get_tracking_events("AWB1002")["carrier"] == "Delhivery"
    assert tools.check_pincode_serviceability("XpressBees", "193502")["serviceable"] is False
    assert "error" in tools.run_tool("nope", {})


def test_agent_loop():
    r = agent.investigate("AWB1002", client=FakeClient())
    assert r["root_cause"] == "customer_unavailable"
    assert r["tools_called"] == ["get_tracking_events"]


def test_api_and_cache(monkeypatch):
    monkeypatch.setattr(agent, "_client", lambda: FakeClient())
    c = TestClient(app)
    assert c.get("/health").json() == {"status": "ok"}
    first = c.post("/investigate", json={"awb": "AWB1002"}).json()
    second = c.post("/investigate", json={"awb": "AWB1002"}).json()
    assert first["cached"] is False and second["cached"] is True
    assert c.get("/stats").json()["cache_hits"] == 1
