"""
autonomous_cycle_utils.py — Pure utility functions extracted from autonomous_cycle.py

Extraction rationale: autonomous_cycle.py exceeded the registered LOC cap (2401).
These functions have no external side-effects and were extracted mechanically.
All function signatures and behaviour are preserved exactly.

Extracted: TC-SAL-DEBT-001 (governance LOC debt reduction sprint)
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import yaml

__all__ = [
    "classify_continuation_state",
    "run_stale_repair_pre_cycle",
    "_PRODUCT_SOURCE_TYPES",
    "_sync_hard_stops_after_repair",
    "_compute_exit_code",
    "bridge_to_legacy_format",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PRODUCT_SOURCE_TYPES = frozenset({
    "PRODUCT_SOURCE", "PRODUCT_TEST", "READINESS", "TEST",
})


# ---------------------------------------------------------------------------
# Extracted functions (verbatim — no logic changes)
# ---------------------------------------------------------------------------

def classify_continuation_state(
    auto_continue_value, at_max_iterations: bool, hard_stops: list,
    overclaimed: list, rework_items: list, review: dict,
    policies_path: Path, anti_skip_result: dict | None = None,
    dirty_state_classified: bool = True,
    required_artifacts_present: bool = True,
    product_output_floor_met: bool = True,
) -> str:
    """Classify the continuation state using a proper state machine.

    States (R112 — extended with YES_WITH_LIMITATIONS):
      YES                              — all accepted, anti-skip clean, pure new-work sprint
      YES_WITH_LIMITATIONS             — accepted but anti-skip has low-severity notes (R112)
      YES_WITH_REWORK                  — rework items but safe lanes continue
      NO_MAX_ITERATIONS                — iteration limit reached
      NO_EXTERNAL_GATE                 — blocked by gate approval / credentials / push
      NO_BROKEN_BASELINE               — critical rework blocks continuation
      NO_UNSAFE_SOURCE_STATE           — overclaimed items present
      NO_NO_PROGRESS                   — consecutive sprints with no product gap closure
      NO_POLICY_BLOCK                  — policy explicitly blocks continuation
      NO_GENERIC_NEXT_PROMPT           — generated prompt is generic, not stream-specific
      NO_LEGACY_REVIEW_CONTRADICTION   — legacy review disagrees with declaration cycle
      NO_STALE_GAPS                    — selected-product-gaps.json is stale
      NO_MISSING_EVIDENCE_MANIFEST     — evidence manifest missing or invalid
      NO_WRONG_STREAM_CONTEXT          — context pack/evidence-review references wrong stream
      NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS — ACCEPTED_VERIFIED but no raw logs packaged
      NO_PROMPT_QUALITY_FAILURE              — prompt quality validation failed (R108)
      NO_UNCLASSIFIED_DIRTY_STATE       — dirty git state without dirty_state_classification
      NO_MISSING_REQUIRED_ARTIFACTS     — declared required artifacts not found on disk
      NO_PRODUCT_OUTPUT_FLOOR           — Mainstream breadth < floor, no blocker removed
    """
    # Check for policy block
    if policies_path and policies_path.exists():
        try:
            policies = yaml.safe_load(policies_path.read_text(encoding="utf-8"))
            ac_policy = policies.get("autonomous_continuation", {})
            if ac_policy.get("force_stop", False):
                return "NO_POLICY_BLOCK"
        except Exception:
            pass

    # Priority-ordered classification
    if overclaimed:
        return "NO_UNSAFE_SOURCE_STATE"

    # Product-first traffic controller states (R113)
    if not dirty_state_classified:
        return "NO_UNCLASSIFIED_DIRTY_STATE"
    if not required_artifacts_present:
        return "NO_MISSING_REQUIRED_ARTIFACTS"
    if not product_output_floor_met:
        return "NO_PRODUCT_OUTPUT_FLOOR"

    if at_max_iterations:
        return "NO_MAX_ITERATIONS"

    # R102: Check for specific hard stop types
    for hs in hard_stops:
        if hs == "max_iterations_reached":
            continue
        if hs == "generic_next_prompt":
            return "NO_GENERIC_NEXT_PROMPT"
        if hs == "legacy_review_contradiction":
            return "NO_LEGACY_REVIEW_CONTRADICTION"
        if hs == "stale_gaps":
            return "NO_STALE_GAPS"
        if hs == "missing_evidence_manifest":
            return "NO_MISSING_EVIDENCE_MANIFEST"
        if hs == "wrong_stream_context":
            return "NO_WRONG_STREAM_CONTEXT"
        if hs == "missing_raw_logs_for_verified_claims":
            return "NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS"
        if hs == "prompt_quality_failure":
            return "NO_PROMPT_QUALITY_FAILURE"

    non_iter_hard_stops = [h for h in hard_stops if h != "max_iterations_reached"]
    if non_iter_hard_stops:
        return "NO_BROKEN_BASELINE"

    if auto_continue_value == "true_with_rework":
        return "YES_WITH_REWORK"

    if auto_continue_value:
        # R112: Check anti-skip for low-severity limitations
        if anti_skip_result and not anti_skip_result.get("all_pass", True):
            # Has violations but not blocked/downgraded — low-severity only
            impact = anti_skip_result.get("impact", {})
            if not impact.get("block") and not impact.get("downgrade"):
                return "YES_WITH_LIMITATIONS"
        return "YES"

    return "NO_EXTERNAL_GATE"


def run_stale_repair_pre_cycle(
    repo_root: Path,
    dry_run: bool = True,
    enabled: bool = False,
) -> dict:
    """Pre-cycle stale queue repair step (disabled by default).

    Calls stale_queue_repair_hook to detect and mark STALE_QUEUE_ITEM defects
    before the main autonomous cycle runs.

    Args:
        repo_root: Repository root path.
        dry_run: If True, report stale items without writing repairs. Default True.
        enabled: Master enable switch. Default False (disabled by default).

    Returns:
        dict with keys: enabled, skipped, stale_count, gap_count, status
    """
    if not enabled:
        return {"enabled": False, "skipped": True, "status": "DISABLED_BY_DEFAULT"}

    try:
        _supervisor_dir = Path(__file__).resolve().parent
        import sys as _sys
        if str(_supervisor_dir) not in _sys.path:
            _sys.path.insert(0, str(_supervisor_dir))
        from stale_queue_repair_hook import run_stale_repair  # type: ignore[import]

        result = run_stale_repair(repo_root=repo_root, dry_run=dry_run)
        return {
            "enabled": True,
            "skipped": False,
            "stale_count": result.get("stale_count", 0),
            "gap_count": result.get("gap_count", 0),
            "status": result.get("status", "UNKNOWN"),
            "dry_run": dry_run,
        }
    except ImportError as exc:
        return {
            "enabled": True,
            "skipped": False,
            "status": f"IMPORT_ERROR: {exc}",
            "stale_count": 0,
            "gap_count": 0,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "enabled": True,
            "skipped": False,
            "status": f"ERROR: {type(exc).__name__}: {exc}",
            "stale_count": 0,
            "gap_count": 0,
        }


def _sync_hard_stops_after_repair(
    hard_stops: list,
    rework_items: list,
    prior_structural_blocks: list,
) -> list:
    """Sync hard_stops after TC-REPAIR-VERIFY-001 resolves GOV_BLOCK items (TC-SIGNAL-001).

    Only clears 'critical_rework_blocks_continuation' when:
    1. prior_structural_blocks was non-empty (GOV_BLOCK items existed before repair)
    2. rework_items is now empty (ALL GOV_BLOCK items resolved)
    3. 'critical_rework_blocks_continuation' is in hard_stops

    Safety: if REJECTED/OVERCLAIMED items also caused exit_code==3, they remain in
    rework_items → condition 2 fails → hard_stop is preserved.
    """
    if (prior_structural_blocks
            and not rework_items
            and "critical_rework_blocks_continuation" in hard_stops):
        updated = [h for h in hard_stops if h != "critical_rework_blocks_continuation"]
        print("  [SIGNAL-SYNC] critical_rework_blocks_continuation cleared: "
              "all GOV_BLOCK items resolved by TC-REPAIR-VERIFY-001")
        return updated
    return hard_stops


def _compute_exit_code(review: dict, decl: dict, gov_result: dict | None) -> int:
    """Compute exit code for the cycle manifest.

    TC-H4-001: If governance blocks_sprint=True AND declaration has PRODUCT_SOURCE
    items → exit 3 (not 0). GOVERNANCE_DOC/GOVERNANCE_TOOL items are exempt.

    Exit codes:
      0 = all accepted, governance clean
      3 = critical rework OR governance blocks PRODUCT_SOURCE items
    """
    if review["critical_rework_count"] > 0:
        return 3
    if gov_result is not None and gov_result.get("blocks_sprint"):
        items = decl.get("planned_work_items", [])
        has_product_items = any(
            item.get("item_type", "") in _PRODUCT_SOURCE_TYPES for item in items
        )
        if has_product_items:
            print("  [EXIT_CODE] governance blocks_sprint=True with PRODUCT_SOURCE items -> exit 3")
            return 3
        else:
            print("  [EXIT_CODE] governance blocks_sprint=True, all items are governance/doc -> exit 0 with WARNING")
    return 0


def bridge_to_legacy_format(review: dict, manifest: dict, decl: dict, repo_root: Path) -> None:
    """Convert declaration-driven cycle outputs to the JSON format expected by
    generate_supervisor_packet.py so that session-resume.md, approval-gates.md,
    and next-sprint.md are regenerated from fresh data.

    Writes:
      reports/supervisor/evidence-review.json
      reports/supervisor/contradictions.json
    """
    output_dir = repo_root / "reports" / "supervisor"
    output_dir.mkdir(parents=True, exist_ok=True)

    test_results = decl.get("test_results", {})
    passed = test_results.get("passed", 0)
    failed = test_results.get("failed", 0)

    # Build evidence-review.json in the format generate_supervisor_packet expects
    # R102: Mark as declaration-sourced so legacy checks (final-verdict.md,
    # sidecar, R90 contract) are skipped by compare_goal_to_evidence.py
    evidence_review = {
        "_declaration_sourced": True,
        "_source_cycle": "autonomous_cycle.py::bridge_to_legacy_format",
        "sprint_id": manifest.get("sprint_id", "unknown"),
        "timestamp": manifest.get("timestamp", datetime.now().isoformat()),
        "verdict": review.get("overall_verdict", "unknown"),
        "bundle_path": str(decl.get("evidence_root", "")),
        "facts": {
            "test_count": passed,
            "fail_count": failed,
            "skip_count": test_results.get("skipped", 0),
            "git_head": decl.get("git_head_end", "unknown"),
            "gate_states": {},
            "final_verdict_text": review.get("overall_verdict", ""),
            "pending_marker_count": 0,
            "bundle_entry_count": len(review.get("item_grades", [])),
            "bundle_validation_pass": manifest.get("exit_code", 9) != 9,
        },
        "contradictions": [],
        "limitation_notes": [],
        "validator_invoked": True,
        "bundle_validation_pass": manifest.get("exit_code", 9) != 9,
        "exit_code": manifest.get("exit_code", 0),
        "status": "complete",
        "evidence_quality_score": review.get("evidence_quality_score", 0.0),
        "verified_item_count": review.get("verified_item_count", 0),
        "evidence_quality_breakdown": review.get("evidence_quality_breakdown", {}),
    }

    # Build contradictions.json
    contradictions_list = []
    if review.get("critical_rework_count", 0) > 0:
        for grade in review.get("item_grades", []):
            if grade.get("supervisor_grade") in ("OVERCLAIMED", "REJECTED"):
                contradictions_list.append({
                    "severity": "CRITICAL",
                    "description": f"{grade['supervisor_grade']}: {grade.get('item_title', grade.get('item_id', 'unknown'))}",
                    "detail": grade.get("required_rework", ""),
                })
    if failed > 0:
        contradictions_list.append({
            "severity": "CRITICAL",
            "description": f"Tests failed: {failed} failures detected",
            "detail": "All tests must pass per Format Factory policy",
        })

    critical_count = sum(1 for c in contradictions_list if c["severity"] == "CRITICAL")
    contradictions = {
        "sprint_id": manifest.get("sprint_id", "unknown"),
        "timestamp": manifest.get("timestamp", datetime.now().isoformat()),
        "overall": "CRITICAL_CONTRADICTIONS" if critical_count > 0 else "CLEAN",
        "critical_count": critical_count,
        "warning_count": 0,
        "autonomous_continue": manifest.get("autonomous_continue", False),
        "contradictions": contradictions_list,
    }

    (output_dir / "evidence-review.json").write_text(
        json.dumps(evidence_review, indent=2), encoding="utf-8"
    )
    (output_dir / "contradictions.json").write_text(
        json.dumps(contradictions, indent=2), encoding="utf-8"
    )

    # R109: Also write stream-local evidence-review and contradictions
    try:
        from validate_package_identity import _extract_stream_from_sprint
        stream = _extract_stream_from_sprint(manifest.get("sprint_id", ""))
        stream_dir = repo_root / "reports" / "supervisor-streams" / stream
        stream_dir.mkdir(parents=True, exist_ok=True)
        (stream_dir / "evidence-review.json").write_text(
            json.dumps(evidence_review, indent=2), encoding="utf-8"
        )
        (stream_dir / "contradictions.json").write_text(
            json.dumps(contradictions, indent=2), encoding="utf-8"
        )
    except Exception:
        pass
