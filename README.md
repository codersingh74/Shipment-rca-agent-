
# Shipment RCA Agent

An LLM agent that investigates delayed or failed shipments and returns a structured root cause
with a recommended action. Claude decides which tools to call (tracking history, carrier
performance, pincode serviceability), reasons over the results, and answers in JSON.

**Live demo:** [link] · **Eval accuracy:** [XX%] on [N] test cases

> Data is synthetic. The workflow is modelled on real post-purchase logistics exceptions
> (failed delivery attempts, hub delays, address issues, unserviceable pincodes).

## Why this exists
Ops teams spend a lot of time reading tracking timelines to work out why an order is stuck.
This agent automates that first-pass root cause analysis and makes the result machine-readable,
so it can feed alerts, dashboards or customer messaging.

## How it works
```
POST /investigate {awb}
        │
   Redis cache ──hit──► cached result
        │ miss
   Claude (tool-use loop, max 6 steps)
        ├─ get_tracking_events(awb)
        ├─ get_carrier_performance(carrier)
        └─ check_pincode_serviceability(carrier, pincode)
        │
   JSON: root_cause · confidence · summary · recommended_action
```

Root causes: `customer_unavailable`, `address_issue`, `carrier_hub_delay`,
`customer_refused`, `pincode_unserviceable`, `on_track`, `unknown`.

## Features
- **Agentic tool use:** Claude chooses and sequences tool calls instead of following a fixed pipeline
- **Eval harness:** scores root-cause accuracy and tool-use accuracy; exits non-zero below a threshold, so it can gate CI
- **FastAPI service** with `/investigate`, `/health` and `/stats` (requests, cache hits, errors, avg latency)
- **Redis caching** with automatic in-memory fallback when `REDIS_URL` is unset
- **MCP server** exposing the same tools to Claude Desktop / Claude Code
- **Structured JSON logging** for each investigation (cause, tools used, latency)
- **Dockerised** for one-command deployment

## Quickstart
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key
uvicorn app.main:app --reload
```
```bash
curl -X POST localhost:8000/investigate \
  -H 'content-type: application/json' -d '{"awb": "AWB1003"}'
```
Example response:
```json
{
  "root_cause": "carrier_hub_delay",
  "confidence": 0.9,
  "summary": "Shipment stuck at Nagpur hub for 6 days due to congestion.",
  "recommended_action": "Escalate to the carrier or reallocate to a faster carrier.",
  "tools_called": ["get_tracking_events", "get_carrier_performance"],
  "cached": false
}
```
*(Replace with a real output from your own run.)*

## Evaluation
```bash
python -m evals.run_evals --threshold 0.8
```
| Metric | Result |
|---|---|
| Root-cause accuracy | [XX%] |
|
