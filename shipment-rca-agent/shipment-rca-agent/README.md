# Shipment RCA Agent

An LLM agent that investigates delayed or failed shipments and returns a structured root cause.
Claude calls tools (tracking history, carrier performance, pincode serviceability), reasons over the
results, and answers as JSON. Data is synthetic, but the structure mirrors a real logistics workflow.

**Stack:** Python, FastAPI, Anthropic API (tool use), Redis (cache), MCP, Docker

## Run
    pip install -r requirements.txt
    cp .env.example .env   # add ANTHROPIC_API_KEY, then: export $(cat .env | xargs)
    uvicorn app.main:app --reload
    curl -X POST localhost:8000/investigate -H 'content-type: application/json' -d '{"awb":"AWB1003"}'

## Evals
    python -m evals.run_evals            # root-cause accuracy + tool-use accuracy, exits 1 below threshold
    pytest                               # plumbing tests with a fake LLM client

## MCP server
    python -m app.mcp_server             # add to Claude Desktop / Claude Code as a stdio server

## Deploy
    docker build -t rca-agent . && docker run -p 8000:8000 --env-file .env rca-agent
On Render: new Web Service from this repo (Docker), set ANTHROPIC_API_KEY, optionally add Render Redis and set REDIS_URL.

## Endpoints
`POST /investigate`, `GET /health`, `GET /stats` (requests, cache hits, errors, avg latency).
