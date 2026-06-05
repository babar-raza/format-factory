"""Generate target-writer readiness registry for the hardening sprint."""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from select_poc_gaps import (
    _ARCHITECTURE_BLOCKED_SEED,
    detect_target_writer_readiness,
    BLOCKED_GAP_IDS,
)

out_dir = REPO_ROOT / "reports" / "dotnet-target-writer-readiness-hardening"
out_dir.mkdir(parents=True, exist_ok=True)

registry = []
for gap_id in sorted(_ARCHITECTURE_BLOCKED_SEED):
    r = detect_target_writer_readiness(REPO_ROOT, gap_id)
    registry.append(r)

payload = {
    "generated_at": "2026-06-05T00:00:00Z",
    "sprint_id": "FORMAT-FACTORY-DOTNET-TARGET-WRITER-READINESS-HARDENING-AND-POC-RECONCILIATION-001",
    "detection_version": "v5",
    "total_gaps": len(registry),
    "ready_count": sum(1 for r in registry if r["status"] == "READY"),
    "blocked_count": len(BLOCKED_GAP_IDS),
    "writers": registry,
    "unblock_rule": (
        "READY only when: source_exists AND project_exists AND tests_exist "
        "AND raw_log_passed AND sample_output_exists. "
        "SOURCE_PRESENT_TESTS_REQUIRED is provisional (not accepted_for_poc). "
        "MISSING_SOURCE reverts gap to ARCHITECTURE_BLOCKED."
    ),
}

(out_dir / "target-writer-readiness-registry.json").write_text(
    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
)
print(f"Registry: {len(registry)} gaps, {payload['ready_count']} READY, {payload['blocked_count']} blocked")
