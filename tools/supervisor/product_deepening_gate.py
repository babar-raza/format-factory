"""product_deepening_gate.py — Per-format product deepening readiness gate.

Reads registry/product-deepening-ledger.yaml and evaluates per-format readiness.
Importable by check_continuation.py and autonomous_cycle.py.

CLI:
    python tools/supervisor/product_deepening_gate.py --dry-run [--repo-root PATH]
    python tools/supervisor/product_deepening_gate.py --check FODS [--repo-root PATH]

Exit codes (CLI only):
    0 — all selected formats pass
    1 — at least one format blocked
    2 — ledger missing (bootstrap tolerance)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_LEDGER = _REPO_ROOT / "registry" / "product-deepening-ledger.yaml"


def load_ledger(ledger_path: Path | None = None) -> dict[str, dict]:
    """Load ledger. Returns dict keyed by format name (lowercase). Returns {} if missing."""
    p = ledger_path or _DEFAULT_LEDGER
    if not p.exists():
        return {}
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, list):
        return {}
    result: dict[str, dict] = {}
    for entry in data:
        if isinstance(entry, dict) and "format" in entry:
            result[entry["format"].lower()] = entry
    return result


def _all_fail_result(format_name: str, reason: str) -> dict:
    return {
        "format": format_name.lower(),
        "allowed": False,
        "reason": reason,
        "qname_gate": "FAIL",
        "src_layout_gate": "FAIL",
        "spec_mapping_gate": "FAIL",
        "sal_gate": "FAIL",
        "forbidden_bucket_gate": "FAIL",
        "taskcard_gate": "FAIL",
        "evidence_gate": "FAIL",
        "ledger_entry": None,
    }


def check_product_readiness(format_name: str, ledger_path: Path | None = None) -> dict:
    """Check a single format's product deepening readiness."""
    ledger = load_ledger(ledger_path)
    if not ledger:
        return _all_fail_result(format_name, "ledger_missing")

    fmt = format_name.lower()
    entry = ledger.get(fmt)
    if entry is None:
        return _all_fail_result(format_name, "no_ledger_entry")

    qname_status = entry.get("qname_compliance_status", "unknown")
    src_layout = entry.get("src_layout_status", "unknown")
    spec_mapping = entry.get("spec_hierarchy_mapping", "missing")
    sal = entry.get("sal_fact_linkage", "unknown")
    forbidden = entry.get("forbidden_bucket_scan_status", "unknown")
    last_verified = entry.get("last_verified_at", "")

    # qname gate
    if qname_status in ("verified", "stable"):
        qname_gate = "PASS"
    elif qname_status == "implementing":
        qname_gate = "PASS"
    else:
        qname_gate = "FAIL"

    # src_layout gate
    if src_layout == "compliant":
        src_layout_gate = "PASS"
    elif src_layout in ("oversized", "mixed_model"):
        src_layout_gate = "FAIL"
    else:
        src_layout_gate = "WARN"

    # spec_mapping gate
    if spec_mapping in ("present", "partial"):
        spec_mapping_gate = "PASS"
    else:
        spec_mapping_gate = "FAIL"

    # sal gate
    if sal == "present":
        sal_gate = "PASS"
    elif sal == "bootstrap_tolerance":
        sal_gate = "WARN"
    else:
        sal_gate = "FAIL"

    # forbidden_bucket gate
    if forbidden == "clean":
        forbidden_bucket_gate = "PASS"
    elif forbidden == "violations_present":
        forbidden_bucket_gate = "FAIL"
    else:
        forbidden_bucket_gate = "WARN"

    # taskcard gate — always PASS (informational)
    taskcard_gate = "PASS"

    # evidence gate
    evidence_gate = "PASS" if last_verified else "WARN"

    # allowed: True ONLY if all critical gates PASS
    # qname must be verified (not just implementing) for continuation_allowed
    allowed = (
        qname_status in ("verified", "stable")
        and src_layout_gate == "PASS"
        and sal_gate == "PASS"
        and forbidden_bucket_gate == "PASS"
    )

    reasons = []
    if qname_status not in ("verified", "stable"):
        reasons.append(f"qname={qname_status}")
    if src_layout_gate != "PASS":
        reasons.append(f"src_layout={src_layout}")
    if sal_gate != "PASS":
        reasons.append(f"sal={sal}")
    if forbidden_bucket_gate != "PASS":
        reasons.append(f"forbidden={forbidden}")

    reason = "all_gates_pass" if allowed else "; ".join(reasons) if reasons else "blocked"

    return {
        "format": fmt,
        "allowed": allowed,
        "reason": reason,
        "qname_gate": qname_gate,
        "src_layout_gate": src_layout_gate,
        "spec_mapping_gate": spec_mapping_gate,
        "sal_gate": sal_gate,
        "forbidden_bucket_gate": forbidden_bucket_gate,
        "taskcard_gate": taskcard_gate,
        "evidence_gate": evidence_gate,
        "ledger_entry": entry,
    }


def check_formats_in_gaps(selected_gaps: list, ledger_path: Path | None = None) -> list:
    """Given list of gap dicts, returns readiness results — one per unique format."""
    if not selected_gaps:
        return []
    seen: set[str] = set()
    results: list[dict] = []
    for gap in selected_gaps:
        fmt = ""
        if isinstance(gap, dict):
            fmt = gap.get("format", "").lower()
        if not fmt or fmt in seen:
            continue
        seen.add(fmt)
        results.append(check_product_readiness(fmt, ledger_path))
    return results


def emit_continuation_signal_gates(selected_gaps: list, ledger_path: Path | None = None) -> dict:
    """Returns the product_deepening_gate_results block for supervisor continuation signal."""
    results = check_formats_in_gaps(selected_gaps, ledger_path)
    blocked = [r["format"] for r in results if not r.get("allowed")]
    return {
        "evaluated_formats": [r["format"] for r in results],
        "all_allowed": len(blocked) == 0 and len(results) >= 0,
        "blocked_formats": blocked,
        "gate_results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Product deepening readiness gate")
    parser.add_argument("--dry-run", action="store_true", help="Show readiness table for all formats")
    parser.add_argument("--check", type=str, metavar="FORMAT", help="Check a single format")
    parser.add_argument("--repo-root", type=str, default=None, help="Repository root path")
    args = parser.parse_args()

    ledger_path = None
    if args.repo_root:
        ledger_path = Path(args.repo_root) / "registry" / "product-deepening-ledger.yaml"

    if args.check:
        result = check_product_readiness(args.check, ledger_path)
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0 if result["allowed"] else 1)

    if args.dry_run:
        ledger = load_ledger(ledger_path)
        if not ledger:
            print("ERROR: Ledger not found or empty", file=sys.stderr)
            sys.exit(2)

        # Print header
        print(f"{'Format':<12} {'QName':<14} {'SrcLayout':<12} {'SpecMap':<10} "
              f"{'SAL':<10} {'Forbidden':<12} {'Allowed':<8} {'Next Action'}")
        print("-" * 100)

        any_blocked = False
        for fmt in sorted(ledger.keys()):
            r = check_product_readiness(fmt, ledger_path)
            entry = ledger[fmt]
            next_action = entry.get("next_required_action", "")[:30]
            allowed_str = "YES" if r["allowed"] else "NO"
            if not r["allowed"]:
                any_blocked = True
            print(f"{fmt:<12} {r['qname_gate']:<14} {r['src_layout_gate']:<12} "
                  f"{r['spec_mapping_gate']:<10} {r['sal_gate']:<10} "
                  f"{r['forbidden_bucket_gate']:<12} {allowed_str:<8} {next_action}")

        sys.exit(1 if any_blocked else 0)

    parser.print_help()


if __name__ == "__main__":
    main()
