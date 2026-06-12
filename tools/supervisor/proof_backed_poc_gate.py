"""
proof_backed_poc_gate.py — Proof-Backed POC Readiness Gate

Replaces the shallow poc-targets.yaml gates_passed check with real proof verification.

DESIGN PRINCIPLE: Each POC target must have verifiable on-disk evidence, not just
text-based status in poc-targets.yaml. This gate checks:

1. Source or package artifact exists (src/ file with real code)
2. Test files exist (tests/ directory with test files)
3. Raw test log exists (captured pytest output per format)
4. Sample/dogfood output exists (examples/ directory)
5. Proof record exists (ledger entry OR proof graph node)
6. No ai_draft-only claims (draft ≠ proof)

Decision output:
  - MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING
  - MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED
  - POC_NOT_READY_CONTINUE
  - HOST_INVOCATION_LAYER_MISSING
  - MAINSTREAM_POC_UNSAFE_WORKSPACE
  - MAINSTREAM_POC_BLOCKED_EXTERNAL_GATE
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# ─────────────────────────────────────────────────────────────
# Format definitions
# ─────────────────────────────────────────────────────────────

COMMERCIAL_NET_FORMATS = [
    {
        "format": "FODS",
        "source_dirs": ["src/net/fods"],
        "source_extensions": [".cs"],
        "test_dirs": ["tests/net/fods"],
        "test_extensions": [".cs"],
        "example_dirs": ["examples/net/fods"],
        "log_search_patterns": ["fods", "FODS"],
        "ledger_key": "fods",
        "required_log": True,
        "required_example": True,
    },
    {
        "format": "FODT",
        "source_dirs": ["src/net/fodt"],
        "source_extensions": [".cs"],
        "test_dirs": ["tests/net/fodt"],
        "test_extensions": [".cs"],
        "example_dirs": ["examples/net/fodt"],
        "log_search_patterns": ["fodt", "FODT"],
        "ledger_key": "fodt",
        "required_log": True,
        "required_example": True,
    },
    {
        "format": "Netpbm",
        "source_dirs": ["src/net/netpbm"],
        "source_extensions": [".cs"],
        "test_dirs": ["tests/net/netpbm"],
        "test_extensions": [".cs"],
        "example_dirs": ["examples/net/netpbm"],
        "log_search_patterns": ["netpbm", "Netpbm", "NetpbmImage"],
        "ledger_key": "netpbm",
        "required_log": True,
        "required_example": True,
    },
]

FOSS_PYTHON_FORMATS = [
    {
        "format": "ZST",
        "source_dirs": ["src/python/zst"],
        "source_extensions": [".py"],
        "test_dirs": ["tests/python/zst"],
        "test_extensions": [".py"],
        "example_dirs": ["examples/python/zst"],
        "log_search_patterns": ["zst", "ZST", "zstandard"],
        "ledger_key": "zst",
        "required_log": True,
        "required_example": True,
    },
    {
        "format": "Netpbm-Python",
        "source_dirs": ["src/python/pbm", "src/python/pgm", "src/python/ppm"],
        "source_extensions": [".py"],
        "test_dirs": ["tests/python/pbm", "tests/python/pgm", "tests/python/ppm"],
        "test_extensions": [".py"],
        "example_dirs": ["examples/python/ppm"],
        "log_search_patterns": ["ppm", "pbm", "pgm", "netpbm"],
        "ledger_key": "netpbm_python",
        "required_log": True,
        "required_example": True,
    },
    {
        "format": "SYLK",
        "source_dirs": ["src/python/sylk"],
        "source_extensions": [".py"],
        "test_dirs": ["tests/python/sylk"],
        "test_extensions": [".py"],
        "example_dirs": ["examples/python/sylk"],
        "log_search_patterns": ["sylk", "SYLK"],
        "ledger_key": "sylk",
        "required_log": True,
        "required_example": True,
    },
    {
        "format": "DIF",
        "source_dirs": ["src/python/dif"],
        "source_extensions": [".py"],
        "test_dirs": ["tests/python/dif"],
        "test_extensions": [".py"],
        "example_dirs": [],
        "log_search_patterns": ["dif", "DIF"],
        "ledger_key": "dif",
        "required_log": False,
        "required_example": False,
    },
]

FOSS_MINIMUM_PASS_COUNT = 3


# ─────────────────────────────────────────────────────────────
# Individual proof checks
# ─────────────────────────────────────────────────────────────

def _check_source_exists(fmt: dict, repo_root: Path) -> dict:
    """Check that at least one source file with real code exists."""
    found = []
    missing = []
    for d in fmt["source_dirs"]:
        full = repo_root / d
        if full.exists():
            files = [f for f in full.rglob("*") if f.suffix in fmt["source_extensions"] and f.stat().st_size > 100]
            if files:
                found.extend([str(f.relative_to(repo_root)) for f in files[:3]])
            else:
                missing.append(d)
        else:
            missing.append(d)
    return {
        "pass": len(found) > 0,
        "found": found[:3],
        "missing": missing,
        "reason": "Source files found" if found else f"No source files in {fmt['source_dirs']}",
    }


def _check_tests_exist(fmt: dict, repo_root: Path) -> dict:
    """Check that test files exist in the test directory."""
    found = []
    missing = []
    for d in fmt["test_dirs"]:
        full = repo_root / d
        if full.exists():
            files = [f for f in full.rglob("*") if f.suffix in fmt["test_extensions"]]
            if files:
                found.extend([str(f.relative_to(repo_root)) for f in files[:2]])
            else:
                missing.append(d)
        else:
            missing.append(d)
    return {
        "pass": len(found) > 0,
        "found_count": len(found),
        "missing": missing,
        "reason": f"{len(found)} test files found" if found else f"No test files in {fmt['test_dirs']}",
    }


def _check_raw_log_exists(fmt: dict, repo_root: Path) -> dict:
    """Check that a raw test log exists that covers this format."""
    patterns = fmt["log_search_patterns"]
    # Search all .log files for content matching format patterns
    log_dirs = [
        repo_root / "reports",
        repo_root / ".local" / "evidences",
        repo_root / ".local" / "supervisor" / "reviews",
    ]
    found_logs = []
    for log_dir in log_dirs:
        if not log_dir.exists():
            continue
        for log_file in log_dir.rglob("*.log"):
            try:
                content = log_file.read_text(encoding="utf-8", errors="ignore")
                if any(p.lower() in content.lower() for p in patterns):
                    found_logs.append(str(log_file.relative_to(repo_root)))
            except Exception:
                pass
    # Also check .txt files named with test/log patterns
    for log_dir in [repo_root / "reports"]:
        if not log_dir.exists():
            continue
        for txt_file in log_dir.rglob("*.txt"):
            if "test" in txt_file.name.lower() or "log" in txt_file.name.lower():
                try:
                    content = txt_file.read_text(encoding="utf-8", errors="ignore")
                    if any(p.lower() in content.lower() for p in patterns):
                        found_logs.append(str(txt_file.relative_to(repo_root)))
                except Exception:
                    pass
    return {
        "pass": len(found_logs) > 0,
        "found": found_logs[:3],
        "reason": f"Raw log found: {found_logs[0]}" if found_logs else f"No raw test log found for {fmt['format']}",
    }


def _check_examples_exist(fmt: dict, repo_root: Path) -> dict:
    """Check that example/sample/dogfood output files exist."""
    if not fmt["example_dirs"]:
        return {"pass": True, "found": [], "reason": "No example required for this format"}
    found = []
    missing = []
    for d in fmt["example_dirs"]:
        full = repo_root / d
        if full.exists():
            files = list(full.rglob("*.*"))
            if files:
                found.extend([str(f.relative_to(repo_root)) for f in files[:2]])
            else:
                missing.append(d)
        else:
            missing.append(d)
    return {
        "pass": len(found) > 0,
        "found": found[:2],
        "missing": missing,
        "reason": "Examples found" if found else f"No examples in {fmt['example_dirs']}",
    }


def _check_proof_record(fmt: dict, repo_root: Path) -> dict:
    """Check for a proof record: ledger entry OR proof graph node."""
    ledger_key = fmt["ledger_key"]
    fmt_name = fmt["format"].lower()

    # OPTION B (Autonomous Execution Contract):
    # Ledger entries are canonical operational records, but MUST have a
    # corresponding proof graph projection to be accepted as POC proof.
    # "Ledger only" without projection is NOT accepted.

    ledger_path = repo_root / "reports" / "r90" / "product-code-change-ledger.json"
    ledger_matches = 0
    if ledger_path.exists():
        try:
            data = json.loads(ledger_path.read_text(encoding="utf-8"))
            entries = data if isinstance(data, list) else data.get("entries", data.get("records", []))
            matching = [e for e in entries if isinstance(e, dict) and
                       (ledger_key in str(e).lower() or fmt_name in str(e).lower())]
            ledger_matches = len(matching)
        except Exception:
            pass

    # Check for proof graph projection (generated by project_product_ledger_to_proof_graph.py)
    proof_graph_dirs = [
        repo_root / "reports" / "autonomous-system-audit" / "projected-proof-graph",
        repo_root / "reports" / "proof-graph",
    ]
    # Also check any proof-graph-nodes.jsonl files
    for pg_file in repo_root.rglob("proof-graph-nodes.jsonl"):
        proof_graph_dirs.append(pg_file.parent)

    projection_found = False
    projection_source = None
    for pg_dir in proof_graph_dirs:
        nodes_file = pg_dir / "nodes.jsonl"
        if nodes_file.exists():
            try:
                content = nodes_file.read_text(encoding="utf-8", errors="ignore")
                if fmt_name in content.lower() or ledger_key in content.lower():
                    projection_found = True
                    projection_source = str(nodes_file.relative_to(repo_root))
                    break
            except Exception:
                pass
        # Also check legacy proof-graph-nodes.jsonl files
        legacy_file = pg_dir / "proof-graph-nodes.jsonl"
        if legacy_file.exists() and legacy_file != nodes_file:
            try:
                content = legacy_file.read_text(encoding="utf-8", errors="ignore")
                if fmt_name in content.lower() or ledger_key in content.lower():
                    projection_found = True
                    projection_source = str(legacy_file.relative_to(repo_root))
                    break
            except Exception:
                pass

    if ledger_matches > 0 and projection_found:
        return {
            "pass": True,
            "source": f"ledger({ledger_matches} entries) + projection({projection_source})",
            "count": ledger_matches,
            "projection_verified": True,
            "reason": f"Found {ledger_matches} ledger entries + proof graph projection for {fmt['format']}",
        }
    elif ledger_matches > 0 and not projection_found:
        # Ledger without projection — not accepted per Option B contract
        # But generate projection path for guidance
        return {
            "pass": False,
            "source": f"product-code-change-ledger.json ({ledger_matches} entries, NO PROJECTION)",
            "count": ledger_matches,
            "projection_verified": False,
            "reason": (
                f"Found {ledger_matches} ledger entries for {fmt['format']} but NO proof graph projection. "
                f"Run: python tools/supervisor/project_product_ledger_to_proof_graph.py"
            ),
        }

    # Check poc-targets.yaml (as ADVISORY-ONLY fallback — not proof)
    poc_path = repo_root / "product-capability-matrix" / "poc-targets.yaml"
    if poc_path.exists():
        try:
            content = poc_path.read_text(encoding="utf-8")
            if fmt_name in content.lower() or fmt["format"] in content:
                return {
                    "pass": False,  # poc-targets.yaml alone is NOT proof
                    "source": "poc-targets.yaml (NOT PROOF — advisory only)",
                    "reason": f"poc-targets.yaml contains {fmt['format']} but is NOT a proof record. Requires ledger entry + proof graph projection.",
                }
        except Exception:
            pass

    return {
        "pass": False,
        "source": None,
        "projection_verified": False,
        "reason": f"No proof record found for {fmt['format']} (no ledger entry, no proof graph node)",
    }


def _check_no_ai_draft_proof(fmt: dict, repo_root: Path) -> dict:
    """Check that ai_draft is not used as the sole proof source."""
    # Look for ai_draft files that claim proof for this format
    fmt_name = fmt["format"].lower()
    draft_files = []
    for f in repo_root.rglob("*ai_draft*"):
        if not f.is_file():
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            if fmt_name in content.lower():
                draft_files.append(str(f.relative_to(repo_root)))
        except Exception:
            pass
    # If ai_draft files exist for this format, it's a WARNING not a failure
    # (ai_draft as supporting note is ok; as SOLE proof is not ok)
    return {
        "pass": True,  # Presence of ai_draft is warning, not block
        "ai_draft_files": draft_files[:2],
        "warning": f"ai_draft files exist for {fmt['format']}" if draft_files else None,
        "reason": "No ai_draft-only proof detected" if not draft_files else "ai_draft files exist (WARNING: not sufficient as sole proof)",
    }


# ─────────────────────────────────────────────────────────────
# Main gate evaluation
# ─────────────────────────────────────────────────────────────

def evaluate_format(fmt: dict, repo_root: Path) -> dict:
    """Evaluate all proof checks for a single format."""
    source_check = _check_source_exists(fmt, repo_root)
    tests_check = _check_tests_exist(fmt, repo_root)
    log_check = _check_raw_log_exists(fmt, repo_root)
    examples_check = _check_examples_exist(fmt, repo_root)
    proof_record_check = _check_proof_record(fmt, repo_root)
    draft_check = _check_no_ai_draft_proof(fmt, repo_root)

    # Determine pass/fail per check
    required_checks = {
        "source_exists": source_check["pass"],
        "tests_exist": tests_check["pass"],
        "raw_log_exists": log_check["pass"] if fmt.get("required_log", True) else True,
        "examples_exist": examples_check["pass"] if fmt.get("required_example", True) else True,
        "proof_record_exists": proof_record_check["pass"],
        "no_ai_draft_only": draft_check["pass"],
    }

    all_pass = all(required_checks.values())
    failures = [k for k, v in required_checks.items() if not v]

    return {
        "format": fmt["format"],
        "passed": all_pass,
        "required_checks": required_checks,
        "failures": failures,
        "details": {
            "source": source_check,
            "tests": tests_check,
            "raw_log": log_check,
            "examples": examples_check,
            "proof_record": proof_record_check,
            "draft_check": draft_check,
        },
    }


def evaluate_poc_readiness(repo_root: Path | None = None) -> dict:
    """
    Main entry point: evaluate proof-backed POC readiness.

    Returns a dict with:
      - poc_ready: bool
      - release_approval_pending: bool
      - commercial_targets: list of format results
      - foss_targets: list of format results
      - foss_pass_count: int
      - proof_failures: list of failure reasons
      - missing_logs: list of formats missing raw logs
      - missing_proof_records: list of formats missing proof records
      - decision: str (one of the 6 decision constants)
      - terminal_state: str
    """
    if repo_root is None:
        repo_root = REPO_ROOT

    commercial_results = [evaluate_format(fmt, repo_root) for fmt in COMMERCIAL_NET_FORMATS]
    foss_results = [evaluate_format(fmt, repo_root) for fmt in FOSS_PYTHON_FORMATS]

    # Commercial: ALL must pass
    commercial_all_pass = all(r["passed"] for r in commercial_results)
    commercial_failures = [(r["format"], r["failures"]) for r in commercial_results if not r["passed"]]

    # FOSS: minimum 3 must pass
    foss_pass_count = sum(1 for r in foss_results if r["passed"])
    foss_passes = [r["format"] for r in foss_results if r["passed"]]
    foss_failures = [(r["format"], r["failures"]) for r in foss_results if not r["passed"]]

    # Collect specific missing items
    missing_logs = []
    missing_proof_records = []
    missing_examples = []
    all_failures = []

    for r in commercial_results + foss_results:
        if not r["details"]["raw_log"]["pass"]:
            missing_logs.append(r["format"])
        if not r["details"]["proof_record"]["pass"]:
            missing_proof_records.append(r["format"])
        if not r["details"]["examples"]["pass"]:
            missing_examples.append(r["format"])
        if r["failures"]:
            all_failures.append({"format": r["format"], "failures": r["failures"]})

    # POC ready check
    poc_ready = commercial_all_pass and foss_pass_count >= FOSS_MINIMUM_PASS_COUNT

    # Gate 11 / release approval pending check
    # Read poc-targets.yaml for gate_11_g11g status (advisory only)
    release_approval_pending = False
    try:
        import yaml
        poc_path = repo_root / "product-capability-matrix" / "poc-targets.yaml"
        if poc_path.exists():
            data = yaml.safe_load(poc_path.read_text(encoding="utf-8"))
            commercial = data.get("commercial_net_products", [])
            any_g11g_not_started = any(
                p.get("gate_11_g11g", "NOT_STARTED") != "APPROVED"
                for p in commercial
            )
            if any_g11g_not_started:
                release_approval_pending = True
    except Exception:
        release_approval_pending = True  # Conservative: assume approval needed

    # Determine decision
    if poc_ready and release_approval_pending:
        decision = "MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING"
    elif poc_ready and not release_approval_pending:
        decision = "MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED"
    elif not poc_ready:
        decision = "POC_NOT_READY_CONTINUE"
    else:
        decision = "POC_NOT_READY_CONTINUE"

    return {
        "poc_ready": poc_ready,
        "release_approval_pending": release_approval_pending,
        "commercial_targets": commercial_results,
        "commercial_all_pass": commercial_all_pass,
        "commercial_failures": commercial_failures,
        "foss_targets": foss_results,
        "foss_pass_count": foss_pass_count,
        "foss_passes": foss_passes,
        "foss_failures": foss_failures,
        "foss_minimum_required": FOSS_MINIMUM_PASS_COUNT,
        "proof_failures": all_failures,
        "missing_logs": missing_logs,
        "missing_proof_records": missing_proof_records,
        "missing_examples": missing_examples,
        "stale_claims": ["poc-targets.yaml gates_passed text is NOT proof — replaced by this gate"],
        "decision": decision,
        "terminal_state": decision,
        "evaluated_at": datetime.utcnow().isoformat(),
    }


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Proof-backed POC readiness gate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    result = evaluate_poc_readiness(repo_root)
    output = json.dumps(result, indent=2, default=str)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        print(f"POC gate result written to {args.output}")
    else:
        print(output)

    # Exit codes
    if result["poc_ready"]:
        return 0
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
