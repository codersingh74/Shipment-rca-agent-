import json, logging, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app import agent, cache

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("rca")
app = FastAPI(title="Shipment RCA Agent")
STATS = {"requests": 0, "cache_hits": 0, "errors": 0, "total_latency_ms": 0}


class InvestigateReq(BaseModel):
    awb: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    n = max(STATS["requests"], 1)
    return {**STATS, "avg_latency_ms": STATS["total_latency_ms"] // n}


@app.post("/investigate")
def investigate(req: InvestigateReq):
    STATS["requests"] += 1
    t0, key = time.time(), f"rca:{req.awb}"
    cached = cache.get(key)
    if cached:
        STATS["cache_hits"] += 1
        return {**cached, "cached": True}
    try:
        result = agent.investigate(req.awb)
    except Exception as e:
        STATS["errors"] += 1
        log.error(json.dumps({"event": "investigate_failed", "awb": req.awb, "error": str(e)}))
        raise HTTPException(502, "Agent failed, try again")
    cache.set(key, result)
    ms = int((time.time() - t0) * 1000)
    STATS["total_latency_ms"] += ms
    log.info(json.dumps({"event": "investigate", "awb": req.awb, "cause": result["root_cause"],
                         "tools": result["tools_called"], "ms": ms}))
    return {**result, "cached": False}
