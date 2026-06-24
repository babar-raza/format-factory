"""
TC-AMD-ADAPT-001: Adapter from format-factory maturity signal → reviewer app agent-run-state.

Output: .local/evidences/reviewer-adapter-pilot/agent-run-state.json
(NOT recruitize-ai-review-agent repo — that would be a brittle cross-repo absolute path)

Schema: agent-run-state/v1 (additionalProperties: true — ff_* extensions permitted)
NOTE: agent-run-directive.json is NOT adaptable (blog-specific schema: blog/queryId/profileId).

Status mapping (maturity-signal sprint_verdict → agent-run-state status):
  ACCEPTED_VERIFIED       → completed
  ACCEPTED_WITH_WARNINGS  → completed  (with ff_has_warnings=True extension)
  REWORK_REQUIRED         → paused
  REJECTED                → failed
  BLOCKED_BY_GATE         → hitl       (explicit human gate required)
  (other/unknown)         → running
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

_STATUS_MAP = {
    "ACCEPTED_VERIFIED": "completed",
    "ACCEPTED_WITH_WARNINGS": "completed",
    "REWORK_REQUIRED": "paused",
    "REJECTED": "failed",
    "BLOCKED_BY_GATE": "hitl",
}


def adapt_signal_to_run_state(signal: dict, run_id: "str | None" = None) -> dict:
    """Convert format-factory maturity signal to agent-run-state schema.

    Returns a dict conforming to agent-run-state/v1 with ff_* extension fields
    (allowed because the schema has additionalProperties: true).
    """
    verdict = signal.get("sprint_verdict", "")
    status = _STATUS_MAP.get(verdict, "running")
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schema": "agent-run-state/v1",
        "runId": run_id or signal.get("run_id", "unknown"),
        "status": status,
        "createdAt": signal.get("timestamp", now),
        "updatedAt": now,
        "control": {
            "stopAfter": None,
            "pauseAfter": None,
        },
        # Format-factory extensions (additionalProperties: true allows these)
        "ff_sprint_verdict": verdict,
        "ff_maturity_score": signal.get("agentic_maturity_score", 0),
        "ff_autonomous_continue": signal.get("autonomous_continue", False),
        "ff_work_items": signal.get("work_items", []),
        "ff_rework_items": signal.get("rework_items", []),
        "ff_integration_mode": signal.get("integration_mode", "adapter_required"),
        "ff_has_warnings": verdict == "ACCEPTED_WITH_WARNINGS",
    }


def write_adapted_state(
    signal: dict, output_path: "Path", run_id: "str | None" = None
) -> bool:
    """Write adapted agent-run-state to output_path atomically. Returns True on success."""
    try:
        state = adapt_signal_to_run_state(signal, run_id)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = output_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        os.replace(str(tmp), str(output_path))
        return True
    except Exception as exc:
        print(f"[reviewer_adapter] ERROR: {exc}")
        return False
