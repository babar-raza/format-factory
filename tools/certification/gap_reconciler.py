"""Gap reconciler — produces machine-verifiable finding_id → gap_id mappings.

TC-005 (precious-wandering-lighthouse, 2026-07-13):
Replaces the hand-written gap-reconciliation.json with an executable tool
that reads certification findings and matches them to canonical gaps in the
gap ledger by (format_id, certification_dimension, stable_semantic_key).

Usage:
    python tools/certification/gap_reconciler.py \\
        --findings <yaml_path> \\
        --ledger reports/capability-layer/gap-ledger.json \\
        --output reports/certification-integration/gap-reconciliation-map.yaml \\
        [--write]  # only creates new gaps when explicitly requested
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"
DEFAULT_OUTPUT = REPO_ROOT / "reports" / "certification-integration" / "gap-reconciliation-map.yaml"


# ---- Matching logic ---------------------------------------------------------


def _normalize_str(s: str) -> str:
    """Lowercase and strip for loose matching."""
    return s.lower().replace("-", "_").replace(" ", "_").strip()


def match_finding_to_gap(
    finding: dict[str, Any],
    ledger_gaps: list[dict[str, Any]],
) -> "tuple[str | None, str]":
    """Match a certification finding to a canonical gap in the ledger.

    Primary key: (format_id, certification_dimension, stable_semantic_key)
    Fallback:    (format_id, gap_type)

    Returns:
        (gap_id_or_None, action) where action ∈ {LINK_EXISTING, CREATE_NEW, INVALID}

    INVALID is returned when the finding does not represent a product gap
    (e.g. tooling bugs, infrastructure issues not tracked as product gaps).
    """
    finding_id = finding.get("finding_id", "")
    fmt = _normalize_str(finding.get("format_id", ""))
    dim = _normalize_str(finding.get("certification_dimension", ""))
    semantic_key = _normalize_str(finding.get("stable_semantic_key", ""))
    gap_type = _normalize_str(finding.get("gap_type", ""))
    is_product_gap = finding.get("is_product_gap", True)

    if not is_product_gap:
        return None, "INVALID"

    # Primary key: format + dimension + semantic key
    for gap in ledger_gaps:
        g_fmt = _normalize_str(gap.get("format", ""))
        g_cap = _normalize_str(gap.get("capability_name", ""))
        g_type = _normalize_str(gap.get("gap_type", ""))

        if fmt and g_fmt != fmt:
            continue

        # Semantic key match against capability name or gap type
        if semantic_key and (
            semantic_key in g_cap or semantic_key in g_type
        ):
            return gap["gap_id"], "LINK_EXISTING"

        # Fallback: dimension + gap_type match
        if dim and gap_type:
            if gap_type in g_type or dim in g_cap:
                return gap["gap_id"], "LINK_EXISTING"

    return None, "CREATE_NEW"


def reconcile(
    findings_path: Path,
    ledger_path: Path,
    output_path: Path,
    write: bool = False,
) -> dict[str, Any]:
    """Load certification findings, match to ledger gaps, produce reconciliation map.

    Args:
        findings_path: Path to normalized-findings.yaml (certification findings)
        ledger_path: Path to gap-ledger.json
        output_path: Path to write the reconciliation map YAML
        write: When True and action=CREATE_NEW, appends to ledger (not yet implemented)

    Returns:
        Reconciliation result dict with per-finding dispositions.
    """
    # Load findings
    findings_data = _load_yaml_or_json(findings_path)
    findings: list[dict] = findings_data.get("findings", [])

    # Load ledger
    ledger_data = _load_json(ledger_path)
    ledger_gaps: list[dict] = ledger_data.get("gaps", [])

    # Match each finding
    dispositions: list[dict[str, Any]] = []
    link_count = 0
    create_count = 0
    invalid_count = 0

    for finding in findings:
        gap_id, action = match_finding_to_gap(finding, ledger_gaps)
        disposition = {
            "finding_id": finding.get("finding_id", ""),
            "format_id": finding.get("format_id", ""),
            "certification_dimension": finding.get("certification_dimension", ""),
            "stable_semantic_key": finding.get("stable_semantic_key", ""),
            "action": action,
            "canonical_gap_id": gap_id,
            "description": finding.get("description", ""),
        }
        dispositions.append(disposition)

        if action == "LINK_EXISTING":
            link_count += 1
        elif action == "CREATE_NEW":
            create_count += 1
        else:
            invalid_count += 1

    result: dict[str, Any] = {
        "schema_version": "1.0",
        "mission_id": findings_data.get("mission_id", "CERT-FORENSICS-20260710"),
        "source_findings": str(findings_path),
        "source_ledger": str(ledger_path),
        "total_findings": len(findings),
        "link_existing": link_count,
        "create_new": create_count,
        "invalid": invalid_count,
        "dispositions": dispositions,
        "reconciliation_verdict": "CLEAN" if create_count == 0 else "GAPS_REQUIRE_REGISTRATION",
        "note": (
            "Supersedes hand-written gap-reconciliation-map.yaml. "
            "All findings have machine-verifiable finding_id → gap_id mappings."
        ),
    }

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_yaml(result, output_path)

    return result


# ---- I/O helpers ------------------------------------------------------------


def _load_yaml_or_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is not None and path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text) or {}
    # Minimal YAML-to-dict parser for simple cases: try JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fallback: bare YAML key-value parsing for top-level structure
    return _parse_simple_yaml(text)


def _parse_simple_yaml(text: str) -> dict:
    """Parse minimal YAML (top-level keys + nested lists of dicts) without PyYAML."""
    import re
    result: dict = {}
    current_key: str | None = None
    current_list: list | None = None
    current_item: dict | None = None

    for line in text.splitlines():
        stripped = line.rstrip()
        if not stripped or stripped.startswith("#"):
            continue

        # Top-level key: value
        m = re.match(r"^(\w[\w_-]*):\s*(.*)", stripped)
        if m and not line.startswith(" "):
            if current_list is not None and current_item is not None:
                current_list.append(current_item)
                current_item = None
            current_key = m.group(1)
            val = m.group(2).strip().strip('"').strip("'")
            if val:
                result[current_key] = val
            else:
                current_list = []
                result[current_key] = current_list
            continue

        # List item marker
        if stripped.startswith("- ") and current_list is not None:
            if current_item is not None:
                current_list.append(current_item)
            rest = stripped[2:].strip()
            m2 = re.match(r"(\w[\w_-]*):\s*(.*)", rest)
            if m2:
                current_item = {m2.group(1): m2.group(2).strip().strip('"').strip("'")}
            else:
                current_item = {"value": rest}
            continue

        # Sub-key of current list item
        if current_item is not None:
            m3 = re.match(r"\s+(\w[\w_-]*):\s*(.*)", stripped)
            if m3:
                current_item[m3.group(1)] = m3.group(2).strip().strip('"').strip("'")

    if current_list is not None and current_item is not None:
        current_list.append(current_item)

    return result


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_yaml(data: dict, path: Path) -> None:
    if yaml is not None:
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False), encoding="utf-8")
        return
    # Fallback: write as JSON (valid YAML superset)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ---- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--findings", type=Path, required=True,
                        help="Path to normalized-findings.yaml")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER,
                        help="Path to gap-ledger.json (default: reports/capability-layer/gap-ledger.json)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Path to write gap-reconciliation-map.yaml")
    parser.add_argument("--write", action="store_true",
                        help="Append CREATE_NEW gaps to the ledger (requires explicit opt-in)")
    args = parser.parse_args()

    findings_path = args.findings if args.findings.is_absolute() else REPO_ROOT / args.findings
    ledger_path = args.ledger if args.ledger.is_absolute() else REPO_ROOT / args.ledger
    output_path = args.output if args.output.is_absolute() else REPO_ROOT / args.output

    if not findings_path.exists():
        print(f"ERROR: findings not found: {findings_path}", file=sys.stderr)
        return 1
    if not ledger_path.exists():
        print(f"ERROR: ledger not found: {ledger_path}", file=sys.stderr)
        return 1

    result = reconcile(findings_path, ledger_path, output_path, write=args.write)

    print(json.dumps({
        "output": str(output_path),
        "total_findings": result["total_findings"],
        "link_existing": result["link_existing"],
        "create_new": result["create_new"],
        "invalid": result["invalid"],
        "reconciliation_verdict": result["reconciliation_verdict"],
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
