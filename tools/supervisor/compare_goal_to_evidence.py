"""
compare_goal_to_evidence.py — Format Factory Local Supervisor Control Plane
Detects contradictions between sprint goals/contracts and evidence facts.

Severity levels:
  CRITICAL — stops autonomous loop; requires human review
  WARNING  — logged and included in report; autonomous continuation allowed
  INFO     — advisory only

Exit codes:
  0 — review complete (contradictions may be present — check output)
  9 — unexpected error

Usage:
  python tools/supervisor/compare_goal_to_evidence.py --review reports/supervisor/evidence-review.json
  python tools/supervisor/compare_goal_to_evidence.py --review reports/supervisor/evidence-review.json --output-dir reports/supervisor
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


PENDING_MARKERS = [
    "PENDING",
    "TO BE FILLED",
    "PLACEHOLDER",
    "TBD",
]


def load_review(review_path: Path) -> dict:
    """Load evidence review JSON."""
    return json.loads(review_path.read_text(encoding="utf-8"))


def find_matching_contract(repo_root: Path, sprint_id: str = "") -> Path | None:
    """Find the contract matching the evidence bundle's sprint_id.

    Prefers a contract whose filename matches the run_number from sprint_id
    (e.g. sprint_id containing 'R80' → looks for 'r80-*.yaml'). Falls back
    to the highest-numbered local contract rather than most-recently-modified.
    """
    contracts_dir = repo_root / "tools" / "evidence" / "contracts"
    if not contracts_dir.exists():
        return None
    contracts = list(contracts_dir.glob("*.yaml"))
    if not contracts:
        return None

    if sprint_id and sprint_id != "unknown":
        import re as _re
        rnum_m = _re.search(r"\br(\d+)\b", sprint_id, _re.IGNORECASE)
        run_token = rnum_m.group(0).lower() if rnum_m else ""
        if run_token:
            for c in contracts:
                if c.stem.lower().startswith(run_token + "-"):
                    return c

    # Fall back: highest run-number contract
    import re as _re

    def _run_num(p: Path) -> int:
        m = _re.match(r"r(\d+)-", p.stem)
        return int(m.group(1)) if m else 0

    numbered = [c for c in contracts if _run_num(c) > 0]
    if numbered:
        return max(numbered, key=_run_num)
    return max(contracts, key=lambda p: p.stat().st_mtime)


def read_contract(contract_path: Path) -> dict:
    """Read contract YAML — minimal parsing without external dependencies."""
    try:
        import yaml
        return yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    except ImportError:
        pass
    # Fallback: basic key:value parsing
    result = {}
    for line in contract_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            k, _, v = line.partition(":")
            result[k.strip()] = v.strip()
    return result


def check_tests_failed(review: dict, contract: dict, contradictions: list) -> None:
    """Check if tests failed when contract requires pass."""
    fail_count = review.get("facts", {}).get("fail_count", 0)
    if fail_count > 0:
        contradictions.append({
            "severity": "CRITICAL",
            "description": f"Tests failed: {fail_count} failures detected in evidence bundle",
            "detail": f"fail_count={fail_count}; all tests must pass per Format Factory policy",
        })


def check_pending_markers(review: dict, contradictions: list) -> None:
    """Check for PENDING markers in final state."""
    pending_count = review.get("facts", {}).get("pending_marker_count", 0)
    verdict_text = review.get("facts", {}).get("final_verdict_text", "")

    # Count non-delegation markers (delegation labels are allowed)
    real_pending = 0
    for line in verdict_text.splitlines():
        if "PENDING" in line and "delegated_to_" not in line.lower():
            real_pending += 1

    if real_pending > 0:
        contradictions.append({
            "severity": "CRITICAL",
            "description": f"PENDING markers found in final-verdict.md: {real_pending} occurrences",
            "detail": "PENDING tokens indicate incomplete sprint state — not RC-ready",
        })


def check_missing_final_verdict(review: dict, contradictions: list) -> None:
    """Check if final verdict is absent."""
    verdict_text = review.get("facts", {}).get("final_verdict_text", "")
    if not verdict_text:
        contradictions.append({
            "severity": "CRITICAL",
            "description": "No final-verdict.md found in evidence bundle",
            "detail": "Evidence bundles must contain a final-verdict.md",
        })


def check_sprint_id_mismatch(review: dict, contract: dict, contradictions: list) -> None:
    """Check sprint_id consistency."""
    review_sprint_id = review.get("sprint_id", "unknown")
    contract_sprint_id = contract.get("sprint_id", "")

    if not contract_sprint_id:
        return  # No contract sprint_id to compare

    if review_sprint_id == "unknown":
        contradictions.append({
            "severity": "WARNING",
            "description": "Sprint ID not found in evidence bundle",
            "detail": "Cannot verify sprint identity match with contract",
        })
        return

    if review_sprint_id != contract_sprint_id and contract_sprint_id:
        contradictions.append({
            "severity": "WARNING",
            "description": f"Sprint ID mismatch: evidence='{review_sprint_id}' vs contract='{contract_sprint_id}'",
            "detail": "Evidence bundle may be from a different sprint",
        })


def check_stale_sha(review: dict, contradictions: list) -> None:
    """Check for stale SHA patterns."""
    verdict_text = review.get("facts", {}).get("final_verdict_text", "")
    stale_patterns = [
        r"PASS_2_SHA.*?:\s*PENDING",
        r"SIDECAR_SHA.*?:\s*PENDING",
        r"DELIVERY_PACKAGE_SHA.*?:\s*PENDING",
    ]
    for pattern in stale_patterns:
        if re.search(pattern, verdict_text, re.IGNORECASE):
            contradictions.append({
                "severity": "CRITICAL",
                "description": f"Stale SHA pattern found: {pattern}",
                "detail": "SHA fields must be filled before bundle is finalized",
            })


def check_gate_overclaim(review: dict, contradictions: list) -> None:
    """Check if gates are claimed closed without evidence."""
    verdict_text = review.get("facts", {}).get("final_verdict_text", "")
    gate_states = review.get("facts", {}).get("gate_states", {})

    # Look for patterns like "gate_11: closed" without supporting evidence
    # Gate 11 (G11-G) requires human approval and cannot be self-approved
    g11_claimed_closed = (
        gate_states.get("gate_11", "").lower() in ["closed", "approved", "pass", "complete"]
        or "G11-G: CLOSED" in verdict_text
        or "gate_11_approved" in verdict_text.lower()
    )
    if g11_claimed_closed:
        contradictions.append({
            "severity": "CRITICAL",
            "description": "Gate 11 (G11-G) appears to be claimed closed — this requires human approval from Babar Raza",
            "detail": "No autonomous process can approve Gate 11. Check if this is a valid human-approved state.",
        })


def check_no_bundle(review: dict, contradictions: list) -> None:
    """Check if no bundle was found."""
    if review.get("verdict") in ["BLOCKED_NO_BUNDLE", "BLOCKED_MALFORMED_ZIP"]:
        contradictions.append({
            "severity": "CRITICAL",
            "description": f"Evidence bundle issue: {review.get('verdict')}",
            "detail": review.get("error", "No additional detail"),
        })


def check_bundle_validation_fail(review: dict, contradictions: list) -> None:
    """Check if the existing validator reported BUNDLE_VALIDATION: FAIL."""
    if not review.get("validator_invoked", False):
        return
    if not review.get("bundle_validation_pass", True):
        validator_output = review.get("validator_output", "")
        # Check for specific error types
        sidecar_error = "SIDECAR_REQUIRED" in validator_output
        detail = "Existing validator (validate_evidence_bundle.py) reported BUNDLE_VALIDATION: FAIL."
        if sidecar_error:
            detail += " Sidecar proof is required but was not supplied."
        contradictions.append({
            "severity": "CRITICAL",
            "description": "BUNDLE_VALIDATION: FAIL — evidence bundle did not pass validation",
            "detail": detail,
        })


def compare(review: dict, contract: dict, repo_root: Path) -> dict:
    """Run all contradiction checks. Returns structured result.

    R102: Declaration-sourced reviews skip legacy bundle checks
    (final-verdict.md, sidecar, bundle-validation) because declaration-review
    packages don't contain those legacy artifacts.
    """
    timestamp = datetime.now().isoformat()
    contradictions = []
    is_declaration_sourced = review.get("_declaration_sourced", False)

    check_no_bundle(review, contradictions)
    # R102: Skip legacy bundle checks for declaration-sourced reviews
    if not is_declaration_sourced:
        check_missing_final_verdict(review, contradictions)
        check_bundle_validation_fail(review, contradictions)
    check_tests_failed(review, contract, contradictions)
    check_pending_markers(review, contradictions)
    check_stale_sha(review, contradictions)
    if not is_declaration_sourced:
        check_sprint_id_mismatch(review, contract, contradictions)
    check_gate_overclaim(review, contradictions)

    critical_count = sum(1 for c in contradictions if c["severity"] == "CRITICAL")
    warning_count = sum(1 for c in contradictions if c["severity"] == "WARNING")

    if not contradictions:
        overall = "CLEAN"
        autonomous_continue = True
    elif critical_count > 0:
        overall = "CRITICAL_CONTRADICTIONS"
        autonomous_continue = False
    else:
        overall = "WARNING_CONTRADICTIONS"
        autonomous_continue = True

    return {
        "sprint_id": review.get("sprint_id", "unknown"),
        "timestamp": timestamp,
        "overall": overall,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "autonomous_continue": autonomous_continue,
        "contradictions": contradictions,
    }


def write_markdown(result: dict, output_dir: Path) -> None:
    """Write contradictions.md."""
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"<!-- generated_at: {result['timestamp']} | source_sprint: {result['sprint_id']} -->",
        "# Contradiction Detection Report",
        f"Sprint ID: {result['sprint_id']}",
        f"Timestamp: {result['timestamp']}",
        f"Overall: {result['overall']}",
        f"Autonomous continue: {result['autonomous_continue']}",
        f"Critical: {result['critical_count']} | Warning: {result['warning_count']}",
        "",
    ]

    if not result["contradictions"]:
        lines.append("No contradictions detected.")
    else:
        lines.append("## Contradictions")
        for i, c in enumerate(result["contradictions"], 1):
            lines += [
                "",
                f"### [{c['severity']}] {i}. {c['description']}",
                f"Detail: {c.get('detail', '')}",
            ]

    if not result["autonomous_continue"]:
        lines += [
            "",
            "## CRITICAL: Autonomous loop stopped.",
            "CRITICAL contradictions require human review before continuing.",
        ]

    path = output_dir / "contradictions.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect contradictions between sprint goals and evidence"
    )
    parser.add_argument(
        "--review",
        type=Path,
        required=True,
        help="Path to evidence-review.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/supervisor"),
        help="Directory for output files",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    review = load_review(args.review)

    contract_path = find_matching_contract(repo_root, review.get("sprint_id", ""))
    contract = read_contract(contract_path) if contract_path else {}

    result = compare(review, contract, repo_root)

    # Write JSON
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "contradictions.json"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    # Write markdown
    write_markdown(result, output_dir)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"CONTRADICTION_CHECK: {result['overall']}")
        print(f"  Critical: {result['critical_count']}, Warning: {result['warning_count']}")
        print(f"  Autonomous continue: {result['autonomous_continue']}")
        if result["contradictions"]:
            for c in result["contradictions"]:
                print(f"  [{c['severity']}] {c['description']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
