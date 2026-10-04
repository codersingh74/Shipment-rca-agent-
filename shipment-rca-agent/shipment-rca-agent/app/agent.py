import json, os, re, time
from app import tools

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
MAX_STEPS = 6
CAUSES = ["customer_unavailable", "address_issue", "carrier_hub_delay",
          "customer_refused", "pincode_unserviceable", "on_track", "unknown"]

SYSTEM = f"""You are a logistics exception analyst for an e-commerce post-purchase platform.
Given an AWB, find the root cause of any delay or delivery failure.
Rules:
- Always call get_tracking_events first. Use the other tools only when relevant.
- Base conclusions only on tool results. If evidence is insufficient, use root_cause "unknown".
- Finish with ONLY a JSON object, no other text:
{{"root_cause": one of {CAUSES}, "confidence": 0-1, "summary": "<=2 sentences", "recommended_action": "<1 sentence>"}}"""


def _client():
    import anthropic
    return anthropic.Anthropic()


def _parse(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    try:
        data = json.loads(m.group(0))
    except Exception:
        return {"root_cause": "unknown", "confidence": 0.0,
                "summary": text[:300], "recommended_action": "Manual review needed"}
    if data.get("root_cause") not in CAUSES:
        data["root_cause"] = "unknown"
    return data


def investigate(awb: str, client=None) -> dict:
    client = client or _client()
    msgs = [{"role": "user", "content": f"Investigate shipment {awb} and find the root cause."}]
    called, t0 = [], time.time()
    for _ in range(MAX_STEPS):
        resp = client.messages.create(model=MODEL, max_tokens=1024, system=SYSTEM,
                                      tools=tools.TOOL_SCHEMAS, messages=msgs)
        if resp.stop_reason != "tool_use":
            break
        msgs.append({"role": "assistant", "content": resp.content})
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                called.append(b.name)
                out = tools.run_tool(b.name, b.input)
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(out)})
        msgs.append({"role": "user", "content": results})
    else:
        raise RuntimeError("agent exceeded max steps")
    text = "".join(b.text for b in resp.content if b.type == "text")
    result = _parse(text)
    result.update(awb=awb, tools_called=called, latency_ms=int((time.time() - t0) * 1000))
    return result
