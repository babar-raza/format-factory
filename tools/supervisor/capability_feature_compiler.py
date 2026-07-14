"""capability_feature_compiler.py — Translate gap-ledger.json gaps into next-work-items.json.

Implements the design spec in docs/code-quality/capability-feature-compiler-spec.md (TC-CAPABILITY-REPAIR-001).
TC-CAPABILITY-REPAIR-002 (cheerful-floating-glade): Phase 2 implementation.

CLI:
    python tools/supervisor/capability_feature_compiler.py \\
        --gap-ledger reports/capability-layer/gap-ledger.json \\
        --output reports/supervisor/next-work-items.json \\
        [--max-items 20] \\
        [--dry-run]

Exit codes:
    0 — success
    1 — gap-ledger not found or invalid schema
    2 — output write failure
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# ── QName validation schema + validators ─────────────────────────────────────


@dataclass
class CompiledCapability:
    """Schema for a capability validated against QName authority.

    TC-ARC-010: compiled_capability output schema for --validate-qnames mode.
    """

    capability_id: str
    product: str
    specification_facts: list[str] = field(default_factory=list)
    qnames: list[str] = field(default_factory=list)
    domain_owner: str = ""
    model_types: list[str] = field(default_factory=list)
    parser_obligations: list[str] = field(default_factory=list)
    writer_obligations: list[str] = field(default_factory=list)
    public_api_options: list[str] = field(default_factory=list)
    test_obligations: list[str] = field(default_factory=list)
    unsupported_states: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


class QNameValidationError(ValueError):
    """Raised when a capability fails QName authority validation."""


# Root document types that must not own nested QName behavior.
_ROOT_DOCUMENT_TYPES: set[str] = {
    "FodsDocument", "FodtDocument", "CsvDocument", "TsvDocument",
    "NdjsonDocument", "HtmlDocument", "MarkdownDocument", "Document",
    "Workbook",
}
# Tokens that indicate a type belongs to a child/nested QName concept.
_NESTED_TYPE_TOKENS: set[str] = {
    "Cell", "Row", "Column", "Sheet", "Worksheet", "Style",
    "Paragraph", "Run", "Span", "Section", "Table", "Frame",
}


def validate_qname_authority(cap: CompiledCapability) -> None:
    """Reject if qnames[] is empty — every capability needs QName authority."""
    if not cap.qnames:
        raise QNameValidationError(
            f"[V-QNAME-001] {cap.capability_id} ({cap.product}): qnames[] is empty. "
            "Every capability must trace to at least one format-spec QName."
        )


def validate_no_root_nesting(cap: CompiledCapability) -> None:
    """Reject if a root document type owns nested-QName model_types."""
    if cap.domain_owner not in _ROOT_DOCUMENT_TYPES:
        return
    nested = [t for t in cap.model_types
              if any(tok in t for tok in _NESTED_TYPE_TOKENS)]
    if nested:
        raise QNameValidationError(
            f"[V-QNAME-002] {cap.capability_id} ({cap.product}): domain_owner="
            f"'{cap.domain_owner}' is a root type but model_types includes nested "
            f"concepts {nested}. Nested behavior must belong to child types."
        )


def validate_parser_writer_obligations(cap: CompiledCapability) -> None:
    """Reject if there are getter public APIs but no parser obligations."""
    getter_options = [
        o for o in cap.public_api_options
        if any(tok in o.lower() for tok in ("get", "getter", "property", "read"))
    ]
    if getter_options and not cap.parser_obligations:
        raise QNameValidationError(
            f"[V-QNAME-003] {cap.capability_id} ({cap.product}): public_api_options "
            f"includes getters {getter_options} but parser_obligations is empty. "
            "Every getter must have a parser obligation."
        )


def _gap_to_compiled_capability(gap: dict) -> CompiledCapability:
    """Convert a gap-ledger entry to a CompiledCapability for validation."""
    return CompiledCapability(
        capability_id=gap.get("gap_id", ""),
        product=gap.get("format", gap.get("product_id", "")),
        specification_facts=gap.get("spec_facts") or [],
        qnames=gap.get("qnames") or [],
        domain_owner=gap.get("domain_owner", ""),
        model_types=gap.get("model_types") or [],
        parser_obligations=gap.get("parser_obligations") or [],
        writer_obligations=gap.get("writer_obligations") or [],
        public_api_options=gap.get("public_api_options") or [],
        test_obligations=gap.get("test_obligations") or [],
        unsupported_states=gap.get("unsupported_states") or [],
        dependencies=gap.get("dependencies") or [],
    )


def validate_capability(cap: CompiledCapability) -> list[str]:
    """Run all QName validators. Returns list of error messages (empty = PASS)."""
    errors: list[str] = []
    for validator in (
        validate_qname_authority,
        validate_no_root_nesting,
        validate_parser_writer_obligations,
    ):
        try:
            validator(cap)
        except QNameValidationError as exc:
            errors.append(str(exc))
    return errors


# ── Priority scoring constants ────────────────────────────────────────────────

_BASE_PRIORITY: dict[str, int] = {
    "P0": 0, "P1": 10, "P2": 20, "P3": 30, "P4": 40,
    "P5": 50, "P6": 60, "P7": 70, "P8": 80,
}

_EVIDENCE_MAP: dict[str, str] = {
    "missing_test_coverage": "Tests added and passing",
    "missing_implementation": "Implementation committed, tests pass",
    "spec_parity_gap": "spec_qname on class, spec fact referenced",
    "architecture_only": "Behavioral implementation replacing stub",
    "missing_qname_registration": "QName registry entry with python_file",
    "missing_capability_annotation": "capability_ref in declaration",
}
_EVIDENCE_DEFAULT = "Work item accepted by supervisor pipeline"

# Lanes 14-15 are machinery-owned; skip them
_MAX_PRODUCT_LANE = 13

# Statuses that exclude a gap from work selection.
# CLOSED/closed: already implemented; DEFERRED_BY_DESIGN/DEFERRED: intentionally deferred;
# test_verified: state beyond gap-level (capability is done).
# implementation_verified_no_tests: promoted by close_implementation_verified_gaps() —
#   re-enter work queue for test writing, NOT selected as product work item.
# TC-DEFERRED-FILTER-001 (2026-06-25): extended to handle all non-actionable statuses.
# TC-BOOL-003 (2026-07-12): replaced "implementation_verified" with
#   "implementation_verified_no_tests" so that gaps with confirmed test coverage are
#   closed by the scanner, not stuck in limbo. Gaps without tests re-enter queue.
_SKIP_STATUSES = {
    "closed", "CLOSED",
    "DEFERRED_BY_DESIGN", "DEFERRED",
    "test_verified", "implementation_verified", "implementation_verified_no_tests",
    "SAL_UNGROUNDED",  # RC-4 fix: no SAL fact authority; excluded until spec facts exist
}

# Statuses that mean "not yet an open gap"
_FAIL_STATUSES = {"implementation_verified_no_tests"}


def _base_priority(gap: dict) -> int:
    prio = gap.get("priority", "P8")
    return _BASE_PRIORITY.get(prio, 80)


def _impact_penalty(gap: dict) -> int:
    ci = gap.get("commercial_impact", "NONE")
    fi = gap.get("foss_impact", "NONE")
    if ci == "HIGH" and fi == "HIGH":
        return -10
    if ci == "HIGH":
        return -5
    if fi == "HIGH":
        return -3
    return 0


def _blocker_bonus(gap: dict) -> int:
    bonus = 0
    if gap.get("blocks_poc"):
        bonus -= 8
    if gap.get("blocks_readiness"):
        bonus -= 5
    return bonus


def _score(gap: dict) -> int:
    base = _base_priority(gap) + _impact_penalty(gap) + _blocker_bonus(gap)
    fmt = gap.get("format", gap.get("product_id", "")).split("-")[0].lower()
    dl = _classify_deepening_lane(gap)
    base += _lane_balance_penalty(dl, fmt)
    return base


def _lane(gap: dict) -> str:
    owning_lane = gap.get("owning_lane", 1)
    try:
        lane_int = int(owning_lane)
    except (TypeError, ValueError):
        lane_int = 1
    return "product" if lane_int <= _MAX_PRODUCT_LANE else "machinery"


_DOM_GAP_TYPES = frozenset({
    "spec_parity_gap", "architecture_only", "missing_qname_registration",
    "dom_maturity_d2", "dom_maturity_d3", "dom_maturity_d4", "dom_maturity_d5",
})


def _classify_deepening_lane(gap: dict) -> str:
    """Classify gap as feature or dom deepening work."""
    # Tier 1: explicit field takes precedence (TC-VPR-004)
    explicit = gap.get("deepening_lane", "")
    if explicit in ("dom", "feature"):
        return explicit
    # Tier 2: known gap_type taxonomy including DOM maturity types
    gap_type = gap.get("gap_type", "")
    if gap_type in _DOM_GAP_TYPES:
        return "dom"
    # Tier 3: keyword heuristics (unchanged)
    cap = gap.get("capability_name", "").lower()
    if any(kw in cap for kw in ("object_model", "dom_", "navigation", "mutation", "spec_class")):
        return "dom"
    return "feature"


def _lane_balance_penalty(lane: str, format_name: str) -> int:
    """Soft penalty for overrepresented lane (starvation prevention)."""
    import yaml
    ledger_path = Path("registry/product-deepening-ledger.yaml")
    if not ledger_path.exists():
        return 0
    try:
        ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8")) or []
    except Exception:
        return 0
    entry = next((e for e in ledger if e.get("format") == format_name.lower()), {})
    mode = entry.get("execution_mode", "AUTO")
    if mode == "FEATURE_ONLY" and lane == "dom":
        return 999
    if mode == "DOM_ONLY" and lane == "feature":
        return 999
    a = entry.get("lane_a_consecutive", 0)
    b = entry.get("lane_b_consecutive", 0)
    threshold = entry.get("lane_starvation_threshold", 3)
    if lane == "feature" and a - b >= threshold:
        return 15
    if lane == "dom" and b - a >= threshold:
        return 15
    return 0


def _evidence_expected(gap: dict) -> str:
    return _EVIDENCE_MAP.get(gap.get("gap_type", ""), _EVIDENCE_DEFAULT)


def _is_external_gate(gap: dict) -> bool:
    return bool(gap.get("blocks_readiness") and gap.get("product_type") == "commercial")


def _description(gap: dict) -> str:
    suggested = gap.get("suggested_taskcard", "")
    if suggested:
        return suggested
    parts = []
    cap = gap.get("capability_name", "")
    fmt = gap.get("format", "")
    gtype = gap.get("gap_type", "")
    state = gap.get("current_state", "")
    if cap and fmt:
        parts.append(f"Implement {cap} for {fmt}.")
    if gtype:
        parts.append(f"Gap type: {gtype}.")
    if state:
        parts.append(f"Current state: {state}.")
    return " ".join(parts) or f"Close gap {gap.get('gap_id', '')}."


def _human_required(gap: dict) -> bool:
    blockers = gap.get("blockers") or []
    return any("TRUE_EXTERNAL_GATE" in str(b) for b in blockers)


def _is_unknown_capability(gap: dict) -> bool:
    """RC-001 quality gate: detect unresolved spec gaps with no real capability name.

    Returns True if capability_name is exactly "unknown" (case-insensitive), None, or "".
    Substring check is intentionally avoided to avoid false positives on legitimate names
    like "parse_unknown_tags" or similar. Exact equality only (shimmering-rolling-meerkat).
    """
    cap_name = gap.get("capability_name") or ""
    return cap_name.strip().lower() == "unknown" or cap_name.strip() == ""


def _gap_to_work_item(gap: dict, score: int) -> dict:
    gap_id = gap.get("gap_id", "")
    blockers = gap.get("blockers") or []
    verification = gap.get("suggested_verification", "")

    # RC-001 (Fix-RC-001, shimmering-rolling-meerkat): quarantine items with no spec authority.
    # Items where capability_name == "unknown" or "" cannot satisfy RULE-LIB-002
    # (every symbol must trace to a QName). Route to quarantine lane, mark non-executable.
    if _is_unknown_capability(gap):
        return {
            "item_id": f"WI-{gap_id}",
            "title": f"[QUARANTINE] {gap.get('capability_name', 'unknown')} for {gap.get('format', 'Unknown')}",
            "lane": "quarantine-needs-sal",
            "quarantine_reason": "spec_fact_not_established",
            "blocked_by": "TC-SAL-001",
            "agent_can_execute": False,
            "execution_status": "blocked-missing-spec-authority",
            "priority": score,
            "source": "gap_ledger",
            "gap_id": gap_id,
            "gap_ref": gap_id,
            "gap_ledger_ref": gap_id,
            "human_required": False,
            "external_gate": False,
        }

    return {
        "item_id": f"WI-{gap_id}",
        "title": f"{gap.get('capability_name', 'Unknown')} for {gap.get('format', 'Unknown')}",
        "lane": _lane(gap),
        "priority": score,
        "description": _description(gap),
        "acceptance_criteria": verification or "Verification passes",
        "verification_command": verification,
        "evidence_expected": _evidence_expected(gap),
        "source": "gap_ledger",
        "stop_reason_adjudication": "agent-owned",
        "human_required": _human_required(gap),
        "blocked_by": blockers if blockers else None,
        "external_gate": _is_external_gate(gap),
        "gap_id": gap_id,
        "gap_ref": gap_id,
        "gap_ledger_ref": gap_id,
        "spec_facts": gap.get("spec_facts") or [],
        "deepening_lane": _classify_deepening_lane(gap),
    }


def _sort_key(item: dict) -> tuple:
    """Tie-breaking: score ASC, blocks_poc DESC, blocks_readiness DESC, gap_id ASC."""
    gap_ref = item.get("gap_id", "")
    return (item["priority"], gap_ref)


def compile_gaps(
    gaps: list[dict],
    max_items: int = 20,
) -> tuple[list[dict], list[dict]]:
    """Filter, score, deduplicate, and sort gaps.

    Returns (items, deduplicated_items).
    """
    # Step 1: filter
    filtered = []
    for gap in gaps:
        if gap.get("status") in _SKIP_STATUSES:
            continue
        try:
            lane_int = int(gap.get("owning_lane", 1))
        except (TypeError, ValueError):
            lane_int = 1
        if lane_int >= 14:
            continue
        filtered.append(gap)

    # Step 2: score
    scored = [(gap, _score(gap)) for gap in filtered]

    # Step 3: deduplicate by format+capability (keep lowest score)
    best: dict[tuple, tuple] = {}
    for gap, score in scored:
        key = (gap.get("format", ""), gap.get("capability_name", ""))
        if key not in best or score < best[key][1]:
            best[key] = (gap, score)

    deduped_gaps = {id(g) for g, _ in best.values()}
    dedup_items = [
        _gap_to_work_item(gap, sc)
        for gap, sc in scored
        if id(gap) not in deduped_gaps
    ]

    # Step 4: build work items from deduped set, sort, truncate
    items = [_gap_to_work_item(gap, sc) for gap, sc in best.values()]
    items.sort(key=_sort_key)
    return items[:max_items], dedup_items


def _run_validate_qnames(gaps: list[dict], format_filter: str | None) -> int:
    """Validate all gaps against QName authority rules.

    Returns 0 if all gaps that have qname-related fields pass, 3 if any fail.
    Gaps without qnames[] are flagged (V-QNAME-001) unless they also have no
    domain_owner and no model_types (i.e. they predate the QName schema).
    """
    target = [
        g for g in gaps
        if not format_filter or g.get("format", "").lower() == format_filter.lower()
    ]
    if not target:
        print(f"No gaps found for format filter '{format_filter}'.", file=sys.stderr)
        return 0

    all_errors: list[str] = []
    for gap in target:
        cap = _gap_to_compiled_capability(gap)
        errors = validate_capability(cap)
        all_errors.extend(errors)

    if all_errors:
        print(f"QName validation FAILED — {len(all_errors)} violation(s):", file=sys.stderr)
        for err in all_errors:
            print(f"  {err}", file=sys.stderr)
        return 3

    total = len(target)
    fmt_label = f" for format '{format_filter}'" if format_filter else ""
    print(f"QName validation PASSED — {total} gap(s){fmt_label} checked.", file=sys.stderr)
    return 0


def run(
    gap_ledger_path: Path,
    output_path: Path | None,
    max_items: int = 20,
    dry_run: bool = False,
    validate_qnames: bool = False,
    format_filter: str | None = None,
) -> int:
    """Main compile + emit. Returns exit code."""
    if not gap_ledger_path.exists():
        print(f"ERROR: gap-ledger not found: {gap_ledger_path}", file=sys.stderr)
        return 1

    try:
        ledger = json.loads(gap_ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot parse gap-ledger: {exc}", file=sys.stderr)
        return 1

    schema_version = ledger.get("schema_version", "1.0")
    if not isinstance(ledger.get("gaps"), list):
        print("ERROR: gap-ledger missing 'gaps' list", file=sys.stderr)
        return 1

    gaps: list[dict] = ledger["gaps"]

    # TC-ARC-010: QName validation mode — validate and exit without emitting work items.
    if validate_qnames:
        return _run_validate_qnames(gaps, format_filter)

    open_gaps = [g for g in gaps if g.get("status") not in _SKIP_STATUSES]
    if format_filter:
        open_gaps = [g for g in open_gaps
                     if g.get("format", "").lower() == format_filter.lower()]

    items, dedup_items = compile_gaps(open_gaps, max_items=max_items)

    output = {
        "items": items,
        "work_selection_mode": "CAPABILITY_COMPILER",
        "stream": "mainstream",
        "compiler_run_id": datetime.now(timezone.utc).isoformat(),
        "gap_ledger_version": schema_version,
        "total_input_gaps": len(gaps),
        "open_gaps_processed": len(open_gaps),
        "deduplicated_items": dedup_items,
    }

    output_json = json.dumps(output, indent=2, ensure_ascii=False)

    if dry_run:
        print(output_json)
        return 0

    if output_path is None:
        print("ERROR: --output required unless --dry-run", file=sys.stderr)
        return 2

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json + "\n", encoding="utf-8")
        print(f"Wrote {len(items)} work items to {output_path}", file=sys.stderr)
    except OSError as exc:
        print(f"ERROR: cannot write output: {exc}", file=sys.stderr)
        return 2

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile gap-ledger.json into next-work-items.json"
    )
    parser.add_argument(
        "--gap-ledger",
        type=Path,
        default=Path("reports/capability-layer/gap-ledger.json"),
        help="Path to gap-ledger.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for next-work-items.json",
    )
    parser.add_argument("--max-items", type=int, default=20, help="Max work items to emit")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout, no file write")
    parser.add_argument(
        "--validate-qnames",
        action="store_true",
        help="Validate QName authority for all gaps; exit 3 on violation. No work items emitted.",
    )
    parser.add_argument(
        "--format",
        dest="format_filter",
        default=None,
        help="Filter gaps by format (e.g. --format fods). Works with --validate-qnames.",
    )
    args = parser.parse_args()

    sys.exit(run(
        args.gap_ledger,
        args.output,
        args.max_items,
        args.dry_run,
        validate_qnames=args.validate_qnames,
        format_filter=args.format_filter,
    ))


if __name__ == "__main__":
    main()
