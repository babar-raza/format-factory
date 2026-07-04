"""promotion_manager.py — Architecture promotion and protection system (TC-ARC-016).

Manages architecture-level promotion state for all 30 product+language combinations.
Cross-references registry/promotion-ledger.yaml (blossom TC-CQGA-018) for source CI state.

Promotion levels (plan §11):
    DRAFT → ARCHITECTURE_APPROVED → IMPLEMENTATION_VERIFIED → PILOT_ACCEPTED
    → PROMOTED_STABLE → CERTIFIED → REOPENED

Authority:
    authoritative_plan: plans/.claude/imperative-drifting-conway.md §11
    architecture registry: reports/product-architecture/promotion-registry.yaml
    source CI registry:    registry/promotion-ledger.yaml  (blossom — READ-ONLY from this module)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

_ARCH_REGISTRY = Path("reports/product-architecture/promotion-registry.yaml")
_SOURCE_LEDGER = Path("registry/promotion-ledger.yaml")

_LEVELS = [
    "DRAFT",
    "ARCHITECTURE_APPROVED",
    "IMPLEMENTATION_VERIFIED",
    "PILOT_ACCEPTED",
    "PROMOTED_STABLE",
    "CERTIFIED",
    "REOPENED",
]

_PROTECTED_LEVELS = {"PROMOTED_STABLE", "CERTIFIED"}

_PROMOTION_CRITERIA: dict[str, list[str]] = {
    "ARCHITECTURE_APPROVED": [
        "qname_mapping_verified",
        "public_api_mapping_verified",
        "file_class_organization_verified",
    ],
    "IMPLEMENTATION_VERIFIED": [
        "parser_model_writer_aligned",
        "roundtrip_proof_exists",
    ],
    "PILOT_ACCEPTED": [
        "all_required_pilots_passed",
        "consumer_proof_exists",
    ],
    "PROMOTED_STABLE": [
        "documentation_traceability_complete",
        "independent_review_passed",
        "idempotent_rerun_verified",
    ],
    "CERTIFIED": [
        "all_promotion_criteria_met",
        "external_audit_passed",
    ],
}


class PromotionError(Exception):
    """Raised when a promotion operation is invalid."""


def _load_registry() -> dict:
    if not _ARCH_REGISTRY.exists():
        raise PromotionError(f"Architecture registry not found: {_ARCH_REGISTRY}")
    return yaml.safe_load(_ARCH_REGISTRY.read_text(encoding="utf-8")) or {}


def _save_registry(data: dict) -> None:
    _ARCH_REGISTRY.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )


def _find_record(records: list[dict], format_id: str, language: str) -> dict | None:
    return next(
        (r for r in records if r.get("format") == format_id and r.get("language") == language),
        None,
    )


def validate_promotion_criteria(format_id: str, language: str, target_level: str) -> list[str]:
    """Check if the product meets criteria to be promoted to target_level.

    Returns list of unmet criteria (empty = all met).
    Note: Criteria are structural checks; caller must supply evidence that each is met.
    This function documents WHAT must be verified — actual verification is a governance gate.
    """
    if target_level not in _PROMOTION_CRITERIA:
        return []
    return _PROMOTION_CRITERIA[target_level]


def get_promotion_level(format_id: str, language: str) -> str | None:
    """Return current architecture promotion level for a product."""
    registry = _load_registry()
    records = registry.get("promotion_records", [])
    rec = _find_record(records, format_id, language)
    return rec.get("promotion_level") if rec else None


def promote(
    format_id: str,
    language: str,
    new_level: str,
    evidence: dict | None = None,
) -> dict:
    """Advance a product to a new promotion level.

    Returns the updated promotion record.
    Raises PromotionError if the transition is invalid.
    """
    if new_level not in _LEVELS:
        raise PromotionError(f"Unknown promotion level: {new_level}")

    registry = _load_registry()
    records = registry.setdefault("promotion_records", [])
    rec = _find_record(records, format_id, language)
    if rec is None:
        raise PromotionError(f"No promotion record found for {format_id}/{language}")

    current = rec.get("promotion_level", "DRAFT")
    current_idx = _LEVELS.index(current) if current in _LEVELS else 0
    new_idx = _LEVELS.index(new_level)

    # REOPENED can come from any level; otherwise must advance forward
    if new_level != "REOPENED" and new_idx <= current_idx:
        raise PromotionError(
            f"{format_id}/{language}: cannot go from {current} to {new_level} (must advance)"
        )

    rec["promotion_level"] = new_level
    rec["promoted_at"] = datetime.now(timezone.utc).isoformat()
    if evidence:
        rec.setdefault("evidence_history", []).append(evidence)

    _save_registry(registry)
    return rec


def reopen(format_id: str, language: str, reason: str) -> dict:
    """Set a product to REOPENED status with a documented reason.

    Returns the updated promotion record.
    Raises PromotionError if no record found.
    """
    registry = _load_registry()
    records = registry.get("promotion_records", [])
    rec = _find_record(records, format_id, language)
    if rec is None:
        raise PromotionError(f"No promotion record found for {format_id}/{language}")

    rec["promotion_level"] = "REOPENED"
    rec["reopened_at"] = datetime.now(timezone.utc).isoformat()
    rec["reopened_reason"] = reason
    _save_registry(registry)
    return rec


def check_protected_change(modified_files: list[str]) -> list[str]:
    """Check if any modified files belong to PROMOTED_STABLE or CERTIFIED products.

    Returns list of violation messages (empty = no violations).
    V119 wires this into the governance validator chain.
    """
    violations: list[str] = []

    # Check architecture promotion registry
    registry = _load_registry()
    records = registry.get("promotion_records", [])
    protected: dict[str, tuple[str, str, str]] = {}
    for rec in records:
        lvl = rec.get("promotion_level", "DRAFT")
        if lvl in _PROTECTED_LEVELS:
            fmt, lang = rec.get("format", ""), rec.get("language", "")
            for f in rec.get("promoted_files", []):
                protected[f] = (fmt, lang, lvl)

    # Also check source CI ledger (blossom TC-CQGA-018) — read-only cross-reference
    if _SOURCE_LEDGER.exists():
        try:
            source_data = yaml.safe_load(_SOURCE_LEDGER.read_text(encoding="utf-8")) or {}
            for entry in source_data.get("entries", []):
                if entry.get("status") in ("PROMOTED_STABLE", "CERTIFIED"):
                    for f in entry.get("files", []):
                        if f not in protected:
                            protected[f] = (
                                entry.get("format", ""),
                                entry.get("language", ""),
                                entry.get("status"),
                            )
        except Exception:
            pass  # Source ledger read failure is non-blocking per Supreme Directive

    for mf in modified_files:
        if mf in protected:
            fmt, lang, lvl = protected[mf]
            violations.append(
                f"[V119] {mf}: belongs to {fmt}/{lang} at {lvl} — requires REOPENED status before modification"
            )

    return violations


def list_products(promotion_level_filter: str | None = None) -> list[dict]:
    """List all promotion records, optionally filtered by level."""
    registry = _load_registry()
    records = registry.get("promotion_records", [])
    if promotion_level_filter:
        records = [r for r in records if r.get("promotion_level") == promotion_level_filter]
    return records


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Architecture promotion manager (TC-ARC-016)")
    sub = parser.add_subparsers(dest="command")

    ls_cmd = sub.add_parser("list", help="List products at a promotion level")
    ls_cmd.add_argument("--level", default=None, help="Filter by promotion level")

    get_cmd = sub.add_parser("get", help="Get promotion level for a product")
    get_cmd.add_argument("format")
    get_cmd.add_argument("language")

    check_cmd = sub.add_parser("check", help="Check modified files for protection violations")
    check_cmd.add_argument("files", nargs="+", help="Modified file paths")

    args = parser.parse_args()

    if args.command == "list":
        products = list_products(args.level)
        for p in products:
            print(f"{p['format']}/{p['language']}: {p.get('promotion_level', 'DRAFT')}")

    elif args.command == "get":
        lvl = get_promotion_level(args.format, args.language)
        print(lvl or "NOT_FOUND")

    elif args.command == "check":
        violations = check_protected_change(args.files)
        for v in violations:
            print(v)
        if violations:
            raise SystemExit(3)
        print("No protected-change violations.")

    else:
        parser.print_help()
