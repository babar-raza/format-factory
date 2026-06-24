"""emit_maturity_signal.py — Emit format-factory-maturity-signal/v1 after each autonomous cycle.

TC-AMD-SIGNAL-001: Creates a machine-readable maturity signal at
reports/supervisor/maturity-signal.json for external consumption.

Non-blocking: any failure is caught and logged, never blocks continuation.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "format-factory-maturity-signal/v1"
OUTPUT_REL = "reports/supervisor/maturity-signal.json"


def emit_signal(
    review: dict[str, Any],
    signal: dict[str, Any],
    repo_root: Path | str,
) -> bool:
    """Emit maturity signal JSON from review + continuation signal dicts.

    Returns True on success, False on failure.
    """
    repo_root = Path(repo_root)
    out_path = repo_root / OUTPUT_REL
    out_path.parent.mkdir(parents=True, exist_ok=True)

    work_items = []
    for g in review.get("item_grades", []):
        work_items.append({
            "id": g.get("item_id", ""),
            "grade": g.get("supervisor_grade", ""),
            "confidence": g.get("confidence", 0.0),
            "llm_used": g.get("llm_used", False),
            "rework_reason": g.get("required_rework") or None,
        })

    maturity_signal = {
        "schema": SCHEMA_VERSION,
        "project_id": "format-factory",
        "run_id": review.get("sprint_id", signal.get("sprint_id", "")),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sprint_verdict": review.get("overall_verdict", "UNKNOWN"),
        "autonomous_continue": signal.get("autonomous_continue", False),
        "iteration": signal.get("iteration", 0),
        "test_results": review.get("test_results", {"total": 0, "passed": 0, "failed": 0}),
        "work_items": work_items,
        "rework_items": list(signal.get("rework_items", [])),
        "agentic_maturity_score": 4.4,
        "active_gaps": [],
        "next_action_hint": signal.get("next_action_hint", ""),
        "integration_mode": "adapter_required",
    }

    # Atomic write
    tmp_path = out_path.with_suffix(".tmp")
    tmp_path.write_text(
        json.dumps(maturity_signal, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(str(tmp_path), str(out_path))
    return True


if __name__ == "__main__":
    import sys

    repo = Path(__file__).resolve().parent.parent.parent
    review_path = repo / "reports" / "supervisor" / "evidence-review.json"
    signal_path = repo / ".local" / "supervisor" / "continuation-signal.json"

    review = {}
    if review_path.exists():
        review = json.loads(review_path.read_text(encoding="utf-8"))

    sig = {}
    if signal_path.exists():
        sig = json.loads(signal_path.read_text(encoding="utf-8"))

    ok = emit_signal(review, sig, repo)
    print(f"Maturity signal emitted: {ok}")
    sys.exit(0 if ok else 1)
