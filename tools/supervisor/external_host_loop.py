"""
external_host_loop.py — External Autonomous Host Loop (v2)

Reads a next-action.json contract, validates it, removes CLAUDECODE from the
child process environment, invokes Claude CLI with the specified prompt, and
verifies results using STRICT validation.

STRICT VALIDATION RULES (added in v2 — package-107 false-positive fix):
  - Substring marker detection is FORBIDDEN.
  - For NOOP mode: stdout.strip() must equal exactly the success_marker.
  - For SMOKE mode: stdout must be valid strict JSON with status, nonce, action_id.
  - The HOST RUNNER must NEVER create the proof file.
  - The CHILD AGENT must create the proof file before the host runner checks it.
  - Proof file must contain the nonce from next-action.json.
  - Permission prompts from Claude -> HOST_LOOP_BLOCKED_PERMISSION_PROMPT.
  - Marker found only in prose -> HOST_LOOP_FALSE_POSITIVE_MARKER_IN_PROSE.
  - Git violations outside allowed write roots -> HOST_LOOP_GIT_VIOLATION.

This script is designed to run OUTSIDE of Claude Code (no CLAUDECODE env var),
either from a PowerShell session, VS Code task, or Task Scheduler.

Exit codes:
  0 -- HOST_LOOP_SMOKE_PROVEN or HOST_LOOP_NOOP_PROVEN
  1 -- HOST_LOOP_BLOCKED or HOST_LOOP_FAILED
  2 -- HOST_LOOP_REFUSED_UNSAFE_ACTION
  3 -- next-action.json missing or invalid
  9 -- unexpected error

Classifications written to host-loop-result.json:
  HOST_LOOP_SMOKE_PROVEN              -- strict JSON child-created proof verified
  HOST_LOOP_NOOP_PROVEN               -- exact stdout match, no expected files
  HOST_LOOP_BLOCKED_CLAUDE_AUTH       -- Claude CLI auth failed
  HOST_LOOP_BLOCKED_CLAUDECODE        -- CLAUDECODE still set in child env
  HOST_LOOP_BLOCKED_PERMISSION_PROMPT -- Claude asked for approval instead of executing
  HOST_LOOP_REFUSED_UNSAFE_ACTION     -- prompt contains forbidden action keyword
  HOST_LOOP_FALSE_POSITIVE_MARKER_IN_PROSE -- marker found in prose, not structured output
  HOST_LOOP_GIT_VIOLATION             -- git changes outside allowed_write_roots
  HOST_LOOP_FAILED                    -- invocation failed or strict validation failed

Hard prohibitions (always refused, regardless of next-action.json contents):
  - git commit / git push / git merge
  - Gate 8 or Gate 11 approval
  - Package publication (nuget, pypi)
  - MCP activation
  - poc-targets.yaml direct mutation
  - src/ or tests/ file writes (outside allowed_write_roots)
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent

RESULT_CLASSIFICATIONS = {
    "SMOKE_PROVEN": "HOST_LOOP_SMOKE_PROVEN",
    "NOOP_PROVEN": "HOST_LOOP_NOOP_PROVEN",
    "BLOCKED_AUTH": "HOST_LOOP_BLOCKED_CLAUDE_AUTH",
    "BLOCKED_CLAUDECODE": "HOST_LOOP_BLOCKED_CLAUDECODE",
    "BLOCKED_PERMISSION_PROMPT": "HOST_LOOP_BLOCKED_PERMISSION_PROMPT",
    "REFUSED_UNSAFE": "HOST_LOOP_REFUSED_UNSAFE_ACTION",
    "FALSE_POSITIVE_PROSE": "HOST_LOOP_FALSE_POSITIVE_MARKER_IN_PROSE",
    "GIT_VIOLATION": "HOST_LOOP_GIT_VIOLATION",
    "FAILED": "HOST_LOOP_FAILED",
    "DRY_RUN_READY": "HOST_LOOP_DRY_RUN_READY",
}

# These keywords in a prompt are always refused -- no exceptions
HARD_STOP_KEYWORDS = [
    "git commit",
    "git push",
    "git merge",
    "gate 8 approval",
    "gate 11 approval",
    "nuget push",
    "pypi publish",
    "pip publish",
    "twine upload",
    "mcp activation",
    "commercial_product_ready: true",
    "authorized git",
    "directly mutate poc-targets",
]

# Patterns indicating Claude is asking for permission instead of executing
PERMISSION_PROMPT_PATTERNS = [
    "i need your approval",
    "could you approve",
    "do i have permission",
    "would you like me to proceed",
    "awaiting your approval",
    "please approve",
    "should i proceed",
    "awaiting approval",
    "request permission",
    "before i proceed",
    "to run these commands",
    "approve the following",
]

SCHEMA_VERSION_V1 = 1
SCHEMA_VERSION_V2 = 2
SUPPORTED_SCHEMA_VERSIONS = {SCHEMA_VERSION_V1, SCHEMA_VERSION_V2}


def _now() -> str:
    return datetime.now().isoformat()


def _append_log(log_path: Path, entry: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": _now(), **entry}) + "\n")


def load_next_action(next_action_path: Path) -> tuple[dict | None, str | None]:
    """Load and basic-validate next-action.json. Returns (data, error)."""
    if not next_action_path.exists():
        return None, f"next-action.json not found: {next_action_path}"
    try:
        data = json.loads(next_action_path.read_text(encoding="utf-8"))
    except Exception as e:
        return None, f"JSON parse error: {e}"
    schema_version = data.get("schema_version")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        return None, (
            f"Unsupported schema_version: {schema_version} "
            f"(expected one of {sorted(SUPPORTED_SCHEMA_VERSIONS)})"
        )
    required_v1 = [
        "action_id", "action_type", "mode", "prompt_path",
        "allowed_write_roots", "forbidden_actions", "success_marker",
        "max_runtime_seconds",
    ]
    for field in required_v1:
        if field not in data:
            return None, f"Missing required field: {field}"
    if schema_version == SCHEMA_VERSION_V2:
        if not data.get("nonce"):
            return None, "schema_version=2 requires a non-empty 'nonce' field"
        if not data.get("success_contract"):
            return None, "schema_version=2 requires a 'success_contract' field"
    return data, None


def detect_claude_cli() -> tuple[str | None, str]:
    """Find Claude CLI executable. Returns (path, reason)."""
    found = shutil.which("claude")
    if found:
        return found, f"Found on PATH: {found}"
    candidates = [
        r"C:\Users\prora\AppData\Roaming\npm\claude.CMD",
        r"C:\Users\prora\AppData\Roaming\npm\claude",
        "/c/Users/prora/AppData/Roaming/npm/claude",
        "/usr/local/bin/claude",
    ]
    for c in candidates:
        if Path(c).exists():
            return c, f"Found at explicit path: {c}"
    return None, "Claude CLI not found on PATH or any known location"


def scrub_claudecode_env() -> tuple[dict, bool]:
    """Return a copy of os.environ with CLAUDECODE removed.
    Returns (clean_env, was_claudecode_set)."""
    was_set = "CLAUDECODE" in os.environ and bool(os.environ.get("CLAUDECODE"))
    clean_env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    return clean_env, was_set


def check_prompt_safety(prompt_content: str, forbidden_actions: list[str]) -> list[str]:
    """Return list of violations found in prompt. Empty = safe."""
    violations = []
    content_lower = prompt_content.lower()
    for kw in HARD_STOP_KEYWORDS:
        if kw.lower() in content_lower:
            violations.append(f"HARD_STOP:{kw}")
    for fa in forbidden_actions:
        if fa.lower() in content_lower:
            violations.append(f"FORBIDDEN_ACTION:{fa}")
    return violations


def is_permission_prompt(stdout: str) -> bool:
    """Return True if Claude stdout appears to be asking for permission/approval."""
    s = stdout.lower()
    return any(pattern in s for pattern in PERMISSION_PROMPT_PATTERNS)


def is_marker_in_prose_only(stdout: str, marker: str) -> bool:
    """Return True if the marker appears in stdout but NOT as the sole content.
    Detects the false-positive pattern where marker is mentioned in explanatory prose.
    """
    stripped = stdout.strip()
    return bool(marker) and marker in stripped and stripped != marker


def validate_strict_json_output(
    stdout: str, action: dict
) -> tuple[bool, str | None, dict | None]:
    """Validate strict JSON output for SMOKE mode.

    Returns (valid, error_reason, parsed_json).
    The child agent must return a JSON object with at minimum:
      {"status": "<success_marker>", "action_id": "<action_id>", "nonce": "<nonce>"}
    """
    stripped = stdout.strip()
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError as e:
        return False, f"stdout is not valid JSON: {e}", None

    if not isinstance(data, dict):
        return False, f"stdout JSON is not an object, got: {type(data).__name__}", None

    success_marker = action.get("success_marker", "")
    if data.get("status") != success_marker:
        return (
            False,
            f"stdout JSON status={data.get('status')!r} != expected={success_marker!r}",
            data,
        )

    expected_action_id = action.get("action_id", "")
    if data.get("action_id") != expected_action_id:
        return (
            False,
            f"stdout JSON action_id={data.get('action_id')!r} != expected={expected_action_id!r}",
            data,
        )

    expected_nonce = action.get("nonce", "")
    if expected_nonce:
        if data.get("nonce") != expected_nonce:
            return (
                False,
                f"stdout JSON nonce mismatch (expected {expected_nonce!r}, got {data.get('nonce')!r})",
                data,
            )

    return True, None, data


def verify_child_proof_file(
    proof_path: Path, action: dict
) -> tuple[bool, str | None]:
    """Verify the child agent created the proof file with correct content.

    The host runner MUST NEVER create this file.
    Returns (valid, error_reason).
    """
    if not proof_path.exists():
        return False, f"child-created proof file not found: {proof_path}"

    content = proof_path.read_text(encoding="utf-8")

    success_marker = action.get("success_marker", "")
    if success_marker and success_marker not in content:
        return False, f"proof file missing success_marker: {success_marker!r}"

    if action.get("schema_version") == SCHEMA_VERSION_V2:
        nonce = action.get("nonce", "")
        if nonce and nonce not in content:
            return False, f"proof file missing nonce {nonce!r} (nonce mismatch)"
        action_id = action.get("action_id", "")
        if action_id and action_id not in content:
            return False, f"proof file missing action_id {action_id!r}"

    return True, None


def verify_git_status(
    repo_root: Path, allowed_write_roots: list[str]
) -> tuple[bool, list[str]]:
    """Check git status -- fail if any changed files are outside allowed_write_roots.
    Returns (clean, list_of_violations).
    """
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=str(repo_root), timeout=15,
        )
        if r.returncode != 0:
            return False, [f"git status failed: {r.stderr[:200]}"]
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        violations = []
        for line in lines:
            path = line[3:].strip().strip('"')
            allowed = any(path.startswith(root) for root in allowed_write_roots)
            if not allowed:
                violations.append(path)
        return len(violations) == 0, violations
    except Exception as e:
        return False, [f"git status error: {e}"]


def invoke_claude(
    cli_path: str,
    prompt: str,
    clean_env: dict,
    timeout: int,
    dry_run: bool = False,
) -> dict:
    """Invoke Claude CLI with --print mode. Returns result dict."""
    if dry_run:
        return {
            "dry_run": True,
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "classification": RESULT_CLASSIFICATIONS["DRY_RUN_READY"],
        }
    try:
        r = subprocess.run(
            [cli_path, "--print", "-p", prompt],
            capture_output=True,
            text=True,
            env=clean_env,
            timeout=timeout,
        )
        stdout = r.stdout
        stderr = r.stderr

        if "cannot be launched inside another claude code session" in (stdout + stderr).lower():
            return {
                "exit_code": r.returncode,
                "stdout": stdout[:500],
                "stderr": stderr[:500],
                "classification": RESULT_CLASSIFICATIONS["BLOCKED_CLAUDECODE"],
            }

        if any(kw in (stdout + stderr).lower() for kw in ["not authenticated", "login required", "auth"]):
            if r.returncode != 0:
                return {
                    "exit_code": r.returncode,
                    "stdout": stdout[:500],
                    "stderr": stderr[:500],
                    "classification": RESULT_CLASSIFICATIONS["BLOCKED_AUTH"],
                }

        # Check for permission prompt -- Claude asking for approval instead of acting
        if is_permission_prompt(stdout):
            return {
                "exit_code": r.returncode,
                "stdout": stdout[:2000],
                "stderr": stderr[:500],
                "classification": RESULT_CLASSIFICATIONS["BLOCKED_PERMISSION_PROMPT"],
                "permission_prompt_detected": True,
            }

        return {
            "exit_code": r.returncode,
            "stdout": stdout[:2000],
            "stderr": stderr[:500],
            "classification": None,  # determined by caller
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": "TIMEOUT",
            "stdout": "",
            "stderr": f"Timeout after {timeout}s",
            "classification": RESULT_CLASSIFICATIONS["FAILED"],
        }
    except Exception as e:
        return {
            "exit_code": "ERROR",
            "stdout": "",
            "stderr": str(e),
            "classification": RESULT_CLASSIFICATIONS["FAILED"],
        }


def run_host_loop(
    next_action_path: Path,
    repo_root: Path,
    output_dir: Path,
    dry_run: bool = False,
) -> dict:
    """Main host loop logic with strict validation.

    IMPORTANT: This function NEVER creates proof files.
    Only VERIFIES child-created files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "host-loop-log.jsonl"
    result_path = output_dir / "host-loop-result.json"

    _append_log(log_path, {"event": "start", "dry_run": dry_run, "next_action": str(next_action_path)})

    # 1. Load next-action.json
    action, err = load_next_action(next_action_path)
    if err:
        result = {
            "classification": RESULT_CLASSIFICATIONS["FAILED"],
            "error": err,
            "next_action_path": str(next_action_path),
        }
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        _append_log(log_path, {"event": "next_action_load_failed", "error": err})
        return result

    _append_log(log_path, {"event": "next_action_loaded", "action_id": action["action_id"]})

    # 2. Load prompt
    prompt_path = repo_root / action["prompt_path"]
    if not prompt_path.exists():
        result = {
            "classification": RESULT_CLASSIFICATIONS["FAILED"],
            "error": f"Prompt file not found: {prompt_path}",
        }
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    prompt_content = prompt_path.read_text(encoding="utf-8")
    _append_log(log_path, {"event": "prompt_loaded", "path": str(prompt_path), "length": len(prompt_content)})

    # 3. Safety check
    violations = check_prompt_safety(prompt_content, action.get("forbidden_actions", []))
    if violations:
        result = {
            "classification": RESULT_CLASSIFICATIONS["REFUSED_UNSAFE"],
            "violations": violations,
            "prompt_path": str(prompt_path),
        }
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        _append_log(log_path, {"event": "prompt_refused", "violations": violations})
        return result

    _append_log(log_path, {"event": "prompt_safe"})

    # 4. Detect Claude CLI
    cli_path, cli_reason = detect_claude_cli()
    if not cli_path:
        result = {
            "classification": RESULT_CLASSIFICATIONS["BLOCKED_AUTH"],
            "error": cli_reason,
        }
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    _append_log(log_path, {"event": "cli_detected", "path": cli_path, "reason": cli_reason})

    # 5. Scrub CLAUDECODE from child env
    clean_env, was_claudecode_set = scrub_claudecode_env()
    _append_log(log_path, {"event": "claudecode_scrub", "was_set": was_claudecode_set, "scrubbed": True})

    # 6. Invoke Claude
    invocation_result = invoke_claude(
        cli_path=cli_path,
        prompt=prompt_content,
        clean_env=clean_env,
        timeout=action["max_runtime_seconds"],
        dry_run=dry_run,
    )
    _append_log(log_path, {"event": "invocation_complete", "result": {
        "exit_code": invocation_result.get("exit_code"),
        "stdout_len": len(invocation_result.get("stdout", "")),
        "classification": invocation_result.get("classification"),
        "permission_prompt": invocation_result.get("permission_prompt_detected", False),
    }})

    # 7. Early exit for definitive pre-validation classifications
    if invocation_result.get("classification") in (
        RESULT_CLASSIFICATIONS["BLOCKED_CLAUDECODE"],
        RESULT_CLASSIFICATIONS["BLOCKED_AUTH"],
        RESULT_CLASSIFICATIONS["BLOCKED_PERMISSION_PROMPT"],
        RESULT_CLASSIFICATIONS["FAILED"],
        RESULT_CLASSIFICATIONS["DRY_RUN_READY"],
    ):
        result = {**invocation_result, "action_id": action["action_id"]}
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    stdout = invocation_result.get("stdout", "")
    success_marker = action.get("success_marker", "")
    schema_version = action.get("schema_version", SCHEMA_VERSION_V1)
    expected_files = action.get("expected_output_files", [])
    success_contract = action.get("success_contract", {})

    # 8. Validate strict output
    # IMPORTANT: Host runner NEVER creates proof files here.
    if not expected_files:
        # NOOP mode: stdout.strip() must equal success_marker exactly
        if success_marker:
            if stdout.strip() != success_marker:
                if is_marker_in_prose_only(stdout, success_marker):
                    result = {
                        "classification": RESULT_CLASSIFICATIONS["FALSE_POSITIVE_PROSE"],
                        "action_id": action["action_id"],
                        "error": (
                            f"marker '{success_marker}' found in prose output, "
                            f"not as exact standalone response"
                        ),
                        "stdout_excerpt": stdout[:500],
                    }
                    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
                    _append_log(log_path, {"event": "false_positive_prose"})
                    return result
                result = {
                    "classification": RESULT_CLASSIFICATIONS["FAILED"],
                    "action_id": action["action_id"],
                    "error": (
                        f"stdout does not equal expected marker. "
                        f"Got: {stdout.strip()[:200]!r}, expected: {success_marker!r}"
                    ),
                }
                result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
                return result
        marker_found = True
    else:
        # SMOKE mode: require strict JSON output
        stdout_mode = success_contract.get("stdout_mode", "STRICT_JSON")
        if stdout_mode == "STRICT_JSON":
            valid_json, json_error, _parsed = validate_strict_json_output(stdout, action)
            if not valid_json:
                if success_marker and is_marker_in_prose_only(stdout, success_marker):
                    result = {
                        "classification": RESULT_CLASSIFICATIONS["FALSE_POSITIVE_PROSE"],
                        "action_id": action["action_id"],
                        "error": f"marker found in prose (not strict JSON): {json_error}",
                        "stdout_excerpt": stdout[:500],
                    }
                    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
                    _append_log(log_path, {"event": "false_positive_prose", "error": json_error})
                    return result
                result = {
                    "classification": RESULT_CLASSIFICATIONS["FAILED"],
                    "action_id": action["action_id"],
                    "error": f"strict JSON validation failed: {json_error}",
                    "stdout_excerpt": stdout[:500],
                }
                result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
                return result
            _append_log(log_path, {"event": "strict_json_valid"})
            marker_found = True
        else:
            result = {
                "classification": RESULT_CLASSIFICATIONS["FAILED"],
                "error": f"Unknown stdout_mode: {stdout_mode!r}",
            }
            result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
            return result

    # 9. Verify child-created proof files (host runner MUST NOT create these)
    missing_files = []
    proof_errors = []
    for ef in expected_files:
        ef_path = repo_root / ef
        valid, proof_err = verify_child_proof_file(ef_path, action)
        if not valid:
            missing_files.append(ef)
            proof_errors.append(proof_err)
            _append_log(log_path, {"event": "child_proof_missing", "path": ef, "error": proof_err})
        else:
            _append_log(log_path, {"event": "child_proof_verified", "path": ef})

    # 10. Verify git status within allowed roots -- violations block smoke
    allowed_roots = action.get("allowed_write_roots", [])
    git_clean, git_violations = verify_git_status(repo_root, allowed_roots)

    if not git_clean and git_violations:
        result = {
            "classification": RESULT_CLASSIFICATIONS["GIT_VIOLATION"],
            "action_id": action["action_id"],
            "git_violations_count": len(git_violations),
            "git_violations_sample": git_violations[:10],
            "allowed_write_roots": allowed_roots,
            "note": "git changes detected outside allowed_write_roots",
        }
        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        _append_log(log_path, {"event": "git_violation", "count": len(git_violations)})
        return result

    # 11. Classify final result
    if expected_files and not missing_files and marker_found:
        classification = RESULT_CLASSIFICATIONS["SMOKE_PROVEN"]
    elif not expected_files and marker_found and invocation_result["exit_code"] == 0:
        classification = RESULT_CLASSIFICATIONS["NOOP_PROVEN"]
    else:
        classification = RESULT_CLASSIFICATIONS["FAILED"]

    result = {
        "classification": classification,
        "action_id": action["action_id"],
        "schema_version": schema_version,
        "invocation": invocation_result,
        "success_marker_found": marker_found,
        "expected_files": expected_files,
        "missing_files": missing_files,
        "proof_errors": proof_errors,
        "git_clean": git_clean,
        "git_violations_count": len(git_violations),
        "was_claudecode_scrubbed": was_claudecode_set,
        "cli_path": cli_path,
        "dry_run": dry_run,
        "timestamp": _now(),
        "strict_validation": True,
    }
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    _append_log(log_path, {"event": "complete", "classification": classification})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="External Autonomous Host Loop v2")
    parser.add_argument(
        "--next-action",
        default="reports/autonomous-external-host-bootstrap/next-action.json",
        help="Path to next-action.json contract",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root (auto-detect if not set)",
    )
    parser.add_argument(
        "--output-dir",
        default="reports/autonomous-external-host-bootstrap/host-loop",
        help="Output directory for logs and result",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Detect CLI and check safety but do NOT invoke (default: live)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else REPO_ROOT
    next_action_path = repo_root / args.next_action
    output_dir = repo_root / args.output_dir

    try:
        result = run_host_loop(
            next_action_path=next_action_path,
            repo_root=repo_root,
            output_dir=output_dir,
            dry_run=args.dry_run,
        )
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        return 9

    classification = result.get("classification", "UNKNOWN")
    print(f"HOST LOOP RESULT: {classification}")
    if result.get("error"):
        print(f"  Error: {result['error']}")
    if result.get("violations"):
        print(f"  Violations: {result['violations']}")
    if result.get("missing_files"):
        print(f"  Missing files: {result['missing_files']}")
    if result.get("proof_errors"):
        print(f"  Proof errors: {result['proof_errors']}")
    if result.get("git_violations_count"):
        print(f"  Git violations count: {result['git_violations_count']}")

    proven = classification in (
        RESULT_CLASSIFICATIONS["SMOKE_PROVEN"],
        RESULT_CLASSIFICATIONS["NOOP_PROVEN"],
        RESULT_CLASSIFICATIONS["DRY_RUN_READY"],
    )
    return 0 if proven else 1


if __name__ == "__main__":
    sys.exit(main())
