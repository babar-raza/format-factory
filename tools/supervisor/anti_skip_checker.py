"""Detect anti-skip violations in sprint evidence and outputs.

Nineteen detectors:
1. Generic prompt detector: flags next prompts that lack stream-specific content
2. Stale gap detector: flags selected gaps with wrong sprint_id
3. Missing raw logs detector: flags evidence without raw test logs
4. Path-only acceptance detector: flags ACCEPTED_VERIFIED with no test content proof
5. Missing evidence-manifest detector: flags missing evidence-manifest.yaml
6. Missing report files detector: flags declared report paths that don't exist
7. Missing lane ledger detector: flags missing lane execution ledger
8. Cross-stream prompt contamination detector: flags prompts with wrong-stream content
9. Missing sample outputs detector: flags evidence without sample output files
10. Dirty git state detector: flags uncommitted changes without classification
11. Wrong-stream selected gaps detector: flags gaps with wrong stream identity
12. Evidence quality score detector: flags sprints where all items are path-only accepted
13. Declaration completeness detector: flags declarations missing required fields
14. Test count regression detector: flags test count drop vs prior sprint
15. Stale evidence manifest detector: flags evidence-manifest.yaml with wrong sprint_id
16. Missing changed files detector: flags declared changed_files not found on disk
17. Stream-local authority detector: flags missing stream-local authority files
18. Wrong-stream next sprint detector: flags global next-sprint.md from a different stream
19. ODF spec linkage detector: flags ODF PRODUCT_SOURCE items missing spec_qname_refs
    and spec_fact_refs (high severity — downgrades verdict, does not block)

Severity mapping (R107):
  critical — blocks continuation, requires rework
  high     — downgrades overall verdict
  medium   — added as caveat, does not block
  low      — informational note only
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

GENERIC_PROMPT_MARKERS = (
    "continue with next sprint",
    "proceed with remaining work",
    "complete outstanding items",
    "address remaining gaps",
    "finish what was started",
)

STREAM_SPECIFIC_MARKERS = (
    "mainstream",
    "acceleration",
    "skills",
    "supervisor",
    "commercial_dotnet",
    "foss_python",
)


def detect_generic_prompt(prompt_text: str) -> dict[str, Any]:
    """Detect if a next prompt is too generic (no stream-specific content)."""
    lower = prompt_text.lower()
    generic_hits = [m for m in GENERIC_PROMPT_MARKERS if m in lower]
    stream_hits = [m for m in STREAM_SPECIFIC_MARKERS if m in lower]
    is_generic = len(generic_hits) > 0 and len(stream_hits) < 2
    return {
        "check": "generic_prompt",
        "is_violation": is_generic,
        "generic_markers_found": generic_hits,
        "stream_markers_found": stream_hits,
        "recommendation": (
            "Prompt is too generic. Add stream-specific boundaries, quotas, and forecasts."
            if is_generic
            else "Prompt has adequate stream-specific content."
        ),
    }


def _extract_sprint_number(sprint_id: str) -> int | None:
    """Extract R-number from sprint ID string."""
    m = re.search(r"R(\d+)", sprint_id, re.IGNORECASE)
    return int(m.group(1)) if m else None


def classify_gap_freshness(actual_sprint: str, expected_sprint: str) -> str:
    """R108: Classify gap freshness based on sprint distance.

    Returns:
      "current" — same sprint
      "recent" — within 3 sprints (still usable as-is)
      "stale" — 4-9 sprints behind (should re-run gap selection)
      "archived" — 10+ sprints behind (treat as reference only)
    """
    actual_n = _extract_sprint_number(actual_sprint)
    expected_n = _extract_sprint_number(expected_sprint)
    if actual_n is None or expected_n is None:
        return "stale"  # can't determine, treat as stale
    distance = expected_n - actual_n
    if distance <= 0:
        return "current"
    if distance <= 3:
        return "recent"
    if distance <= 9:
        return "stale"
    return "archived"


def detect_stale_gaps(
    gaps_data: dict[str, Any],
    expected_sprint: str,
) -> dict[str, Any]:
    """Detect if selected gaps have a stale sprint_id."""
    actual_sprint = gaps_data.get("sprint_id", gaps_data.get("sprint", ""))
    is_stale = bool(expected_sprint and actual_sprint and actual_sprint != expected_sprint)
    freshness = classify_gap_freshness(actual_sprint, expected_sprint) if is_stale else "current"
    return {
        "check": "stale_gaps",
        "is_violation": is_stale,
        "expected_sprint": expected_sprint,
        "actual_sprint": actual_sprint,
        "freshness": freshness,
        "recommendation": (
            f"Selected gaps are {freshness} (expected {expected_sprint}, got {actual_sprint}). "
            f"{'Re-run gap selection.' if freshness in ('stale', 'archived') else 'Usable but consider refreshing.'}"
            if is_stale
            else "Selected gaps sprint matches expected."
        ),
    }


def detect_missing_raw_logs(
    evidence_root: Path,
    declaration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Detect if raw test logs are missing from evidence.

    Searches in order:
    1. evidence_root/ directly (*.log, raw-test-log.txt, etc.)
    2. evidence_root/raw-logs/ subdirectory
    3. reports/<run_id>/raw-logs/ (R100 fix: logs declared in reports/, not evidence_root/)
    4. sprint-evidence/reports/<run_id>/raw-logs/
    5. changed-files/reports/<run_id>/raw-logs/
    6. declaration.evidence_artifacts with type in (raw_log, raw-log, log, test_log)
    7. declaration.evidence_paths for any item that ends with .log
    """
    log_patterns = ["raw-test-log.txt", "raw-log*.txt", "*.log"]
    found_logs = []
    found_sources = []
    repo_root = None

    # Determine repo_root from evidence_root
    if evidence_root and evidence_root.exists():
        # evidence_root is .local/evidences/<run_id>/
        # repo_root is 3 levels up
        repo_root = evidence_root.parent.parent.parent
    elif declaration:
        er_str = declaration.get("evidence_root", "")
        if er_str:
            candidate = Path(er_str)
            if not candidate.is_absolute():
                # try to find repo root from current script location
                candidate = REPO_ROOT / er_str
            repo_root = candidate.parent.parent.parent

    if not repo_root:
        repo_root = REPO_ROOT

    if evidence_root and evidence_root.exists():
        for pattern in log_patterns:
            for f in evidence_root.glob(pattern):
                if str(f) not in [str(x) for x in found_logs]:
                    found_logs.append(f)
                    found_sources.append("evidence_root")
        # R107: Also check raw-logs/ subdirectory
        raw_logs_dir = evidence_root / "raw-logs"
        if raw_logs_dir.exists():
            for pattern in log_patterns:
                for f in raw_logs_dir.glob(pattern):
                    if str(f) not in [str(x) for x in found_logs]:
                        found_logs.append(f)
                        found_sources.append("evidence_root/raw-logs")

    # R100 fix: also check reports/<run_id>/raw-logs/ and related paths
    if declaration:
        run_id = declaration.get("run_id", "")
        if run_id:
            candidate_dirs = [
                repo_root / "reports" / run_id / "raw-logs",
                repo_root / "reports" / f"sprint-{run_id}" / "raw-logs",
            ]
            # Also check sprint-evidence and changed-files paths
            for review_dir in (repo_root / ".local" / "supervisor" / "reviews").glob("*"):
                candidate_dirs.append(review_dir / "sprint-evidence" / "reports" / run_id / "raw-logs")
                candidate_dirs.append(review_dir / "changed-files" / "reports" / run_id / "raw-logs")
            for cand in candidate_dirs:
                if cand.exists():
                    for pattern in log_patterns:
                        for f in cand.glob(pattern):
                            if str(f) not in [str(x) for x in found_logs]:
                                found_logs.append(f)
                                found_sources.append(f"reports/{run_id}/raw-logs")

        # Check declaration evidence_artifacts
        # R100 fix: accept types raw_log, raw-log, log, test_log
        raw_log_types = {"raw_log", "raw-log", "log", "test_log", "raw_test_log"}
        for artifact in declaration.get("evidence_artifacts", []):
            if artifact.get("type") in raw_log_types:
                p = Path(artifact["path"])
                if not p.is_absolute():
                    p = repo_root / p
                if p.exists() and str(p) not in [str(x) for x in found_logs]:
                    found_logs.append(p)
                    found_sources.append("declaration_artifact")

        # Also check all declared evidence_paths for *.log files
        for item in declaration.get("planned_work_items", []):
            for ep in item.get("evidence_paths", []):
                if ep.endswith(".log"):
                    p = Path(ep)
                    if not p.is_absolute():
                        p = repo_root / ep
                    if p.exists() and str(p) not in [str(x) for x in found_logs]:
                        found_logs.append(p)
                        found_sources.append("evidence_path")

        # Also check changed_files for .log files
        for cf in declaration.get("changed_files", []):
            if cf.endswith(".log"):
                p = Path(cf)
                if not p.is_absolute():
                    p = repo_root / cf
                if p.exists() and str(p) not in [str(x) for x in found_logs]:
                    found_logs.append(p)
                    found_sources.append("changed_file")

    is_missing = len(found_logs) == 0
    return {
        "check": "missing_raw_logs",
        "is_violation": is_missing,
        "logs_found": [str(p) for p in found_logs[:5]],
        "logs_found_count": len(found_logs),
        "sources": found_sources[:5],
        "recommendation": (
            "No raw test logs found. Capture pytest output to a file before closing."
            if is_missing
            else f"Found {len(found_logs)} raw log file(s)."
        ),
    }


def detect_path_only_acceptance(
    grades: dict[str, Any] | list,
) -> dict[str, Any]:
    """Detect ACCEPTED grades with no evidence of test content verification."""
    if isinstance(grades, dict):
        items = grades.get("work_item_grades", [])
    else:
        items = grades

    path_only = []
    for item in items:
        grade = item.get("supervisor_grade", item.get("grade", ""))
        if grade in ("ACCEPTED", "ACCEPTED_VERIFIED"):
            # Check if there's any test content evidence
            has_test_evidence = bool(item.get("test_file_content_checked"))
            has_acceptance_criteria = bool(item.get("acceptance_criteria_met"))
            if not has_test_evidence and not has_acceptance_criteria:
                path_only.append(item.get("item_id", "unknown"))

    return {
        "check": "path_only_acceptance",
        "is_violation": len(path_only) > 0,
        "path_only_items": path_only,
        "recommendation": (
            f"{len(path_only)} items accepted without test content verification: {path_only}"
            if path_only
            else "All accepted items have test content or acceptance criteria evidence."
        ),
    }


STREAM_BOUNDARY_FORBIDDEN = {
    "mainstream": ["tools/supervisor/", "tests/supervisor/"],
    "acceleration": ["src/net/", "src/python/"],
    "skills": ["src/net/", "src/python/"],
    "supervisor": ["src/net/", "src/python/"],
}

MAINSTREAM_PRODUCT_MARKERS = (
    "fods", "fodt", "netpbm", "pbm", "pgm", "ppm",
    "sylk", "zst", "gate 11", "commercial",
    "dotnet_status", "python_foss_status",
    "export_csv", "save_same_format",
)


def detect_missing_evidence_manifest(
    evidence_root: Path,
    declaration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Detect if evidence-manifest.yaml is missing from evidence."""
    manifest_paths = []
    if evidence_root.exists():
        manifest_paths.extend(evidence_root.glob("evidence-manifest.yaml"))

    # Also check declaration evidence_root
    if declaration:
        decl_root = declaration.get("evidence_root", "")
        if decl_root:
            decl_path = Path(decl_root) / "evidence-manifest.yaml"
            if decl_path.exists():
                manifest_paths.append(decl_path)

    is_missing = len(manifest_paths) == 0
    return {
        "check": "missing_evidence_manifest",
        "is_violation": is_missing,
        "manifests_found": [str(p) for p in manifest_paths],
        "recommendation": (
            "No evidence-manifest.yaml found. Create one listing all evidence artifacts."
            if is_missing
            else f"Found {len(manifest_paths)} evidence manifest(s)."
        ),
    }


def detect_missing_report_files(
    declaration: dict[str, Any],
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Detect declared report paths that don't exist on disk."""
    repo_root = repo_root or REPO_ROOT
    missing = []
    checked = []

    for report_path in declaration.get("reports_created", []):
        full = repo_root / report_path
        checked.append(str(report_path))
        if not full.exists():
            missing.append(str(report_path))

    for item in declaration.get("planned_work_items", []):
        for ep in item.get("evidence_paths", []):
            if ep not in checked:
                checked.append(ep)
                full = repo_root / ep
                if not full.exists():
                    missing.append(ep)

    return {
        "check": "missing_report_files",
        "is_violation": len(missing) > 0,
        "missing_reports": missing,
        "checked_count": len(checked),
        "recommendation": (
            f"{len(missing)} declared report(s) missing: {missing}"
            if missing
            else f"All {len(checked)} declared report paths exist."
        ),
    }


def detect_missing_lane_ledger(
    evidence_root: Path,
    sample_outputs_dir: Path | None = None,
    declaration: dict[str, Any] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Detect if lane execution ledger is missing from evidence.

    R109: Also searches declared report paths and the run_id-specific reports directory.
    """
    found = []
    search_dirs = [evidence_root]
    if sample_outputs_dir and sample_outputs_dir.exists():
        search_dirs.append(sample_outputs_dir)

    # R109: Also search the run_id-specific reports directory
    if declaration and repo_root:
        run_id = declaration.get("run_id", "")
        if run_id:
            reports_dir = repo_root / "reports" / run_id
            if reports_dir.exists():
                search_dirs.append(reports_dir)

    for d in search_dirs:
        if d.exists():
            found.extend(d.glob("*ledger*.json"))
            found.extend(d.glob("*ledger*.yaml"))
            found.extend(d.glob("*ledger*.jsonl"))  # GEC-TC-002: .jsonl support
            found.extend(d.glob("*lane*.json"))
            found.extend(d.glob("*lane*.yaml"))
            found.extend(d.glob("*lane*.jsonl"))  # GEC-TC-002: .jsonl support

    # R109: Also check declared reports_created for ledger files
    if declaration and repo_root and not found:
        for rp in declaration.get("reports_created", []):
            if "ledger" in rp.lower() or "lane" in rp.lower():
                rp_path = repo_root / rp
                if rp_path.exists():
                    found.append(rp_path)

    is_missing = len(found) == 0
    return {
        "check": "missing_lane_ledger",
        "is_violation": is_missing,
        "ledgers_found": [str(p) for p in found],
        "recommendation": (
            "No lane execution ledger found. Record lane executions in evidence_root or reports/<run_id>/."
            if is_missing
            else f"Found {len(found)} ledger file(s)."
        ),
    }


_GOVERNANCE_ITEM_TYPES = frozenset({
    "GOVERNANCE_DOC", "GOVERNANCE_SCHEMA", "GOVERNANCE_POLICY",
    "GOVERNANCE_TASKCARD", "LEGACY_BACKFILL_METADATA",
})
_GOVERNANCE_EXCEPTION_CLASSES = frozenset({
    "investigation_only", "legacy_backfill",
})
_DRY_RUN_CLASSIFICATIONS = frozenset({
    "dry_run_fixture", "governance_pilot", "test_fixture_only",
})


def _is_governance_only_sprint(declaration: dict[str, Any] | None) -> bool:
    """Return True if all work items are governance or backfill types (no PRODUCT_SOURCE)."""
    if not declaration:
        return False
    items = declaration.get("planned_work_items", [])
    if not items:
        return False
    return all(
        item.get("item_type", "") in _GOVERNANCE_ITEM_TYPES
        or item.get("exception_classification", "") in _GOVERNANCE_EXCEPTION_CLASSES
        for item in items
    )


def _has_product_source_items(declaration: dict[str, Any] | None) -> bool:
    """Return True if declaration has any PRODUCT_SOURCE items that need sample outputs."""
    if not declaration:
        return False
    for item in declaration.get("planned_work_items", []):
        item_type = item.get("item_type", "")
        exc_class = item.get("exception_classification", "")
        if item_type == "PRODUCT_SOURCE" and exc_class not in _DRY_RUN_CLASSIFICATIONS:
            return True
    return False


def detect_missing_sample_outputs(
    evidence_root: Path,
    sample_outputs_dir: Path | None = None,
    min_outputs: int = 1,
    declaration: dict[str, Any] | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Detect if sample output files are missing from evidence.

    R112: Also checks evidence-manifest artifacts with type: sample_output
    and declared evidence_artifacts with type: sample_output.

    GRE-TC-003: Governance-only sprints are exempt from sample output requirement.
    Sample outputs are only required for PRODUCT_SOURCE work items.
    """
    from collections import Counter

    # GRE-TC-003: Exempt governance-only sprints (only when declaration is provided)
    if declaration is not None and (
        _is_governance_only_sprint(declaration) or not _has_product_source_items(declaration)
    ):
        return {
            "check": "missing_sample_outputs",
            "is_violation": False,
            "outputs_found": 0,
            "min_required": 0,
            "sources": {},
            "exemption": "governance_or_no_product_source",
            "recommendation": (
                "Sample outputs not required: no PRODUCT_SOURCE items in declaration."
            ),
        }

    found_files: list[str] = []
    found_sources: list[str] = []
    search_dirs = []
    if sample_outputs_dir and sample_outputs_dir.exists():
        search_dirs.append(sample_outputs_dir)
    else:
        default = evidence_root / "sample-outputs"
        if default.exists():
            search_dirs.append(default)

    for d in search_dirs:
        for f in d.iterdir():
            if f.is_file():
                found_files.append(str(f))
                found_sources.append("directory")

    # R112: Check declaration evidence_artifacts for type: sample_output
    repo_root = evidence_root.parent.parent if evidence_root else None
    if declaration:
        for artifact in declaration.get("evidence_artifacts", []):
            if artifact.get("type") == "sample_output":
                p = Path(artifact["path"])
                if not p.is_absolute() and repo_root:
                    p = repo_root / p
                if p.exists() and str(p) not in found_files:
                    found_files.append(str(p))
                    found_sources.append("declaration")

    # R112: Check evidence-manifest.yaml for type: sample_output
    if manifest_path is None and evidence_root:
        manifest_path = evidence_root / "evidence-manifest.yaml"
    if manifest_path and manifest_path.exists():
        try:
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            for artifact in manifest.get("artifacts", []):
                if artifact.get("type") == "sample_output":
                    p = Path(artifact["path"])
                    if not p.is_absolute() and repo_root:
                        p = repo_root / p
                    if p.exists() and str(p) not in found_files:
                        found_files.append(str(p))
                        found_sources.append("manifest")
        except Exception:
            pass

    total = len(found_files)
    is_missing = total < min_outputs
    src_counts = Counter(found_sources)
    source_summary = ", ".join(f"{v} from {k}" for k, v in src_counts.items())

    return {
        "check": "missing_sample_outputs",
        "is_violation": is_missing,
        "outputs_found": total,
        "min_required": min_outputs,
        "sources": dict(src_counts),
        "recommendation": (
            f"Only {total} sample output(s) found (need {min_outputs}+). Generate sample outputs before closing."
            if is_missing
            else f"Found {total} sample output file(s) ({source_summary})."
        ),
    }


_BOUNDARY_SECTION_PREFIXES = (
    "## File Boundaries",
    "## Mandatory Evidence Rules",
    "## Governed Product Acceleration Rules",
    "## Group G8: Evidence + Supervisor Loop",
    "## Final Validation Sequence",
    "## Sprint Closeout",
    "## Closeout",
)


def _strip_boundary_section(text: str) -> str:
    """Remove sections that legitimately reference cross-stream paths.

    Stripped sections:
    - 'File Boundaries': documents forbidden paths informatively
    - 'Mandatory Evidence Rules': universal sprint close-out protocol (all streams)
    - 'Group G8: Evidence + Supervisor Loop': universal close-out group
    - 'Final Validation Sequence': py_compile + autonomous-cycle close-out
    - 'Sprint Closeout' / 'Closeout': any generic closeout section
    """
    lines = text.split("\n")
    filtered = []
    in_excluded = False
    for line in lines:
        stripped = line.strip()
        if any(stripped.startswith(pfx) for pfx in _BOUNDARY_SECTION_PREFIXES):
            in_excluded = True
            continue
        if in_excluded and stripped.startswith("## "):
            in_excluded = False
        if not in_excluded:
            filtered.append(line)
    return "\n".join(filtered)


SUPERVISOR_ITEM_TYPES = frozenset({
    "GOVERNANCE_DOC", "GOVERNANCE_HARDENING", "SUPERVISOR_TOOL",
    "SUPERVISOR_REPAIR", "SUPERVISOR_INTEGRATION", "SUPERVISOR_TEST",
    "SYSTEM_HEALING", "CLOSEOUT_GATE", "WATCHDOG",
    # Canonical short-form item types used in evidence declarations
    "governance", "supervisor", "system_healing", "test",
})


def detect_cross_stream_prompt_contamination(
    prompt_text: str,
    target_stream: str,
    declared_scope: list[str] | None = None,
) -> dict[str, Any]:
    """Detect if a stream-specific prompt contains content from other streams.

    Ignores the 'File Boundaries' section which legitimately references forbidden paths.

    When ``declared_scope`` contains supervisor/governance item types,
    supervisor paths (``tools/supervisor/``, ``tests/supervisor/``) are
    exempt from the mainstream forbidden list because the sprint explicitly
    includes governance work.
    """
    content_text = _strip_boundary_section(prompt_text)
    lower = content_text.lower()
    forbidden = list(STREAM_BOUNDARY_FORBIDDEN.get(target_stream, []))

    # Stream-aware exemption: if declared scope includes supervisor item types,
    # supervisor paths are legitimate in mainstream prompts.
    scope_types = set(declared_scope or [])
    has_supervisor_scope = bool(scope_types & SUPERVISOR_ITEM_TYPES)
    exempt_paths: list[str] = []
    if has_supervisor_scope and target_stream == "mainstream":
        exempt_paths = [p for p in forbidden if "supervisor" in p]
        forbidden = [p for p in forbidden if p not in exempt_paths]

    # Check for forbidden path references outside boundary docs
    forbidden_refs = [f for f in forbidden if f.lower() in lower]

    # For acceleration stream, check for mainstream product markers
    product_contamination = []
    if target_stream == "acceleration":
        product_contamination = [m for m in MAINSTREAM_PRODUCT_MARKERS if m in lower]

    is_contaminated = len(forbidden_refs) > 0 or (
        target_stream == "acceleration" and len(product_contamination) > 3
    )

    result: dict[str, Any] = {
        "check": "cross_stream_prompt_contamination",
        "is_violation": is_contaminated,
        "target_stream": target_stream,
        "forbidden_refs_found": forbidden_refs,
        "product_markers_found": product_contamination if target_stream == "acceleration" else [],
        "recommendation": (
            f"Prompt for {target_stream} contains cross-stream content: forbidden={forbidden_refs}, product_markers={product_contamination}"
            if is_contaminated
            else f"Prompt for {target_stream} has clean stream boundaries."
        ),
    }
    if exempt_paths:
        result["exempt_paths"] = exempt_paths
        result["exemption_reason"] = "declared_scope includes supervisor item types"
    return result


def _detect_dirty_from_status(git_status: str) -> bool:
    """Detect dirty git state from git_status_final string.

    Handles both prose format ("uncommitted changes") and git-status-short
    format ("M file.py, ?? newfile.py, A staged.py").
    """
    if not git_status:
        return False
    lower = git_status.lower()
    if "uncommitted" in lower:
        return True
    # Git-status-short prefixes: M, ??, A, D, R, AM, MM
    short_pattern = re.compile(
        r'(?:^|,\s*)'
        r'(?:M|A|D|R|AM|MM|\?\?)\s+'
    )
    if short_pattern.search(git_status):
        return True
    return False


def detect_dirty_git_state(
    declaration: dict[str, Any],
) -> dict[str, Any]:
    """Detect if git_status_final indicates uncommitted changes without classification."""
    git_status = declaration.get("git_status_final", "")
    is_dirty = _detect_dirty_from_status(git_status)
    has_classification = bool(
        declaration.get("dirty_state_classification")
        or "classified" in git_status.lower()
        or "DIRTY_" in git_status.upper()
    )
    is_violation = is_dirty and not has_classification
    return {
        "check": "dirty_git_state",
        "is_violation": is_violation,
        "git_status_final": git_status,
        "is_dirty": is_dirty,
        "has_classification": has_classification,
        "recommendation": (
            "Git state is dirty without classification. Add dirty_state_classification to declaration."
            if is_violation
            else ("Git state is clean." if not is_dirty else "Dirty state classified.")
        ),
    }


def detect_wrong_stream_gaps(
    gaps_data: dict[str, Any],
    expected_stream: str,
) -> dict[str, Any]:
    """Detect if selected gaps are from the wrong stream."""
    actual_stream = gaps_data.get("stream", "")
    if not actual_stream:
        # Try to detect from gap items
        gap_streams = {g.get("stream", "") for g in gaps_data.get("gaps", [])}
        gap_streams.discard("")
        actual_stream = gap_streams.pop() if len(gap_streams) == 1 else "mixed"

    is_wrong = bool(
        expected_stream and actual_stream
        and actual_stream not in (expected_stream, "", "mixed")
    )
    return {
        "check": "wrong_stream_gaps",
        "is_violation": is_wrong,
        "expected_stream": expected_stream,
        "actual_stream": actual_stream,
        "recommendation": (
            f"Selected gaps are from stream '{actual_stream}' but expected '{expected_stream}'. Regenerate stream-specific gaps."
            if is_wrong
            else f"Selected gaps stream matches expected: {expected_stream}."
        ),
    }


def _item_has_backed_evidence(item: dict[str, Any]) -> bool:
    """Check if an item has any real (non-path-only) backing evidence.

    An item is considered backed (not path-only) if it has any of:
    - grade == ACCEPTED_VERIFIED
    - test_file_content_checked=True
    - acceptance_criteria_met=True
    - raw_log_verified=True
    - declared evidence_paths with .log files that exist
    - proof_audit_backed=True
    - package_materialized=True
    - test_count > 0 declared on the item
    """
    grade = item.get("supervisor_grade", item.get("grade", ""))
    if grade == "ACCEPTED_VERIFIED":
        return True
    if item.get("test_file_content_checked"):
        return True
    if item.get("acceptance_criteria_met"):
        return True
    if item.get("raw_log_verified"):
        return True
    if item.get("proof_audit_backed"):
        return True
    if item.get("package_materialized"):
        return True
    test_count = item.get("test_count", item.get("tests_run", 0))
    if test_count and int(test_count) > 0:
        return True
    # Check evidence_paths for log files
    for ep in item.get("evidence_paths", []):
        if ep.endswith(".log") and Path(ep).exists():
            return True
        if ep.endswith(".log"):
            # path declared but may not exist locally — still credit it
            if "raw-logs" in ep or "test" in ep.lower():
                return True
    return False


def detect_evidence_quality_score(
    grades: dict[str, Any] | list,
) -> dict[str, Any]:
    """Detect if all accepted items are path-only (no concrete proof anywhere).

    R100 fix: An item is considered 'backed' (not path-only) if it has:
    - grade ACCEPTED_VERIFIED, OR
    - test_file_content_checked=True, acceptance_criteria_met=True, OR
    - raw_log_verified=True, proof_audit_backed=True, package_materialized=True, OR
    - test_count > 0 declared, OR
    - evidence_paths containing .log files (declared path to log = partial backing)

    score = backed_count / accepted_count
    is_violation = True only when score == 0.0 (truly no backing evidence at all)
    """
    if isinstance(grades, dict):
        items = grades.get("work_item_grades", grades.get("item_grades", []))
    else:
        items = grades

    accepted_grades = ("ACCEPTED", "ACCEPTED_VERIFIED", "ACCEPTED_WITH_LIMITATIONS", "ACCEPTED_WITH_WARNINGS")
    accepted = [i for i in items if i.get("supervisor_grade", i.get("grade", "")) in accepted_grades]
    if not accepted:
        return {
            "check": "evidence_quality_score",
            "is_violation": False,
            "score": 0.0,
            "recommendation": "No accepted items to score.",
        }

    verified = [i for i in accepted if i.get("supervisor_grade", i.get("grade", "")) == "ACCEPTED_VERIFIED"]
    backed = [i for i in accepted if _item_has_backed_evidence(i)]
    score = len(backed) / len(accepted) if accepted else 0.0
    is_all_path_only = len(backed) == 0 and len(accepted) > 0

    return {
        "check": "evidence_quality_score",
        "is_violation": is_all_path_only,
        "score": round(score, 2),
        "verified_count": len(verified),
        "backed_count": len(backed),
        "accepted_count": len(accepted),
        "recommendation": (
            f"All {len(accepted)} accepted items are truly path-only (no logs, no test counts, no proof audit). "
            f"At least one must have real backing evidence."
            if is_all_path_only
            else f"Evidence quality score: {score:.0%} ({len(backed)}/{len(accepted)} backed, {len(verified)} fully verified)."
        ),
    }


REQUIRED_DECLARATION_FIELDS = [
    "run_id", "sprint_id", "evidence_root", "planned_work_items",
    "test_results", "worker_self_verdict",
]


def detect_declaration_completeness(
    declaration: dict[str, Any],
) -> dict[str, Any]:
    """Detect if declaration is missing required fields."""
    missing = [f for f in REQUIRED_DECLARATION_FIELDS if f not in declaration]
    return {
        "check": "declaration_completeness",
        "is_violation": len(missing) > 0,
        "missing_fields": missing,
        "recommendation": (
            f"Declaration missing required fields: {missing}"
            if missing
            else f"Declaration has all {len(REQUIRED_DECLARATION_FIELDS)} required fields."
        ),
    }


def detect_test_count_regression(
    declaration: dict[str, Any],
    prior_test_count: int = 0,
) -> dict[str, Any]:
    """Detect if test count dropped from prior sprint."""
    test_results = declaration.get("test_results", {})
    current_count = test_results.get("passed", 0) + test_results.get("failed", 0)
    is_regression = prior_test_count > 0 and current_count < prior_test_count

    return {
        "check": "test_count_regression",
        "is_violation": is_regression,
        "current_count": current_count,
        "prior_count": prior_test_count,
        "recommendation": (
            f"Test count regressed: {current_count} < {prior_test_count} (prior sprint)."
            if is_regression
            else f"Test count: {current_count} (prior: {prior_test_count})."
        ),
    }


def detect_stale_evidence_manifest(
    evidence_root: Path,
    expected_sprint: str,
) -> dict[str, Any]:
    """Detect if evidence-manifest.yaml references a different sprint_id (#15)."""
    manifest_path = evidence_root / "evidence-manifest.yaml" if evidence_root else None
    if not manifest_path or not manifest_path.exists():
        return {
            "check": "stale_evidence_manifest",
            "is_violation": False,
            "recommendation": "No evidence-manifest.yaml to check.",
        }

    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        manifest_sprint = manifest.get("sprint_id", "")
        is_stale = bool(expected_sprint and manifest_sprint and manifest_sprint != expected_sprint)
        return {
            "check": "stale_evidence_manifest",
            "is_violation": is_stale,
            "expected_sprint": expected_sprint,
            "manifest_sprint": manifest_sprint,
            "recommendation": (
                f"Evidence manifest references sprint '{manifest_sprint}' but expected '{expected_sprint}'."
                if is_stale
                else "Evidence manifest sprint matches expected."
            ),
        }
    except Exception as e:
        return {
            "check": "stale_evidence_manifest",
            "is_violation": True,
            "recommendation": f"Failed to parse evidence-manifest.yaml: {e}",
        }


def detect_missing_changed_files(
    declaration: dict[str, Any],
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Detect if declared changed_files are missing from disk (#16)."""
    repo_root = repo_root or REPO_ROOT
    changed_files = declaration.get("changed_files", [])
    if not changed_files:
        return {
            "check": "missing_changed_files",
            "is_violation": False,
            "recommendation": "No changed_files declared.",
        }

    missing = []
    for cf in changed_files:
        full = repo_root / cf
        if not full.exists():
            missing.append(cf)

    return {
        "check": "missing_changed_files",
        "is_violation": len(missing) > 0,
        "missing_files": missing,
        "total_declared": len(changed_files),
        "recommendation": (
            f"{len(missing)}/{len(changed_files)} declared changed_files missing: {missing[:5]}"
            if missing
            else f"All {len(changed_files)} declared changed_files exist."
        ),
    }


def detect_stream_local_authority(
    target_stream: str,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """R109: Detect if stream-local authority files exist for the target stream.

    Checks reports/supervisor-streams/{stream}/ for expected files.
    """
    repo_root = repo_root or REPO_ROOT
    if not target_stream:
        return {
            "check": "stream_local_authority",
            "is_violation": False,
            "recommendation": "No target stream specified.",
        }

    streams_root = repo_root / "reports" / "supervisor-streams"
    if not streams_root.exists():
        # Pre-R109 repo — stream-local authority not yet established
        return {
            "check": "stream_local_authority",
            "is_violation": False,
            "recommendation": "Stream-local authority not yet established (pre-R109).",
        }

    stream_dir = streams_root / target_stream
    expected_files = [
        "latest-review.md",
        "latest-next-worker-prompt.md",
        "work-item-grades.json",
    ]
    found = []
    missing = []
    for f in expected_files:
        if (stream_dir / f).exists():
            found.append(f)
        else:
            missing.append(f)

    # Also check stream-local continuation signal
    signal_path = repo_root / ".local" / "supervisor" / "streams" / target_stream / "continuation-signal.json"
    if signal_path.exists():
        found.append("continuation-signal.json")
    else:
        missing.append("continuation-signal.json")

    is_violation = len(missing) > len(found)  # More missing than found

    return {
        "check": "stream_local_authority",
        "is_violation": is_violation,
        "target_stream": target_stream,
        "stream_dir": str(stream_dir),
        "found": found,
        "missing": missing,
        "recommendation": (
            f"Stream-local authority for '{target_stream}': {len(missing)} files missing ({missing})"
            if is_violation
            else f"Stream-local authority for '{target_stream}': {len(found)}/{len(found) + len(missing)} files present."
        ),
    }


# R111: Stream-output authority classification
STREAM_OUTPUT_AUTHORITY = {
    "CURRENT_STREAM_AUTHORITY": "Generated by and for the current stream",
    "CURRENT_STREAM_ADVISORY": "Advisory artifact generated for the current stream",
    "CROSS_STREAM_REFERENCE": "Reference from another stream (not authoritative)",
    "ARCHIVED_LAST_WRITER_SNAPSHOT": "Last-writer snapshot (may be from any stream)",
    "INVALID_WRONG_STREAM": "Wrong-stream artifact incorrectly treated as authority",
}


def classify_stream_output_authority(
    artifact_path: str,
    artifact_stream: str,
    target_stream: str,
    is_global: bool = False,
) -> str:
    """R111: Classify the authority level of a stream output artifact.

    Returns one of the STREAM_OUTPUT_AUTHORITY keys.
    """
    if not artifact_stream or not target_stream:
        return "ARCHIVED_LAST_WRITER_SNAPSHOT"
    if artifact_stream == target_stream:
        return "CURRENT_STREAM_AUTHORITY"
    if is_global:
        return "ARCHIVED_LAST_WRITER_SNAPSHOT"
    return "CROSS_STREAM_REFERENCE"


def detect_wrong_stream_next_sprint(
    next_sprint_text: str,
    target_stream: str,
    repo_root: Path | None = None,
    path_read: str = "reports/supervisor/next-sprint.md",
    source_kind: str = "workspace",
) -> dict[str, Any]:
    """R111/R112: Detect if global next-sprint.md is from a different stream.

    The global next-sprint.md is a last-writer-wins artifact. If the current
    package is for stream X but next-sprint.md was generated for stream Y,
    classify it as ARCHIVED_LAST_WRITER_SNAPSHOT (not authoritative).

    R112: Adds source tracing (path_read, source_kind, is_blocking).
    """
    # Extract stream from next-sprint.md header
    detected_stream = ""
    for line in next_sprint_text.splitlines()[:10]:
        if line.startswith("# Stream:"):
            detected_stream = line.split(":", 1)[1].strip().lower()
            break

    if not detected_stream:
        return {
            "check": "wrong_stream_next_sprint",
            "is_violation": False,
            "detected_stream": "",
            "target_stream": target_stream,
            "authority": "ARCHIVED_LAST_WRITER_SNAPSHOT",
            "path_read": path_read,
            "source_kind": source_kind,
            "is_blocking": False,
            "recommendation": "No stream header found in next-sprint.md; treating as snapshot.",
        }

    is_wrong = detected_stream != target_stream
    authority = classify_stream_output_authority(
        path_read,
        detected_stream,
        target_stream,
        is_global=True,
    )

    # R112: CURRENT_STREAM_AUTHORITY wrong-stream is blocking; ARCHIVED is not
    is_blocking = is_wrong and authority == "INVALID_WRONG_STREAM"

    return {
        "check": "wrong_stream_next_sprint",
        "is_violation": is_wrong,
        "detected_stream": detected_stream,
        "target_stream": target_stream,
        "authority": authority,
        "path_read": path_read,
        "source_kind": source_kind,
        "is_blocking": is_blocking,
        "recommendation": (
            f"Global next-sprint.md is {detected_stream} (target: {target_stream}). "
            f"Authority: {authority}. Source: {source_kind}."
        ),
    }


# R113: ODF formats that require spec linkage on PRODUCT_SOURCE items.
# These formats have entries in shared/qname-registry/ and validated QName coverage.
_ODF_SPEC_LINKAGE_FORMATS = frozenset({
    "fods", "fodt", "ods", "odt", "fodg", "fodp",
})


def detect_odf_spec_linkage(
    declaration: dict[str, Any],
) -> dict[str, Any]:
    """R113/Detector 19: Warn when ODF PRODUCT_SOURCE items lack spec refs.

    ODF formats (FODS, FODT, ODS, ODT, FODG, FODP) have QName registries in
    shared/qname-registry/ and spec-parity validators in governance_validators.py.
    When a PRODUCT_SOURCE item for one of these formats declares no spec_qname_refs
    AND no spec_fact_refs, it is missing verifiable spec linkage.

    Severity: high — downgrades overall verdict but does NOT block continuation.
    Other enforcement layers (TC-GUARD-001, skill registry, 6 governance validators)
    already enforce at different points; this detector adds sprint-review visibility.

    Scope: ODF formats only. Non-ODF formats (ZST, CSV, etc.) do not yet have
    QName registries and are exempt.
    """
    missing_items: list[str] = []

    for item in declaration.get("planned_work_items", []):
        if item.get("item_type") != "PRODUCT_SOURCE":
            continue
        fmt = (item.get("format") or "").lower()
        if fmt not in _ODF_SPEC_LINKAGE_FORMATS:
            continue
        has_qname = bool(item.get("spec_qname_refs"))
        has_fact = bool(item.get("spec_fact_refs"))
        if not has_qname and not has_fact:
            missing_items.append(item.get("item_id", "<unknown>"))

    is_violation = len(missing_items) > 0
    return {
        "check": "odf_spec_linkage",
        "is_violation": is_violation,
        "missing_items": missing_items,
        "recommendation": (
            f"ODF PRODUCT_SOURCE item(s) {missing_items} missing spec_qname_refs "
            f"and spec_fact_refs. Add spec linkage or use a non-ODF item_type."
            if is_violation
            else "All ODF PRODUCT_SOURCE items have adequate spec linkage."
        ),
    }


# R107: Severity mapping — determines how violations affect the cycle verdict
SEVERITY_MAP = {
    "generic_prompt": "high",
    "stale_gaps": "critical",
    "missing_raw_logs": "medium",
    "path_only_acceptance": "medium",
    "missing_evidence_manifest": "medium",
    "missing_report_files": "high",
    "missing_lane_ledger": "medium",
    "cross_stream_prompt_contamination": "critical",
    "missing_sample_outputs": "low",
    "dirty_git_state": "medium",
    "wrong_stream_gaps": "critical",
    "evidence_quality_score": "high",
    "declaration_completeness": "critical",
    "test_count_regression": "high",
    "stale_evidence_manifest": "high",
    "missing_changed_files": "high",
    "stream_local_authority": "low",
    "wrong_stream_next_sprint": "medium",  # R111: caveat, not block (global is last-writer)
    "odf_spec_linkage": "high",  # R113: downgrades verdict; ODF items need spec refs
}


def classify_violation_impact(checks: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify the aggregate impact of all anti-skip violations.

    Returns:
      block: bool — at least one critical violation, must stop
      downgrade: bool — at least one high violation, verdict should be downgraded
      caveats: list — medium violations to note
      notes: list — low violations (informational)
    """
    violations = [c for c in checks if c.get("is_violation")]
    block_items = []
    downgrade_items = []
    caveats = []
    notes = []

    for v in violations:
        severity = SEVERITY_MAP.get(v["check"], "medium")
        v["severity"] = severity
        if severity == "critical":
            block_items.append(v["check"])
        elif severity == "high":
            downgrade_items.append(v["check"])
        elif severity == "medium":
            caveats.append(v["check"])
        else:
            notes.append(v["check"])

    return {
        "block": len(block_items) > 0,
        "downgrade": len(downgrade_items) > 0,
        "block_items": block_items,
        "downgrade_items": downgrade_items,
        "caveats": caveats,
        "notes": notes,
        "total_violations": len(violations),
    }


def run_all_checks(
    prompt_text: str = "",
    gaps_data: dict[str, Any] | None = None,
    expected_sprint: str = "",
    evidence_root: Path | None = None,
    declaration: dict[str, Any] | None = None,
    grades: dict[str, Any] | list | None = None,
    target_stream: str = "",
    repo_root: Path | None = None,
    sample_outputs_dir: Path | None = None,
    prior_test_count: int = 0,
    next_sprint_text: str = "",
    declared_scope: list[str] | None = None,
) -> dict[str, Any]:
    """Run all 19 anti-skip checks and return consolidated results with severity."""
    results = []

    # Original 4 detectors
    if prompt_text:
        results.append(detect_generic_prompt(prompt_text))
    if gaps_data:
        results.append(detect_stale_gaps(gaps_data, expected_sprint))
    if evidence_root:
        results.append(detect_missing_raw_logs(evidence_root, declaration))
    if grades is not None:
        results.append(detect_path_only_acceptance(grades))

    # R103 detectors
    if evidence_root:
        results.append(detect_missing_evidence_manifest(evidence_root, declaration))
    if declaration:
        results.append(detect_missing_report_files(declaration, repo_root))
    if evidence_root:
        results.append(detect_missing_lane_ledger(
            evidence_root,
            sample_outputs_dir=sample_outputs_dir,
            declaration=declaration,
            repo_root=repo_root,
        ))
    if prompt_text and target_stream:
        # Extract declared item types from declaration for stream-aware exemption
        _scope = declared_scope
        if _scope is None and declaration:
            _scope = list({
                item.get("item_type", "")
                for item in declaration.get("work_items", [])
                if item.get("item_type")
            })
        results.append(detect_cross_stream_prompt_contamination(
            prompt_text, target_stream, declared_scope=_scope,
        ))

    # R104 detector (R112: also check declaration/manifest for sample_output artifacts)
    if evidence_root:
        results.append(detect_missing_sample_outputs(
            evidence_root,
            sample_outputs_dir=sample_outputs_dir,
            declaration=declaration,
        ))

    # R105 detectors
    if declaration:
        results.append(detect_dirty_git_state(declaration))
    if gaps_data and target_stream:
        results.append(detect_wrong_stream_gaps(gaps_data, target_stream))

    # R106 detectors
    if grades is not None:
        results.append(detect_evidence_quality_score(grades))
    if declaration:
        results.append(detect_declaration_completeness(declaration))
    if declaration:
        results.append(detect_test_count_regression(declaration, prior_test_count))

    # R107 detectors
    if evidence_root and expected_sprint:
        results.append(detect_stale_evidence_manifest(evidence_root, expected_sprint))
    if declaration:
        results.append(detect_missing_changed_files(declaration, repo_root))

    # R109 detector
    if target_stream:
        results.append(detect_stream_local_authority(target_stream, repo_root))

    # R111 detector: wrong-stream global next-sprint
    if next_sprint_text and target_stream:
        results.append(detect_wrong_stream_next_sprint(next_sprint_text, target_stream, repo_root))

    # R113 detector: ODF PRODUCT_SOURCE items missing spec linkage
    if declaration:
        results.append(detect_odf_spec_linkage(declaration))

    violations = [r for r in results if r.get("is_violation")]

    # R107: Classify violation impact using severity mapping
    impact = classify_violation_impact(results)

    return {
        "total_checks": len(results),
        "violations": len(violations),
        "all_pass": len(violations) == 0,
        "checks": results,
        "impact": impact,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt-file", type=Path, default=None)
    parser.add_argument("--gaps-file", type=Path, default=None)
    parser.add_argument("--expected-sprint", default="")
    parser.add_argument("--evidence-root", type=Path, default=None)
    parser.add_argument("--declaration", type=Path, default=None)
    parser.add_argument("--grades-file", type=Path, default=None)
    args = parser.parse_args()

    prompt_text = ""
    if args.prompt_file and args.prompt_file.exists():
        prompt_text = args.prompt_file.read_text(encoding="utf-8")

    gaps_data = None
    if args.gaps_file and args.gaps_file.exists():
        gaps_data = json.loads(args.gaps_file.read_text(encoding="utf-8"))

    declaration = None
    if args.declaration and args.declaration.exists():
        declaration = yaml.safe_load(args.declaration.read_text(encoding="utf-8"))

    grades = None
    if args.grades_file and args.grades_file.exists():
        grades = json.loads(args.grades_file.read_text(encoding="utf-8"))

    result = run_all_checks(
        prompt_text=prompt_text,
        gaps_data=gaps_data,
        expected_sprint=args.expected_sprint,
        evidence_root=args.evidence_root,
        declaration=declaration,
        grades=grades,
    )

    print(json.dumps(result, indent=2))
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
