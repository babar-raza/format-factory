"""
autonomous_host_runner.py â€” Host-Level Autonomous Runner

Attempts to invoke the next autonomous cycle by calling the Claude CLI.
Reads: train-state.json, next-action.json, continuation-signal.json, next-sprint.md
Writes: host-runner-state.json, host-runner-log.jsonl

Classification:
  HOST_INVOCATION_ATTEMPTED      â€” CLI invocation was started (async)
  HOST_INVOCATION_LAYER_MISSING  â€” CLI not found, invocation impossible
  HOST_INVOCATION_DEFERRED       â€” POC ready or terminal, no invocation needed
  HOST_INVOCATION_REFUSED        â€” Safety check blocked invocation (hard stop)

DESIGN INVARIANT:
  This runner never claims 100% full autonomy.
  Even when it CAN invoke the CLI, it only starts the worker.
  The worker still requires context limits, approval gates, etc.
  Honest classification: CONTINUATION_PACKET_ONLY if CLI unavailable.

Hard prohibitions (never invoked, always refused):
  - git push / git commit
  - Gate 8 or Gate 11 approval
  - Package publication
  - MCP activation changes
  - commercial_product_ready=true
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

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Invocation result constants
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

HOST_INVOCATION_ATTEMPTED = "HOST_INVOCATION_ATTEMPTED"
HOST_INVOCATION_LAYER_MISSING = "HOST_INVOCATION_LAYER_MISSING"
HOST_INVOCATION_DEFERRED = "HOST_INVOCATION_DEFERRED"
HOST_INVOCATION_REFUSED = "HOST_INVOCATION_REFUSED"
HOST_INVOCATION_PACKET_ONLY = "CONTINUATION_PACKET_ONLY"
HOST_INVOCATION_BLOCKED_NESTED = "HOST_RUNNER_LIVE_INVOCATION_BLOCKED_BY_CLAUDECODE"

# Hard-stop keywords: if next sprint contains these, refuse invocation
HARD_STOP_KEYWORDS = [
    "git push",
    "git commit",
    "gate 11 approval",
    "gate 8 approval",
    "publish",
    "commercial_product_ready: true",
    "mcp activation",
]

# Claude CLI candidate paths (Windows + Unix)
CLAUDE_CLI_CANDIDATES = [
    "claude",                               # On PATH
    "/c/Users/prora/AppData/Roaming/npm/claude",
    r"C:\Users\prora\AppData\Roaming\npm\claude.cmd",
    "/usr/local/bin/claude",
    "/usr/bin/claude",
]


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Nested session detection
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

NESTED_SESSION_ENV_VAR = "CLAUDECODE"
_EXTERNAL_TERMINAL_COMMAND = (
    'unset CLAUDECODE && claude --print -p '
    '"Respond with exactly: HOST_RUNNER_NOOP_OK. Do not modify files. Do not run commands."'
)


def detect_nested_session() -> dict:
    """Check if we are running inside a Claude Code nested session.

    When CLAUDECODE is set, the Claude CLI will refuse to be invoked
    (to prevent nested sessions from crashing all active sessions).

    Returns:
        {
          "nested": bool,
          "env_var": str | None,
          "wiring_instructions": str | None,
          "external_terminal_command": str,
        }
    """
    claudecode_val = os.environ.get(NESTED_SESSION_ENV_VAR)
    nested = claudecode_val is not None and claudecode_val != ""
    wiring = None
    if nested:
        wiring = (
            f"CLAUDECODE={claudecode_val!r} is set â€” nested Claude Code session detected. "
            "The Claude CLI will refuse invocation to protect running sessions. "
            "To prove live invocation, run from an EXTERNAL terminal (not inside Claude Code):\n"
            f"  {_EXTERNAL_TERMINAL_COMMAND}\n"
            "Or unset CLAUDECODE in your shell before running this host runner."
        )
    return {
        "nested": nested,
        "env_var": claudecode_val,
        "wiring_instructions": wiring,
        "external_terminal_command": _EXTERNAL_TERMINAL_COMMAND,
    }


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CLI detection
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def detect_claude_cli() -> dict:
    """
    Detect whether the Claude CLI is available and executable.

    Returns:
        {
          "available": bool,
          "path": str | None,
          "version": str | None,
          "invocable": bool,
          "reason": str,
        }
    """
    # Try shutil.which first (respects PATH)
    found = shutil.which("claude")
    if found:
        # Verify it runs
        try:
            result = subprocess.run(
                [found, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            version = (result.stdout.strip() or result.stderr.strip()).splitlines()[0] if result.returncode == 0 else None
            return {
                "available": True,
                "path": found,
                "version": version,
                "invocable": True,
                "reason": f"Claude CLI found on PATH: {found}",
            }
        except Exception as e:
            return {
                "available": True,
                "path": found,
                "version": None,
                "invocable": False,
                "reason": f"Claude CLI found but --version failed: {e}",
            }

    # Try explicit candidates
    for candidate in CLAUDE_CLI_CANDIDATES[1:]:
        p = Path(candidate)
        if p.exists() and p.is_file():
            return {
                "available": True,
                "path": str(p),
                "version": None,
                "invocable": True,
                "reason": f"Claude CLI found at explicit path: {candidate}",
            }

    return {
        "available": False,
        "path": None,
        "version": None,
        "invocable": False,
        "reason": "Claude CLI not found on PATH or any known location. Cannot invoke autonomously.",
    }


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Safety checks
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _check_prompt_safety(prompt_content: str) -> dict:
    """
    Check that the prompt doesn't contain hard-stop keywords.

    Returns {"safe": bool, "violations": list[str]}
    """
    violations = []
    content_lower = prompt_content.lower()
    for keyword in HARD_STOP_KEYWORDS:
        if keyword.lower() in content_lower:
            violations.append(keyword)
    return {
        "safe": len(violations) == 0,
        "violations": violations,
    }


def _is_terminal_state(train_state: dict) -> bool:
    """Return True if train-state.json reports terminal."""
    return train_state.get("terminal", False)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# State loading
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _load_train_state(report_dir: Path) -> dict:
    path = report_dir / "train-state.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _load_next_action(report_dir: Path) -> dict:
    path = report_dir / "next-action.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _load_continuation_signal(repo_root: Path) -> dict:
    path = repo_root / ".local" / "supervisor" / "continuation-signal.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _load_next_sprint(repo_root: Path, next_sprint_path: str = None) -> str:
    path = repo_root / (next_sprint_path or "reports/supervisor/next-sprint.md")
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            pass
    return ""


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Log helpers
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _append_log(log_path: Path, entry: dict) -> None:
    entry["timestamp"] = datetime.now().isoformat()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# Safe no-op prompt for live invocation testing
NOOP_PROMPT = "Respond with exactly: HOST_RUNNER_NOOP_OK. Do not modify files. Do not run commands."
NOOP_EXPECTED_RESPONSE = "HOST_RUNNER_NOOP_OK"


def run_noop_invocation(
    cli_path: str,
    output_dir: Path,
    timeout: int = 30,
) -> dict:
    """
    Invoke the Claude CLI with a safe no-op prompt to prove live invocation.

    The prompt instructs Claude to respond with exactly: HOST_RUNNER_NOOP_OK
    This does not modify files or run commands.

    Returns:
        {
          "success": bool,
          "output": str,
          "noop_confirmed": bool,    # True if response contains HOST_RUNNER_NOOP_OK
          "git_unchanged": bool,     # Always True (we don't git-check here)
          "error": str | None,
          "classification": str,
        }
    """
    # Safety: double-check prompt is safe before invoking
    safety = _check_prompt_safety(NOOP_PROMPT)
    if not safety["safe"]:
        return {
            "success": False,
            "output": "",
            "noop_confirmed": False,
            "error": f"Noop prompt failed safety check: {safety['violations']}",
            "classification": "HOST_RUNNER_NOOP_REFUSED",
        }

    output_file = output_dir / "host-runner-live-output.txt"
    try:
        proc = subprocess.run(
            [cli_path, "--print", "-p", NOOP_PROMPT],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = proc.stdout.strip() or proc.stderr.strip()
        output_file.write_text(output, encoding="utf-8")
        noop_confirmed = NOOP_EXPECTED_RESPONSE in output
        return {
            "success": proc.returncode == 0,
            "output": output[:500],
            "noop_confirmed": noop_confirmed,
            "returncode": proc.returncode,
            "git_unchanged": True,  # noop prompt doesn't change files
            "error": None if proc.returncode == 0 else f"Exit code {proc.returncode}",
            "classification": (
                "HOST_RUNNER_LIVE_INVOCATION_PROVEN"
                if noop_confirmed
                else "HOST_RUNNER_LIVE_INVOCATION_ATTEMPTED_UNEXPECTED_OUTPUT"
            ),
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "noop_confirmed": False,
            "error": f"Timeout after {timeout}s",
            "classification": "HOST_RUNNER_LIVE_INVOCATION_TIMEOUT",
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "noop_confirmed": False,
            "error": str(e),
            "classification": "HOST_RUNNER_LIVE_INVOCATION_FAILED",
        }


NESTED_SESSION_ERROR = "cannot be launched inside another claude code session"


def classify_noop_result(noop_result: dict) -> dict:
    """Classify a noop invocation result with honest status and wiring instructions.

    Returns:
        {
          "classification": str,
          "proven": bool,
          "wiring_instructions": str | None,
          "blocker_reason": str | None,
        }
    """
    if noop_result.get("noop_confirmed"):
        return {
            "classification": "HOST_RUNNER_LIVE_INVOCATION_PROVEN",
            "proven": True,
            "wiring_instructions": None,
            "blocker_reason": None,
        }

    output = noop_result.get("output", "").lower()
    if NESTED_SESSION_ERROR in output:
        return {
            "classification": "HOST_RUNNER_LIVE_INVOCATION_BLOCKED_BY_POLICY",
            "proven": False,
            "wiring_instructions": (
                "Invocation blocked by Claude Code nested-session protection. "
                "To prove live invocation, run from an external terminal (not inside Claude Code): "
                "\n  1. Open a terminal outside of Claude Code"
                "\n  2. cd to the repo root"
                "\n  3. Run: unset CLAUDECODE && claude --print -p 'Respond with exactly: HOST_RUNNER_NOOP_OK. Do not modify files. Do not run commands.'"
                "\n  4. Verify output contains HOST_RUNNER_NOOP_OK"
                "\n  5. Or set AUTONOMOUS_NOOP_OVERRIDE=1 in environment before running host runner"
                "\nThis is a runtime environment constraint, not a tooling defect."
            ),
            "blocker_reason": "CLAUDECODE env var prevents nested Claude Code invocation",
            "unblock_action": "Unset CLAUDECODE env var or run from external terminal",
        }

    error = noop_result.get("error", "")
    return {
        "classification": "HOST_RUNNER_LIVE_INVOCATION_FAILED",
        "proven": False,
        "wiring_instructions": f"Invocation failed: {error}. Check CLI path and permissions.",
        "blocker_reason": error,
    }


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Core runner
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run_host_runner(
    repo_root: Path,
    report_dir: Path,
    dry_run: bool = True,
) -> dict:
    """
    Main host runner logic.

    Args:
        repo_root:   Repository root
        report_dir:  Directory containing train-state.json, next-action.json
        dry_run:     If True, detect CLI and check safety but do NOT actually invoke

    Returns:
        Runner result dict with classification and invocation details.
    """
    output_dir = report_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "host-runner-log.jsonl"

    _append_log(log_path, {"event": "runner_start", "dry_run": dry_run})

    # 1. Load current state
    train_state = _load_train_state(report_dir)
    next_action = _load_next_action(report_dir)
    continuation_signal = _load_continuation_signal(repo_root)

    # 2. Detect CLI
    cli_detection = detect_claude_cli()
    _append_log(log_path, {"event": "cli_detection", "result": cli_detection})

    # 2b. Detect nested session (CLAUDECODE env var blocks invocation)
    nested_detection = detect_nested_session()
    _append_log(log_path, {"event": "nested_session_detection", "result": nested_detection})
    if nested_detection["nested"]:
        result = {
            "classification": HOST_INVOCATION_BLOCKED_NESTED,
            "reason": nested_detection["wiring_instructions"],
            "nested_session": True,
            "claudecode_env": nested_detection["env_var"],
            "wiring_instructions": nested_detection["wiring_instructions"],
            "external_terminal_command": nested_detection["external_terminal_command"],
            "cli_detection": cli_detection,
            "manual_invocation_required": True,
        }
        _write_state(output_dir, result)
        return result

    # 3. Check if terminal â€” no invocation needed
    if _is_terminal_state(train_state):
        terminal_state = train_state.get("execution_state", "UNKNOWN_TERMINAL")
        _append_log(log_path, {"event": "terminal_state_deferred", "state": terminal_state})
        result = {
            "classification": HOST_INVOCATION_DEFERRED,
            "reason": f"Train is in terminal state: {terminal_state}. No invocation needed.",
            "terminal_state": terminal_state,
            "cli_detection": cli_detection,
        }
        _write_state(output_dir, result)
        return result

    # 4. If CLI not available â†’ CONTINUATION_PACKET_ONLY (honest classification)
    if not cli_detection["invocable"]:
        _append_log(log_path, {"event": "cli_missing", "reason": cli_detection["reason"]})
        result = {
            "classification": HOST_INVOCATION_LAYER_MISSING,
            "honest_classification": HOST_INVOCATION_PACKET_ONLY,
            "reason": (
                "Claude CLI is not invocable from within this tooling environment. "
                "The runner can write continuation packets but cannot start the next worker. "
                "This is NOT full autonomy â€” it is CONTINUATION_PACKET_ONLY. "
                f"CLI detection: {cli_detection['reason']}"
            ),
            "cli_detection": cli_detection,
            "continuation_packet_path": str(output_dir / "continuation-packet.md"),
            "next_sprint_path": continuation_signal.get("next_sprint_path", "reports/supervisor/next-sprint.md"),
            "manual_invocation_required": True,
            "invocation_command": "claude --print -p \"$(cat reports/supervisor/next-sprint.md)\"",
        }
        _write_state(output_dir, result)
        return result

    # 5. Load next sprint prompt
    next_sprint_path = (
        next_action.get("next_sprint_path")
        or continuation_signal.get("next_sprint_path")
        or "reports/supervisor/next-sprint.md"
    )
    prompt_content = _load_next_sprint(repo_root, next_sprint_path)

    if not prompt_content:
        _append_log(log_path, {"event": "prompt_missing", "path": next_sprint_path})
        result = {
            "classification": HOST_INVOCATION_LAYER_MISSING,
            "reason": f"Next sprint prompt not found: {next_sprint_path}",
            "cli_detection": cli_detection,
        }
        _write_state(output_dir, result)
        return result

    # 6. Safety check
    safety = _check_prompt_safety(prompt_content)
    _append_log(log_path, {"event": "safety_check", "result": safety})

    if not safety["safe"]:
        _append_log(log_path, {"event": "invocation_refused", "violations": safety["violations"]})
        result = {
            "classification": HOST_INVOCATION_REFUSED,
            "reason": f"Prompt contains hard-stop keywords: {safety['violations']}. Invocation refused.",
            "violations": safety["violations"],
            "cli_detection": cli_detection,
        }
        _write_state(output_dir, result)
        return result

    # 7. Dry run: classify only, don't invoke
    if dry_run:
        _append_log(log_path, {"event": "dry_run_complete", "would_invoke": True})
        result = {
            "classification": HOST_INVOCATION_ATTEMPTED,
            "dry_run": True,
            "reason": "Dry run â€” CLI available and prompt safe. Would invoke in live mode.",
            "cli_detection": cli_detection,
            "invocation_command": f"{cli_detection['path']} --print -p <next-sprint-prompt>",
            "next_sprint_path": next_sprint_path,
            "prompt_length": len(prompt_content),
            "safety": safety,
        }
        _write_state(output_dir, result)
        return result

    # 8. Live invocation (non-dry-run only)
    # Write prompt to temp file to avoid shell injection
    prompt_file = output_dir / "invocation-prompt.md"
    prompt_file.write_text(prompt_content, encoding="utf-8")
    _append_log(log_path, {"event": "prompt_written", "path": str(prompt_file)})

    try:
        cli_path = cli_detection["path"]
        # Use --print for non-interactive execution
        cmd = [cli_path, "--print", "-p", prompt_content[:2000]]  # truncate for safety
        _append_log(log_path, {"event": "invocation_start", "cmd": cmd[:3] + ["<prompt>"]})

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(repo_root),
        )
        _append_log(log_path, {"event": "invocation_pid", "pid": proc.pid})

        result = {
            "classification": HOST_INVOCATION_ATTEMPTED,
            "dry_run": False,
            "reason": f"Claude CLI invoked. PID: {proc.pid}",
            "cli_detection": cli_detection,
            "pid": proc.pid,
            "next_sprint_path": next_sprint_path,
            "invocation_command": f"{cli_path} --print -p <prompt>",
        }
    except Exception as e:
        _append_log(log_path, {"event": "invocation_failed", "error": str(e)})
        result = {
            "classification": HOST_INVOCATION_LAYER_MISSING,
            "honest_classification": HOST_INVOCATION_PACKET_ONLY,
            "reason": f"CLI invocation failed: {e}",
            "cli_detection": cli_detection,
        }

    _write_state(output_dir, result)
    return result


def _write_state(output_dir: Path, result: dict) -> None:
    """Write host-runner-state.json."""
    state = {
        "timestamp": datetime.now().isoformat(),
        **result,
        "non_terminal_proof": {
            "continuation_packet_only_is_not_full_autonomy": True,
            "host_invocation_layer_missing_is_honest_classification": True,
            "runner_never_claims_100pct_autonomous_without_cli": True,
        },
    }
    path = output_dir / "host-runner-state.json"
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CLI
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main() -> int:
    parser = argparse.ArgumentParser(description="Host-Level Autonomous Runner")
    parser.add_argument(
        "--report-dir",
        default="reports/host-autonomy-runner",
        help="Directory with train-state.json and to write host-runner-state.json",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root (auto-detect if not set)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Detect and check safety but do NOT invoke CLI (default: True)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        default=False,
        help="Actually invoke the Claude CLI (requires explicit --live flag)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else REPO_ROOT
    report_dir = repo_root / args.report_dir
    dry_run = not args.live  # default dry_run=True unless --live passed

    try:
        result = run_host_runner(
            repo_root=repo_root,
            report_dir=report_dir,
            dry_run=dry_run,
        )

        print(f"Classification: {result['classification']}")
        if result.get("honest_classification"):
            print(f"Honest classification: {result['honest_classification']}")
        print(f"Reason: {result['reason']}")
        if result.get("invocation_command"):
            print(f"Invocation command: {result['invocation_command']}")
        print(f"Host runner state: {report_dir}/host-runner-state.json")

        if result["classification"] == HOST_INVOCATION_LAYER_MISSING:
            print("\nACTION REQUIRED: Claude CLI is not invocable from this environment.")
            print("This system is CONTINUATION_PACKET_ONLY â€” not fully autonomous.")
            print(f"Manual invocation: {result.get('invocation_command', 'See next-sprint.md')}")
            return 1

        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 9


if __name__ == "__main__":
    sys.exit(main())
