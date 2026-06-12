"""validate_prompt_quality.py — Stream Prompt Quality Validator

Validates that generated stream prompts meet quality requirements:
1. Not generic (has stream-specific content)
2. Correct stream identity (no wrong-stream markers in body)
3. Has repair lane when repairs exist
4. Has advancement lane when safe advancement exists
5. Has evidence declaration/manifest requirement
6. Has stream-specific context (not boilerplate)

Exit codes:
  0 — all prompts pass quality checks
  1 — quality violations found
"""

from __future__ import annotations

from typing import Any


STREAM_IDENTITY_MARKERS = {
    "mainstream": ["product", "fods", "fodt", "netpbm", "gate 11", "src/net", "src/python"],
    "acceleration": ["tool", "gap selector", "anti-skip", "package", "validator"],
    "skills": ["skill", "governed", "registry", "transcript", "handoff"],
    "supervisor": ["pipeline", "grading", "continuation", "evidence-review", "autonomous-cycle"],
}

EVIDENCE_MARKERS = [
    "evidence-declaration",
    "evidence declaration",
    "evidence-manifest",
    "autonomous-cycle",
    "autonomous cycle",
    "declaration review package",
]


def validate_prompt_quality(
    prompt_text: str,
    target_stream: str,
    has_repairs: bool = False,
    has_advancement: bool = True,
) -> dict[str, Any]:
    """Validate a stream prompt against quality requirements."""
    lower = prompt_text.lower()
    checks = []

    # Check 1: Not generic
    word_count = len(prompt_text.split())
    is_too_short = word_count < 50
    checks.append({
        "check": "not_generic",
        "pass": not is_too_short,
        "detail": f"Word count: {word_count}" + (" (too short)" if is_too_short else ""),
    })

    # Check 2: Has stream identity markers
    markers = STREAM_IDENTITY_MARKERS.get(target_stream, [])
    found = [m for m in markers if m in lower]
    has_identity = len(found) >= 2
    checks.append({
        "check": "stream_identity",
        "pass": has_identity,
        "markers_found": found,
        "detail": f"Found {len(found)}/{len(markers)} stream markers",
    })

    # Check 3: Has repair lane if repairs exist
    if has_repairs:
        repair_terms = ["repair", "fix", "rework", "defect", "d10"]
        has_repair_lane = any(t in lower for t in repair_terms)
        checks.append({
            "check": "repair_lane",
            "pass": has_repair_lane,
            "detail": "Repair lane present" if has_repair_lane else "Missing repair lane despite repairs needed",
        })

    # Check 4: Has advancement lane (R108: stream-aware terms, R110: broadened)
    if has_advancement:
        # Generic advancement terms (mainstream/product)
        advance_terms = ["advance", "improve", "add", "implement", "new"]
        # R108/R110: Stream-specific advancement terms
        stream_advance_terms = {
            "supervisor": ["pipeline", "grading", "strengthen", "enhance", "harden",
                          "capture", "enforce", "validate", "expand", "deepen"],
            "acceleration": ["detector", "validator", "harden", "expand", "enhance",
                            "severity", "enforce", "integrate",
                            # R110: Terms matching STREAM_FORWARD_WORK descriptions
                            "detection accuracy", "quality scoring",
                            "continuation policy", "stop condition",
                            "strengthen", "refine"],
            "skills": ["skill", "governed", "transcript", "expand", "harden",
                      "validate", "registry"],
        }
        all_terms = advance_terms + stream_advance_terms.get(target_stream, [])
        has_advance = any(t in lower for t in all_terms)
        checks.append({
            "check": "advancement_lane",
            "pass": has_advance,
            "detail": "Advancement lane present" if has_advance else "Missing advancement content",
        })

    # Check 5: Has evidence requirement
    has_evidence = any(m in lower for m in EVIDENCE_MARKERS)
    checks.append({
        "check": "evidence_requirement",
        "pass": has_evidence,
        "detail": "Evidence declaration/manifest requirement present" if has_evidence else "Missing evidence closeout requirement",
    })

    # Check 6: No wrong-stream identity (reuse anti-skip logic concept)
    from anti_skip_checker import _strip_boundary_section, STREAM_BOUNDARY_FORBIDDEN
    clean_text = _strip_boundary_section(prompt_text).lower()
    forbidden = STREAM_BOUNDARY_FORBIDDEN.get(target_stream, [])
    forbidden_found = [f for f in forbidden if f.lower() in clean_text]
    no_wrong_stream = len(forbidden_found) == 0
    checks.append({
        "check": "no_wrong_stream",
        "pass": no_wrong_stream,
        "forbidden_found": forbidden_found,
        "detail": "Clean stream boundaries" if no_wrong_stream else f"Wrong-stream refs: {forbidden_found}",
    })

    # Check 7 (R106): Sprint structure — prompt should have distinct sections
    section_markers = ["##", "lane", "train", "phase", "step", "task"]
    section_hits = sum(1 for m in section_markers if m in lower)
    has_structure = section_hits >= 2
    checks.append({
        "check": "prompt_structure",
        "pass": has_structure,
        "section_markers_found": section_hits,
        "detail": f"Prompt has {section_hits} structural markers" + ("" if has_structure else " (need 2+)"),
    })

    # Check 8 (GEC-TC-005): No unsafe commit/push authorization wording
    _UNSAFE_PROMPT_PATTERNS = [
        "authorized git commit + push",
        "authorized git commit+push",
        "commit + push (requires",
        "commit and push to remote",
    ]
    unsafe_found = [p for p in _UNSAFE_PROMPT_PATTERNS if p in lower]
    no_unsafe_wording = len(unsafe_found) == 0
    checks.append({
        "check": "no_unsafe_commit_push_wording",
        "pass": no_unsafe_wording,
        "unsafe_patterns_found": unsafe_found,
        "detail": (
            "No unsafe commit/push authorization wording found"
            if no_unsafe_wording
            else f"UNSAFE wording in prompt: {unsafe_found} — remove or replace with safe alternatives"
        ),
    })

    # Check 9: No executable unauthorized mutation instructions
    from tools.supervisor.autonomy_route_decider import check_prompt_for_unsafe_instructions
    check9 = check_prompt_for_unsafe_instructions(prompt_text)
    checks.append({
        "check": check9["check"],
        "pass": check9["pass"],
        "detail": check9["detail"],
        "violations": check9.get("violations", []),
    })

    all_pass = all(c["pass"] for c in checks)
    return {
        "valid": all_pass,
        "target_stream": target_stream,
        "total_checks": len(checks),
        "passed": sum(1 for c in checks if c["pass"]),
        "failed": sum(1 for c in checks if not c["pass"]),
        "checks": checks,
    }


# R108: Next-work-items stream validation
PRODUCT_FACTORY_LANES = {"product-advancement"}
NON_MAINSTREAM_STREAMS = {"acceleration", "skills", "supervisor"}


def validate_next_work_items(
    work_items: dict[str, Any],
    target_stream: str,
) -> dict[str, Any]:
    """Validate next-work-items output for stream correctness.

    Checks:
    1. stream field matches target_stream
    2. Non-mainstream streams have no product-factory source items
    3. Non-mainstream streams have stream-specific forward work
    4. All items have required fields
    """
    checks = []
    items = work_items.get("items", [])

    # Check 1: stream field present and correct
    declared_stream = work_items.get("stream", "")
    stream_match = declared_stream == target_stream
    checks.append({
        "check": "stream_field_match",
        "pass": stream_match,
        "detail": f"stream={declared_stream}, target={target_stream}",
    })

    # Check 2: No product-factory items in non-mainstream streams
    if target_stream in NON_MAINSTREAM_STREAMS:
        product_items = [i for i in items if i.get("source") == "product-factory"]
        no_product = len(product_items) == 0
        checks.append({
            "check": "no_wrong_stream_items",
            "pass": no_product,
            "detail": f"{len(product_items)} product-factory items"
                      + (" (wrong stream)" if product_items else " (clean)"),
        })

    # Check 3: Non-mainstream has stream-specific forward work
    if target_stream in NON_MAINSTREAM_STREAMS:
        expected_lane = f"{target_stream}-advancement"
        stream_items = [i for i in items if i.get("lane") == expected_lane]
        has_forward = len(stream_items) > 0
        checks.append({
            "check": "has_stream_forward_work",
            "pass": has_forward,
            "detail": f"{len(stream_items)} {expected_lane} items",
        })

    # Check 4: All items have required fields
    required_fields = {"item_id", "title", "lane", "priority", "source"}
    missing = []
    for i, item in enumerate(items):
        item_missing = required_fields - set(item.keys())
        if item_missing:
            missing.append(f"item[{i}] missing: {item_missing}")
    all_have_fields = len(missing) == 0
    checks.append({
        "check": "item_schema_valid",
        "pass": all_have_fields,
        "detail": "All items have required fields" if all_have_fields else "; ".join(missing[:3]),
    })

    all_pass = all(c["pass"] for c in checks)
    return {
        "valid": all_pass,
        "target_stream": target_stream,
        "total_checks": len(checks),
        "passed": sum(1 for c in checks if c["pass"]),
        "failed": sum(1 for c in checks if not c["pass"]),
        "checks": checks,
    }
