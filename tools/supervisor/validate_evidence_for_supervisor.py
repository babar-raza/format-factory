"""
validate_evidence_for_supervisor.py — Format Factory Local Supervisor Control Plane
Validates an evidence bundle and extracts structured facts for supervisor use.

Does NOT duplicate logic from validate_evidence_bundle.py — calls it as subprocess
if available and compatible. If not available, performs its own lightweight extraction.

Exit codes:
  0 — validation complete (may be ACCEPTED or with warnings)
  2 — validation failed / malformed bundle
  9 — unexpected error

Usage:
  python tools/supervisor/validate_evidence_for_supervisor.py --bundle path/to/bundle.zip
  python tools/supervisor/validate_evidence_for_supervisor.py --bundle path/to/bundle.zip --output-dir reports/supervisor
  python tools/supervisor/validate_evidence_for_supervisor.py --bundle path/to/bundle.zip --json
"""

import argparse
import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path


FINAL_VERDICT_PATTERNS = [
    "final-verdict.md",
    "reports/*/final-verdict.md",
]
GIT_STATUS_PATTERNS = [
    "git-status-final.txt",
    "bundle-metadata/git-status-final.txt",
]
TEST_LOG_PATTERNS = [
    "test-results.txt",
    "test-log.txt",
    "pytest.log",
    "bundle-metadata/test-results.txt",
]
CONTRACT_PATTERNS = [
    "bundle-metadata/contract.yaml",
    "contract.yaml",
    "sprint-contract.yaml",
]
SPRINT_ID_PATTERNS = [
    "bundle-metadata/sprint-id.txt",
    "sprint-id.txt",
]

PENDING_MARKERS = [
    "PENDING",
    "TO BE FILLED",
    "TODO",
    "PLACEHOLDER",
    "TBD",
]

# Delegation labels are intentional per R75 two-authority model — NOT pending markers
DELEGATION_LABELS = [
    "delegated_to_final_artifact_authority_json",
]


def read_zip_file(zf: zipfile.ZipFile, patterns: list[str]) -> tuple[str, str]:
    """Try to read first matching file. Returns (name, content) or ('', '')."""
    namelist = set(zf.namelist())
    for pattern in patterns:
        # Exact match first
        if pattern in namelist:
            return pattern, zf.read(pattern).decode("utf-8", errors="replace")
        # Suffix match
        for name in zf.namelist():
            if name.endswith(pattern.lstrip("*/")):
                return name, zf.read(name).decode("utf-8", errors="replace")
    return "", ""


def extract_test_counts(text: str) -> dict:
    """Extract test counts from pytest output text."""
    counts = {"test_count": 0, "fail_count": 0, "skip_count": 0}
    # pytest summary pattern: "N passed, M failed, K skipped"
    pattern = r"(\d+)\s+passed"
    m = re.search(pattern, text)
    if m:
        counts["test_count"] = int(m.group(1))
    m = re.search(r"(\d+)\s+failed", text)
    if m:
        counts["fail_count"] = int(m.group(1))
    m = re.search(r"(\d+)\s+skipped", text)
    if m:
        counts["skip_count"] = int(m.group(1))
    return counts


def extract_git_head(text: str) -> str:
    """Extract git HEAD SHA from text."""
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^([0-9a-f]{7,40})$", line)
        if m:
            return m.group(1)
        if "HEAD" in line or "commit" in line.lower():
            m = re.search(r"[0-9a-f]{7,40}", line)
            if m:
                return m.group(0)
    return "unknown"


def count_pending_markers(text: str) -> int:
    """Count PENDING-style markers in text, excluding delegation labels."""
    count = 0
    for line in text.splitlines():
        # Skip lines that contain delegation labels (intentional per R75)
        if any(dl in line for dl in DELEGATION_LABELS):
            continue
        for marker in PENDING_MARKERS:
            count += line.count(marker)
    return count


def extract_sprint_id(zf: zipfile.ZipFile) -> str:
    """Extract sprint_id from bundle."""
    # 1. Try sprint-id.txt (entire content is the sprint_id)
    name, content = read_zip_file(zf, SPRINT_ID_PATTERNS)
    if content and content.strip() and "\n" not in content.strip():
        return content.strip()
    # 2. Try bundle-metadata/sprint-summary.md (YAML field: sprint_id: ...)
    name, content = read_zip_file(zf, ["bundle-metadata/sprint-summary.md", "sprint-summary.md"])
    if content:
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("sprint_id:"):
                return line.split(":", 1)[-1].strip()
    # 3. Try most recent sprint final-verdict.md (prefer high-numbered /r<N>/ paths)
    verdict_files = [n for n in zf.namelist() if n.endswith("final-verdict.md")]

    def sprint_num_from_path(path: str) -> int:
        import re as _re
        m = _re.search(r"/r(\d+)/", path)
        return int(m.group(1)) if m else 0

    verdict_files.sort(key=sprint_num_from_path, reverse=True)
    for vname in verdict_files[:5]:
        vc = zf.read(vname).decode("utf-8", errors="replace")
        for line in vc.splitlines():
            if "FORMAT-FACTORY" in line:
                # Strip markdown/YAML prefixes
                line = line.strip().lstrip("#").lstrip("*").strip()
                if line.startswith("Sprint:") or line.startswith("sprint_id:"):
                    line = line.split(":", 1)[-1].strip()
                return line
    return "unknown"


def extract_gate_states(final_verdict_text: str) -> dict:
    """Extract gate states from final-verdict.md text."""
    gates = {}
    for line in final_verdict_text.splitlines():
        # Look for patterns like "gate_10: local_release_candidate_ready"
        m = re.search(r"gate_(\d+)[:\s]+(\w+)", line, re.IGNORECASE)
        if m:
            key = f"gate_{m.group(1)}"
            gates[key] = m.group(2)
    return gates


def invoke_existing_validator(bundle_path: Path, repo_root: Path, sprint_id: str = "") -> dict:
    """Try to invoke tools/evidence/validate_evidence_bundle.py as subprocess.

    Selects the contract that best matches the bundle's sprint_id, not the
    most-recently-modified file (which may be from a different sprint).
    """
    validator = repo_root / "tools" / "evidence" / "validate_evidence_bundle.py"
    if not validator.exists():
        return {"invoked": False, "reason": "validator not found"}

    contracts_dir = repo_root / "tools" / "evidence" / "contracts"
    if not contracts_dir.exists():
        return {"invoked": False, "reason": "contracts dir not found"}

    contracts = list(contracts_dir.glob("*.yaml"))
    if not contracts:
        return {"invoked": False, "reason": "no contracts found"}

    # Prefer contract whose filename matches the sprint_id or run_number
    best_contract = None
    if sprint_id and sprint_id != "unknown":
        # Extract run_number token (e.g. "r80") from sprint_id
        import re as _re
        rnum_m = _re.search(r"\br(\d+)\b", sprint_id, _re.IGNORECASE)
        run_token = rnum_m.group(0).lower() if rnum_m else ""
        for c in contracts:
            stem = c.stem.lower()
            if run_token and stem.startswith(run_token + "-"):
                best_contract = c
                break
            if sprint_id.lower()[:20] in stem:
                best_contract = c
                break

    if best_contract is None:
        # Fall back: prefer contract whose run_number matches (not just mtime)
        # Sort by run_number parsed from filename
        import re as _re

        def _run_num(p: Path) -> int:
            m = _re.match(r"r(\d+)-", p.stem)
            return int(m.group(1)) if m else 0

        matched = [c for c in contracts if _run_num(c) > 0]
        if matched:
            best_contract = max(matched, key=_run_num)
        else:
            best_contract = max(contracts, key=lambda p: p.stat().st_mtime)

    python = sys.executable
    cmd = [
        python,
        str(validator),
        "--contract", str(best_contract),
        "--bundle", str(bundle_path),
        "--no-strict-git",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(repo_root),
        )
        output = result.stdout + result.stderr
        return {
            "invoked": True,
            "exit_code": result.returncode,
            "output": output[:5000],
            "bundle_validation_pass": "BUNDLE_VALIDATION: PASS" in output,
            "contract_used": str(best_contract.name),
        }
    except subprocess.TimeoutExpired:
        return {"invoked": True, "exit_code": -1, "output": "TIMEOUT", "bundle_validation_pass": False}
    except Exception as e:
        return {"invoked": False, "reason": f"subprocess error: {e}"}


def validate(bundle_path: Path, repo_root: Path) -> dict:
    """Main validation logic. Returns structured result dict."""
    timestamp = datetime.now().isoformat()

    if not bundle_path.exists():
        return {
            "status": "error",
            "exit_code": 2,
            "error": f"Bundle not found: {bundle_path}",
            "timestamp": timestamp,
            "verdict": "BLOCKED_NO_BUNDLE",
        }

    try:
        with zipfile.ZipFile(bundle_path, "r") as zf:
            all_names = zf.namelist()
            entry_count = len(all_names)

            # Extract sprint_id
            sprint_id = extract_sprint_id(zf)

            # Extract final verdict
            verdict_name, verdict_text = read_zip_file(zf, ["final-verdict.md"])
            pending_count = count_pending_markers(verdict_text) if verdict_text else 0

            # Extract test logs — prefer current-sprint logs over historical ones
            test_name, test_text = read_zip_file(zf, TEST_LOG_PATTERNS)
            if not test_text or not extract_test_counts(test_text).get("test_count"):
                # Fall back: search all test log files, prefer highest-sprint directory
                import re as _re

                def _sprint_num(path: str) -> int:
                    m = _re.search(r"/r(\d+)/", path)
                    return int(m.group(1)) if m else 0

                candidate_logs = [
                    n for n in all_names
                    if (n.endswith("test-log.txt") or n.endswith("test-results.txt")
                        or n.endswith("pytest.log"))
                ]
                candidate_logs.sort(key=_sprint_num, reverse=True)
                for clog in candidate_logs:
                    c = zf.read(clog).decode("utf-8", errors="replace")
                    counts = extract_test_counts(c)
                    if counts.get("test_count", 0) > 0:
                        test_text = c
                        test_name = clog
                        break
            test_counts = extract_test_counts(test_text) if test_text else {}

            # Extract git head from git status or bundle metadata
            git_name, git_text = read_zip_file(zf, ["git-head.txt", "bundle-metadata/git-head.txt"])
            if not git_text:
                git_name, git_text = read_zip_file(zf, GIT_STATUS_PATTERNS)
            git_head = extract_git_head(git_text) if git_text else "unknown"

            # Extract gate states
            gate_states = extract_gate_states(verdict_text) if verdict_text else {}

    except zipfile.BadZipFile as e:
        return {
            "status": "malformed_zip",
            "exit_code": 2,
            "error": str(e),
            "bundle_path": str(bundle_path),
            "timestamp": timestamp,
            "verdict": "BLOCKED_MALFORMED_ZIP",
        }
    except Exception as e:
        return {
            "status": "error",
            "exit_code": 9,
            "error": f"Unexpected error: {e}",
            "bundle_path": str(bundle_path),
            "timestamp": timestamp,
            "verdict": "BLOCKED_MALFORMED_ZIP",
        }

    # Invoke existing validator if available (pass sprint_id for contract matching)
    existing_validator_result = invoke_existing_validator(bundle_path, repo_root, sprint_id)

    # Determine overall verdict
    fail_count = test_counts.get("fail_count", 0)
    bundle_validation_pass = existing_validator_result.get("bundle_validation_pass", False)
    validator_invoked = existing_validator_result.get("invoked", False)
    validator_output = existing_validator_result.get("output", "")
    sidecar_required_error = "SIDECAR_REQUIRED" in validator_output

    if not verdict_text:
        overall_verdict = "BLOCKED_MISSING_FINAL_VERDICT"
    elif validator_invoked and not bundle_validation_pass:
        # D86-SUP-01 fix: If the existing validator was invoked and reported FAIL, reject
        overall_verdict = "REJECTED_BUNDLE_VALIDATION_FAIL"
    elif sidecar_required_error:
        # D86-SUP-01 fix: Sidecar required but missing — reject
        overall_verdict = "REJECTED_SIDECAR_REQUIRED"
    elif pending_count > 0:
        # D86-SUP-02 fix: Any real PENDING marker (after excluding delegation labels) is a reject
        overall_verdict = "REJECTED"
    elif fail_count > 0:
        overall_verdict = "ACCEPTED_WITH_WARNINGS"
    else:
        overall_verdict = "ACCEPTED"

    limitation_notes = []
    if not verdict_text:
        limitation_notes.append("No final-verdict.md found in bundle")
    if not test_counts:
        limitation_notes.append("No test log found in bundle — test counts unavailable")
    if not existing_validator_result.get("invoked"):
        limitation_notes.append(
            f"Existing validator not invoked: {existing_validator_result.get('reason', 'unknown')}"
        )

    return {
        "sprint_id": sprint_id,
        "timestamp": timestamp,
        "verdict": overall_verdict,
        "bundle_path": str(bundle_path.resolve()),
        "facts": {
            "test_count": test_counts.get("test_count", 0),
            "fail_count": test_counts.get("fail_count", 0),
            "skip_count": test_counts.get("skip_count", 0),
            "git_head": git_head,
            "gate_states": gate_states,
            "final_verdict_text": verdict_text[:2000] if verdict_text else "",
            "pending_marker_count": pending_count,
            "bundle_entry_count": entry_count,
            "bundle_validation_pass": bundle_validation_pass,
            "validator_error_summary": (
                validator_output[:500] if validator_invoked and not bundle_validation_pass else ""
            ),
        },
        "contradictions": [],
        "limitation_notes": limitation_notes,
        "validator_invoked": existing_validator_result.get("invoked", False),
        "validator_output": existing_validator_result.get("output", ""),
        "bundle_validation_pass": existing_validator_result.get("bundle_validation_pass", False),
        "exit_code": 0,
        "status": "complete",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Format Factory evidence bundle for supervisor review"
    )
    parser.add_argument("--bundle", type=Path, required=True, help="Path to evidence ZIP bundle")
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
        help="Repository root (default: current directory)",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    result = validate(args.bundle, repo_root)

    # Write JSON output
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "evidence-review.json"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    # Write markdown output
    md_lines = [
        "# Evidence Review — Supervisor",
        f"Sprint ID: {result.get('sprint_id', 'unknown')}",
        f"Timestamp: {result.get('timestamp', '')}",
        f"Verdict: {result.get('verdict', '')}",
        f"Bundle: {result.get('bundle_path', '')}",
        "",
        "## Facts",
        f"- Tests: {result['facts']['test_count']} passed, {result['facts']['fail_count']} failed, {result['facts']['skip_count']} skipped",
        f"- Git HEAD: {result['facts']['git_head']}",
        f"- Bundle entries: {result['facts']['bundle_entry_count']}",
        f"- PENDING markers: {result['facts']['pending_marker_count']}",
        "",
        "## Gate States",
    ]
    for gate, state in result["facts"].get("gate_states", {}).items():
        md_lines.append(f"- {gate}: {state}")
    if not result["facts"].get("gate_states"):
        md_lines.append("(none extracted)")

    md_lines += [
        "",
        "## Limitation Notes",
    ]
    for note in result.get("limitation_notes", []):
        md_lines.append(f"- {note}")
    if not result.get("limitation_notes"):
        md_lines.append("None")

    if result.get("validator_output"):
        md_lines += [
            "",
            "## Existing Validator Output",
            "```",
            result["validator_output"][:2000],
            "```",
        ]

    md_path = output_dir / "evidence-review.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        verdict = result.get("verdict", "unknown")
        print(f"EVIDENCE_REVIEW: {verdict}")
        facts = result.get("facts", {})
        print(f"  Tests: {facts.get('test_count',0)} passed / {facts.get('fail_count',0)} failed")
        print(f"  PENDING markers: {facts.get('pending_marker_count',0)}")
        if result.get("limitation_notes"):
            for note in result["limitation_notes"]:
                print(f"  LIMITATION: {note}")

    return result.get("exit_code", 9)


if __name__ == "__main__":
    sys.exit(main())
