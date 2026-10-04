"""Run: python -m evals.run_evals [--threshold 0.8]
Scores root-cause accuracy and whether the agent used the right tools."""
import argparse, json, pathlib, sys
from app import agent


def run(threshold: float) -> int:
    cases = json.loads(pathlib.Path(__file__).with_name("cases.json").read_text())
    rows = []
    for c in cases:
        try:
            r = agent.investigate(c["awb"])
        except Exception as e:
            r = {"root_cause": "error", "tools_called": [], "latency_ms": 0, "summary": str(e)}
        cause_ok = r["root_cause"] == c["expected_cause"]
        tools_ok = set(c["expected_tools"]) <= set(r["tools_called"])
        rows.append({"awb": c["awb"], "expected": c["expected_cause"], "got": r["root_cause"],
                     "cause_ok": cause_ok, "tools_ok": tools_ok, "latency_ms": r["latency_ms"]})
        print(f'{"PASS" if cause_ok and tools_ok else "FAIL"}  {c["awb"]}  expected={c["expected_cause"]}  got={r["root_cause"]}  tools_ok={tools_ok}')
    n = len(rows)
    acc = sum(r["cause_ok"] for r in rows) / n
    tool_acc = sum(r["tools_ok"] for r in rows) / n
    avg_ms = sum(r["latency_ms"] for r in rows) // n
    print(f"\nroot-cause accuracy: {acc:.0%} | tool-use accuracy: {tool_acc:.0%} | avg latency: {avg_ms} ms")
    pathlib.Path(__file__).with_name("last_run.json").write_text(
        json.dumps({"accuracy": acc, "tool_accuracy": tool_acc, "avg_latency_ms": avg_ms, "rows": rows}, indent=2))
    return 0 if acc >= threshold else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--threshold", type=float, default=0.8)
    sys.exit(run(p.parse_args().threshold))
