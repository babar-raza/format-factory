"""validate_package_identity.py — Package Identity Validator

Validates that primary files in a declaration review package ZIP match the
declared stream. Detects cross-stream contamination where global supervisor
state (from whatever stream ran last) is packaged as if it belongs to the
declaring stream.

Checks:
1. supervisor/latest-cycle-summary.md — sprint ID should match declaration
2. supervisor/evidence-review.md — sprint ID should match declaration
3. supervisor/contradictions.md — sprint ID should match declaration
4. state/context-pack.yaml — latest_sprint should match declaration
5. state/selected-product-gaps.json — should be fresh for declared sprint
6. evidence/evidence-declaration.yaml — run_id must match
7. review/supervisor-review.json — run_id must match (if present)

Exit codes:
  0 — identity validated
  1 — identity violations found
  9 — unexpected error
"""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any

import yaml


def _extract_sprint_from_text(text: str) -> str | None:
    """Extract sprint ID from text content using common patterns."""
    patterns = [
        r"Sprint(?:\s+ID)?:\s*(.+?)(?:\n|$)",
        r"sprint_id:\s*(.+?)(?:\n|$)",
        r"sprint:\s*(.+?)(?:\n|$)",
        r"Run:\s*(.+?)(?:\n|$)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip().strip('"').strip("'")
            if val and len(val) > 5:
                return val
    return None


def _extract_stream_from_sprint(sprint_id: str) -> str:
    """Detect stream from sprint ID naming convention."""
    lower = sprint_id.lower()
    if "acceleration" in lower:
        return "acceleration"
    if "skills" in lower:
        return "skills"
    if "supervisor" in lower and "acceleration" not in lower:
        return "supervisor"
    if "mainstream" in lower:
        return "mainstream"
    # Older sprints without stream prefix are mainstream
    return "mainstream"


def validate_package_identity(
    zip_path: Path,
    expected_run_id: str,
    expected_sprint_id: str,
    expected_stream: str,
) -> dict[str, Any]:
    """Validate that package primary files match the declared identity."""
    results = []

    if not zip_path.exists():
        return {
            "valid": False,
            "error": f"ZIP not found: {zip_path}",
            "checks": [],
        }

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

        # Check 1: evidence/evidence-declaration.yaml
        if "evidence/evidence-declaration.yaml" in names:
            content = zf.read("evidence/evidence-declaration.yaml").decode("utf-8")
            decl = yaml.safe_load(content)
            decl_run = decl.get("run_id", "")
            decl_sprint = decl.get("sprint_id", "")
            results.append({
                "file": "evidence/evidence-declaration.yaml",
                "check": "run_id",
                "expected": expected_run_id,
                "actual": decl_run,
                "status": "MATCH" if decl_run == expected_run_id else "WRONG_STREAM",
            })
            results.append({
                "file": "evidence/evidence-declaration.yaml",
                "check": "sprint_id",
                "expected": expected_sprint_id,
                "actual": decl_sprint,
                "status": "MATCH" if decl_sprint == expected_sprint_id else "WRONG_STREAM",
            })

        # Check 2: supervisor/latest-cycle-summary.md
        if "supervisor/latest-cycle-summary.md" in names:
            content = zf.read("supervisor/latest-cycle-summary.md").decode("utf-8")
            detected_sprint = _extract_sprint_from_text(content)
            detected_stream = _extract_stream_from_sprint(detected_sprint or "")
            match = detected_stream == expected_stream if detected_sprint else None
            results.append({
                "file": "supervisor/latest-cycle-summary.md",
                "check": "stream_identity",
                "expected_stream": expected_stream,
                "detected_sprint": detected_sprint,
                "detected_stream": detected_stream,
                "status": "MATCH" if match else ("WRONG_STREAM" if match is False else "UNVERIFIABLE"),
            })

        # Check 3: supervisor/evidence-review.md
        if "supervisor/evidence-review.md" in names:
            content = zf.read("supervisor/evidence-review.md").decode("utf-8")
            detected_sprint = _extract_sprint_from_text(content)
            detected_stream = _extract_stream_from_sprint(detected_sprint or "")
            match = detected_stream == expected_stream if detected_sprint else None
            results.append({
                "file": "supervisor/evidence-review.md",
                "check": "stream_identity",
                "expected_stream": expected_stream,
                "detected_sprint": detected_sprint,
                "detected_stream": detected_stream,
                "status": "MATCH" if match else ("WRONG_STREAM" if match is False else "UNVERIFIABLE"),
            })

        # Check 4: supervisor/contradictions.md
        if "supervisor/contradictions.md" in names:
            content = zf.read("supervisor/contradictions.md").decode("utf-8")
            detected_sprint = _extract_sprint_from_text(content)
            detected_stream = _extract_stream_from_sprint(detected_sprint or "")
            match = detected_stream == expected_stream if detected_sprint else None
            results.append({
                "file": "supervisor/contradictions.md",
                "check": "stream_identity",
                "expected_stream": expected_stream,
                "detected_sprint": detected_sprint,
                "detected_stream": detected_stream,
                "status": "MATCH" if match else ("WRONG_STREAM" if match is False else "UNVERIFIABLE"),
            })

        # Check 5: state/context-pack.yaml
        if "state/context-pack.yaml" in names:
            content = zf.read("state/context-pack.yaml").decode("utf-8")
            cp = yaml.safe_load(content)
            latest = cp.get("latest_sprint", {})
            cp_sprint = latest.get("sprint_id", "")
            cp_stream = _extract_stream_from_sprint(cp_sprint)
            match = cp_stream == expected_stream if cp_sprint else None
            results.append({
                "file": "state/context-pack.yaml",
                "check": "latest_sprint_stream",
                "expected_stream": expected_stream,
                "detected_sprint": cp_sprint,
                "detected_stream": cp_stream,
                "status": "MATCH" if match else ("WRONG_STREAM" if match is False else "UNVERIFIABLE"),
            })

        # Check 6: state/selected-product-gaps.json
        if "state/selected-product-gaps.json" in names:
            content = zf.read("state/selected-product-gaps.json").decode("utf-8")
            try:
                gaps = json.loads(content)
                gap_sprint = gaps.get("sprint_id", gaps.get("requested_sprint", ""))
                is_stale = gap_sprint and gap_sprint != expected_sprint_id
                # Also check if it's from a completely different round
                gap_stream = _extract_stream_from_sprint(gap_sprint)
                results.append({
                    "file": "state/selected-product-gaps.json",
                    "check": "freshness",
                    "expected_sprint": expected_sprint_id,
                    "actual_sprint": gap_sprint,
                    "detected_stream": gap_stream,
                    "status": "STALE" if is_stale else ("MATCH" if gap_sprint else "UNVERIFIABLE"),
                })
            except json.JSONDecodeError:
                results.append({
                    "file": "state/selected-product-gaps.json",
                    "check": "freshness",
                    "status": "UNVERIFIABLE",
                    "error": "invalid JSON",
                })

        # Check 7: review/supervisor-review.json
        for review_name in ["review/supervisor-review.json", "review/supervisor-review.md"]:
            if review_name in names:
                content = zf.read(review_name).decode("utf-8")
                detected_sprint = _extract_sprint_from_text(content)
                detected_stream = _extract_stream_from_sprint(detected_sprint or "")
                match = detected_stream == expected_stream if detected_sprint else None
                results.append({
                    "file": review_name,
                    "check": "stream_identity",
                    "expected_stream": expected_stream,
                    "detected_sprint": detected_sprint,
                    "detected_stream": detected_stream,
                    "status": "MATCH" if match else ("WRONG_STREAM" if match is False else "UNVERIFIABLE"),
                })

    # Aggregate
    violations = [r for r in results if r["status"] in ("WRONG_STREAM", "STALE")]
    matches = [r for r in results if r["status"] == "MATCH"]
    unverifiable = [r for r in results if r["status"] == "UNVERIFIABLE"]

    return {
        "valid": len(violations) == 0,
        "total_checks": len(results),
        "matches": len(matches),
        "violations": len(violations),
        "unverifiable": len(unverifiable),
        "violation_details": violations,
        "checks": results,
    }


def validate_package_identity_from_declaration(
    zip_path: Path,
    declaration: dict[str, Any],
) -> dict[str, Any]:
    """Convenience: extract identity from declaration and validate."""
    run_id = declaration.get("run_id", "")
    sprint_id = declaration.get("sprint_id", "")
    stream = _extract_stream_from_sprint(sprint_id)
    return validate_package_identity(zip_path, run_id, sprint_id, stream)
