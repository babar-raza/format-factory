"""
prior_closure_auditor.py — Prior sprint closure audit scanner (TC-FG-008).

Scans evidence declarations from prior sprints to identify high-risk
false-green patterns: items graded ACCEPTED_VERIFIED where proof level
was file-existence only (no AST assertion analysis was performed).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

_SUPERVISOR = Path(__file__).resolve().parent
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))


def _load_declaration(decl_path: Path) -> Optional[dict]:
    """Load YAML or JSON evidence declaration. Returns None on failure."""
    try:
        if decl_path.suffix in (".yaml", ".yml"):
            try:
                import yaml  # type: ignore[import]
                return yaml.safe_load(decl_path.read_text(encoding="utf-8", errors="replace"))
            except ImportError:
                # Fallback: minimal YAML parsing for key: value structures
                text = decl_path.read_text(encoding="utf-8", errors="replace")
                result: dict = {}
                for line in text.splitlines():
                    if ":" in line and not line.strip().startswith("#"):
                        k, _, v = line.partition(":")
                        k = k.strip()
                        v = v.strip()
                        if k and v:
                            result[k] = v
                return result
        elif decl_path.suffix == ".json":
            return json.loads(decl_path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        pass
    return None


def _assess_item_risk(item: dict, high_risk_item_types: list) -> list:
    """Return list of risk signal strings for a completed work item."""
    from proof_adequacy_contract import (
        assess_proof_level,
        infer_default_contract,
        proof_sufficient_for_closure,
    )

    signals = []
    item_type = item.get("item_type", "")
    if item_type not in high_risk_item_types:
        return signals

    status = item.get("status", "")
    if status not in ("completed", "COMPLETED", "done", "DONE", ""):
        return signals

    tests = item.get("tests_supporting", [])
    if not tests:
        signals.append(f"NO_TESTS_DECLARED:{item.get('item_id', '?')}")
        return signals

    try:
        contract = infer_default_contract(item)
        for t in tests:
            t_path = Path(t)
            if not t_path.exists():
                signals.append(f"MISSING_TEST_FILE:{t}")
                continue
            assessment = assess_proof_level(str(t_path))
            sufficient, gaps = proof_sufficient_for_closure(contract, [str(t_path)], assessment)
            if not sufficient:
                signals.append(f"PROOF_INADEQUATE:{item.get('item_id', '?')}")
                break
    except Exception as _e:
        signals.append(f"ASSESSMENT_ERROR:{_e}")

    return signals


def audit_prior_closures(
    evidence_dir: str = ".local/evidences/",
    lookback_runs: int = 20,
    high_risk_item_types: Optional[list] = None,
) -> list:
    """
    Scan last N evidence declarations for high-risk false-green patterns.

    Returns list of closure audit records, one per declaration found.
    """
    if high_risk_item_types is None:
        high_risk_item_types = ["PRODUCT_TEST", "PRODUCT_SOURCE"]

    evidence_path = Path(evidence_dir)
    if not evidence_path.exists():
        return []

    # Find all evidence-declaration.yaml files, sorted by mtime (newest first)
    declarations = sorted(
        list(evidence_path.glob("**/evidence-declaration.yaml"))
        + list(evidence_path.glob("**/evidence-declaration.json")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:lookback_runs]

    results = []
    for decl_path in declarations:
        decl = _load_declaration(decl_path)
        if not decl:
            results.append({
                "mission_id": str(decl_path),
                "error": "failed to load declaration",
                "risk_signals": [],
                "proof_adequacy": "UNKNOWN",
                "disposition": "LOAD_ERROR",
            })
            continue

        risk_signals = []
        try:
            for item in decl.get("planned_work_items", []):
                item_signals = _assess_item_risk(item, high_risk_item_types)
                risk_signals.extend(item_signals)
        except Exception as _e:
            risk_signals.append(f"SCAN_ERROR:{_e}")

        results.append({
            "mission_id": decl.get("sprint_id", decl.get("run_id", str(decl_path.parent.name))),
            "closure_revision": decl.get("git_head_end", "unknown"),
            "risk_signals": risk_signals,
            "proof_adequacy": "ADEQUATE" if not risk_signals else "AT_RISK",
            "reopened": False,
            "gap_ids": [],
            "disposition": "REVIEWED",
            "declaration_path": str(decl_path),
        })

    return results


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Prior closure audit scanner (TC-FG-008)")
    parser.add_argument("--evidence-dir", default=".local/evidences/",
                        help="Directory containing evidence declarations")
    parser.add_argument("--lookback", type=int, default=20,
                        help="Number of prior declarations to scan")
    parser.add_argument("--output", default=None,
                        help="Output YAML path (default: stdout JSON)")
    args = parser.parse_args()

    results = audit_prior_closures(
        evidence_dir=args.evidence_dir,
        lookback_runs=args.lookback,
    )

    if args.output:
        try:
            import yaml  # type: ignore[import]
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(
                yaml.dump({"audit_results": results}, default_flow_style=False, sort_keys=False),
                encoding="utf-8",
            )
            print(f"Written: {args.output}")
        except Exception as e:
            print(f"ERROR writing output: {e}", file=sys.stderr)
            return 1
    else:
        print(json.dumps(results, indent=2))

    at_risk = sum(1 for r in results if r.get("proof_adequacy") == "AT_RISK")
    print(f"\nAudit complete: {len(results)} declarations scanned, {at_risk} AT_RISK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
