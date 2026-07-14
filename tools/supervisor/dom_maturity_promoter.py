"""DOM Maturity Promoter — checks contracts and updates ledger maturity.

Promotion is idempotent and cannot exceed ceiling.

Behavioral proof runner (TC-PCL-003): when .supervisor/dom-proofs/{format}.yaml
exists, run configured test commands instead of AST scan. Falls back to AST scan
when no proof file is present.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = REPO_ROOT / "registry" / "product-deepening-ledger.yaml"

sys.path.insert(0, str(Path(__file__).parent))
from dom_contract_checker import check_contract

_MATURITY_ORDER = {"D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D5": 5}


def load_dom_proofs(format_id: str, repo_root: Path = REPO_ROOT) -> dict:
    """Load .supervisor/dom-proofs/{format_id}.yaml proof definitions.

    Returns dict mapping level → proof_def, or empty dict if file absent.
    """
    proof_file = repo_root / ".supervisor" / "dom-proofs" / f"{format_id.lower()}.yaml"
    if not proof_file.exists():
        return {}
    try:
        data = yaml.safe_load(proof_file.read_text(encoding="utf-8"))
        return data.get("proofs", {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


def _normalize_test_command(cmd: str, repo_root: Path) -> str:
    """Normalize pytest invocation for the current platform.

    Replaces `.venv/Scripts/pytest` / `.venv/bin/pytest` with a quoted
    absolute-path invocation so cmd.exe (Windows shell=True) can run it.
    """
    import sys
    if sys.platform == "win32":
        venv_pytest = str(repo_root / ".venv" / "Scripts" / "pytest.exe")
        quoted = f'"{venv_pytest}"'
        if ".venv/Scripts/pytest" in cmd:
            cmd = cmd.replace(".venv/Scripts/pytest", quoted)
        elif ".venv\\Scripts\\pytest" in cmd:
            cmd = cmd.replace(".venv\\Scripts\\pytest", quoted)
    else:
        venv_pytest = str(repo_root / ".venv" / "bin" / "pytest")
        if ".venv/bin/pytest" in cmd:
            cmd = cmd.replace(".venv/bin/pytest", venv_pytest)
    return cmd


def run_proof(level: str, proof_def: dict, repo_root: Path = REPO_ROOT) -> dict:
    """Run a single level's proof test command.

    Returns {level, passed, stdout, stderr, reason}.
    """
    cmd = proof_def.get("test_command", "")
    if not cmd:
        return {"level": level, "passed": False, "reason": "no_command"}
    cmd = _normalize_test_command(cmd, repo_root)
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=repo_root,
            capture_output=True, text=True, timeout=120,
        )
        passed = result.returncode == 0
        return {
            "level": level,
            "passed": passed,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-500:],
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"level": level, "passed": False, "reason": "timeout"}
    except Exception as exc:
        return {"level": level, "passed": False, "reason": str(exc)}


def assess_dom_maturity(format_id: str, repo_root: Path = REPO_ROOT) -> dict:
    """Assess DOM maturity level via behavioral proof tests.

    Runs levels D1→D5 sequentially, stopping at first failure.
    Returns highest passing level (or D0 if none pass).
    When no proof file exists, returns fallback=ast_scan.
    """
    proofs = load_dom_proofs(format_id, repo_root)
    if not proofs:
        return {"computed_level": None, "fallback": "ast_scan", "proof_results": {}}
    passing_levels = []
    proof_results = {}
    for level in ["D1", "D2", "D3", "D4", "D5"]:
        if level not in proofs:
            continue
        result = run_proof(level, proofs[level], repo_root)
        proof_results[level] = result
        if result["passed"]:
            passing_levels.append(level)
        else:
            break  # Sequential: first failure stops
    computed = passing_levels[-1] if passing_levels else "D0"
    return {
        "computed_level": computed,
        "passing_levels": passing_levels,
        "proof_results": proof_results,
        "fallback": None,
    }


def check_promotion(format_name: str, target_level: str, ledger_path: Path | None = None) -> dict:
    """Check if a format is eligible for promotion to target_level.

    Returns {eligible, passed, failed, evidence_paths}.
    """
    path = ledger_path or DEFAULT_LEDGER
    ledger = yaml.safe_load(path.read_text(encoding="utf-8"))

    entry = next((e for e in ledger if e.get("format") == format_name.lower()
                  and e.get("runtime", "python") == "python"), None)
    if entry is None:
        return {"eligible": False, "error": f"Format '{format_name}' not found in ledger"}

    current = entry.get("lane_b_maturity", "D0")
    ceiling = entry.get("lane_b_ceiling", "D0")
    target_val = _MATURITY_ORDER.get(target_level, 0)
    current_val = _MATURITY_ORDER.get(current, 0)
    ceiling_val = _MATURITY_ORDER.get(ceiling, 0)

    # Already at or above target — idempotent no-op
    if current_val >= target_val:
        return {"eligible": False, "reason": "already_at_or_above_target",
                "current": current, "target": target_level}

    # Cannot promote beyond ceiling
    if target_val > ceiling_val:
        return {"eligible": False, "reason": "exceeds_ceiling",
                "target": target_level, "ceiling": ceiling}

    # Check contract
    contract = check_contract(format_name, target_level)
    passed = [c for c in contract["criteria"] if c["found"]]
    failed = [c for c in contract["criteria"] if not c["found"]]

    return {
        "eligible": contract["passed"],
        "format": format_name,
        "current": current,
        "target": target_level,
        "ceiling": ceiling,
        "passed": [c["id"] for c in passed],
        "failed": [c["id"] for c in failed],
        "criteria_detail": contract["criteria"],
    }


def promote(format_name: str, target_level: str,
            ledger_path: Path | None = None, dry_run: bool = False,
            repo_root: Path = REPO_ROOT) -> dict:
    """Promote a format to target_level if eligible.

    Behavioral proof (TC-PCL-003): if .supervisor/dom-proofs/{format}.yaml exists,
    use behavioral test results. Otherwise fall back to AST scan.
    No auto-demote: will not lower lane_b_maturity even if proof fails at claimed level.

    Returns {promoted, previous_level, new_level}.
    """
    path = ledger_path or DEFAULT_LEDGER

    # TC-PCL-003: Try behavioral proof first
    assessment = assess_dom_maturity(format_name, repo_root)
    if assessment.get("fallback") != "ast_scan":
        # Behavioral proof file exists — use computed level
        computed = assessment.get("computed_level", "D0")
        target_val = _MATURITY_ORDER.get(target_level, 0)
        computed_val = _MATURITY_ORDER.get(computed, 0)
        if computed_val < target_val:
            return {
                "promoted": False,
                "reason": "behavioral_proof_below_target",
                "computed_level": computed,
                "target": target_level,
                "proof_results": assessment.get("proof_results", {}),
            }
        # Proof passes at or above target — proceed with eligibility check
        eligibility = check_promotion(format_name, target_level, path)
        if not eligibility.get("eligible") and eligibility.get("reason") != "already_at_or_above_target":
            # May still be ineligible for other reasons (ceiling, not found)
            return {"promoted": False, **eligibility}
        if eligibility.get("reason") == "already_at_or_above_target":
            return {"promoted": False, **eligibility}
        if dry_run:
            return {"promoted": False, "dry_run": True, "would_promote": True,
                    "previous_level": eligibility["current"], "new_level": target_level,
                    "proof_method": "behavioral"}
    else:
        # Fallback: AST scan
        eligibility = check_promotion(format_name, target_level, path)
        if not eligibility.get("eligible"):
            return {"promoted": False, **eligibility}
        if dry_run:
            return {"promoted": False, "dry_run": True, "would_promote": True,
                    "previous_level": eligibility["current"], "new_level": target_level,
                    "proof_method": "ast_scan"}

    # Update ledger
    ledger = yaml.safe_load(path.read_text(encoding="utf-8"))
    for entry in ledger:
        if entry.get("format") == format_name.lower() and entry.get("runtime", "python") == "python":
            previous = entry["lane_b_maturity"]
            # No auto-demote: never lower the maturity
            if _MATURITY_ORDER.get(previous, 0) >= _MATURITY_ORDER.get(target_level, 0):
                return {"promoted": False, "reason": "no_auto_demote",
                        "current": previous, "target": target_level}
            entry["lane_b_maturity"] = target_level
            path.write_text(yaml.dump(ledger, default_flow_style=False, sort_keys=False), encoding="utf-8")
            return {"promoted": True, "previous_level": previous, "new_level": target_level,
                    "format": format_name}

    return {"promoted": False, "error": "entry_not_found_during_update"}


def main():
    parser = argparse.ArgumentParser(description="DOM Maturity Promoter")
    parser.add_argument("--format", required=True, help="Format name")
    parser.add_argument("--target", choices=["D2", "D3", "D4", "D5"],
                        help="Target maturity level (required unless --assess)")
    parser.add_argument("--ledger", default=None, help="Path to ledger YAML")
    parser.add_argument("--dry-run", action="store_true", help="Check without updating")
    parser.add_argument("--assess", action="store_true",
                        help="Run behavioral proof assessment without promoting")
    parser.add_argument("--force-regrade", action="store_true",
                        help="Allow downgrade in ledger (override no-auto-demote)")
    args = parser.parse_args()

    ledger_path = Path(args.ledger) if args.ledger else None

    if args.assess:
        result = assess_dom_maturity(args.format)
        print(json.dumps(result, indent=2, default=str))
        return 0 if result.get("computed_level") else 1

    if not args.target:
        parser.error("--target is required unless --assess")

    if args.dry_run:
        result = check_promotion(args.format, args.target, ledger_path)
    else:
        result = promote(args.format, args.target, ledger_path, dry_run=False)

    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("eligible") or result.get("promoted") else 1


if __name__ == "__main__":
    sys.exit(main())
