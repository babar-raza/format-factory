"""
sprint_executor.py — Autonomous Loop Actuator for format-factory

Provides the missing "actuator" layer: check_continuation.py and autonomous_cycle.py
produce signals but nothing re-invokes Claude for the next sprint. This tool closes that
gap with a run-loop subcommand that calls `claude --print --dangerously-skip-permissions`
as a subprocess (same pattern as aspose.org sprint_loop.py).

Subcommands:
  inject-declaration <sprint_id>   Pre-create skeleton evidence-declaration.yaml
  run-sprint <sprint_id>           Invoke claude --print headlessly, capture output
  run-loop [--max-cycles N]        Full autonomous cycle loop (check → sprint → closeout → repeat)
  build-review-package             Wrapper for build_declaration_review_package.py
  status                           Print current continuation signal as JSON

Exit codes:
  0  — success / loop completed normally
  1  — hard stop or external gate
  2  — claude CLI not found (run-sprint/run-loop only)
  9  — unexpected error

Usage:
  python tools/supervisor/sprint_executor.py inject-declaration sprint-20260616-abc1234
  python tools/supervisor/sprint_executor.py status
  python tools/supervisor/sprint_executor.py run-loop --max-cycles 3
  python tools/supervisor/sprint_executor.py build-review-package --declaration .local/evidences/.../evidence-declaration.yaml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent

# Required fields from evidence-declaration.schema.json
_REQUIRED_FIELDS = [
    "run_id", "sprint_id", "evidence_root",
    "start_time", "end_time",
    "git_head_start", "git_head_end", "git_status_final",
    "declared_scope",
    "planned_work_items", "completed_work_items", "incomplete_work_items",
    "changed_files", "tests_run", "test_results",
    "evidence_artifacts", "reports_created",
    "worker_self_verdict", "worker_self_grade",
    "next_recommended_work",
]

_TRUE_EXTERNAL_GATES = {
    "EXTERNAL_GATE",
    "NO_EXTERNAL_GATE",
    "GATE_11_APPROVAL",
    "GIT_PUSH_CREDENTIALS",
    "PUBLICATION_CREDENTIALS",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _git(args: list[str], *, cwd: Path = _REPO) -> str:
    """Run a git command and return stdout stripped. Returns '' on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write(path: Path, text: str) -> None:
    """Write atomically: tmp → fsync → os.replace()."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        data = text.encode("utf-8")
        with open(tmp, "wb") as tmp_fd:
            tmp_fd.write(data)
            try:
                os.fsync(tmp_fd.fileno())
            except OSError:
                pass  # fsync best-effort on Windows
        os.replace(str(tmp), str(path))
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_continuation_signal(repo_root: Path) -> dict | None:
    p = repo_root / ".local" / "supervisor" / "continuation-signal.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _check_continuation(repo_root: Path) -> dict:
    """Run check_continuation.py and return parsed output dict."""
    result = subprocess.run(
        [sys.executable,
         str(repo_root / "tools" / "supervisor" / "check_continuation.py"),
         "--repo-root", str(repo_root)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    try:
        data = json.loads(result.stdout)
    except Exception:
        data = {
            "verdict": "STOP",
            "reason": "PARSE_ERROR",
            "detail": result.stdout[:500] or result.stderr[:500],
        }
    data["_exit_code"] = result.returncode
    return data


def _is_external_gate(stop_reason: str) -> bool:
    """Return True if stop_reason represents a TRUE_EXTERNAL_GATE."""
    if not stop_reason:
        return False
    upper = stop_reason.upper()
    if any(gate in upper for gate in _TRUE_EXTERNAL_GATES):
        return True
    # Git push and package pub blockers are external gates
    external_markers = ["GIT_PUSH", "PUSH_CREDENTIALS", "PYPI", "NUGET", "GATE_11"]
    return any(m in upper for m in external_markers)


# ---------------------------------------------------------------------------
# inject-declaration
# ---------------------------------------------------------------------------

def cmd_inject_declaration(sprint_id: str, repo_root: Path) -> Path:
    """
    Pre-create a skeleton evidence-declaration.yaml for the given sprint_id.
    All 21 required fields are present with empty/default values.
    The worker (Claude) fills in the specifics after completing the sprint.

    Returns the path to the created skeleton file.
    """
    git_head = _git(["rev-parse", "HEAD"], cwd=repo_root) or "unknown"
    short_sha = git_head[:7] if git_head != "unknown" else "unknown"
    git_status = _git(["status", "--short"], cwd=repo_root) or ""
    now = _now_iso()

    run_id = f"{sprint_id}-{short_sha}"
    evidence_root = f".local/evidences/{run_id}/"
    evidence_dir = repo_root / ".local" / "evidences" / run_id
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Read next-sprint.md to extract scope hint
    next_sprint_path = repo_root / "reports" / "supervisor" / "next-sprint.md"
    declared_scope = "Execute next sprint from reports/supervisor/next-sprint.md"
    if next_sprint_path.exists():
        first_lines = next_sprint_path.read_text(encoding="utf-8")[:400].strip()
        # Use first non-empty heading or first line
        for line in first_lines.splitlines():
            line = line.strip().lstrip("#").strip()
            if line:
                declared_scope = line[:200]
                break

    skeleton = {
        "run_id": run_id,
        "sprint_id": sprint_id,
        "evidence_root": evidence_root,
        "start_time": now,
        "end_time": now,  # worker updates this at end
        "git_head_start": git_head,
        "git_head_end": git_head,  # worker updates after work
        "git_status_final": git_status,
        "declared_scope": declared_scope,
        "planned_work_items": [],     # worker fills these in
        "completed_work_items": [],   # list of item_id strings
        "incomplete_work_items": [],
        "changed_files": [],
        "tests_run": 0,
        "test_results": {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
        },
        "evidence_artifacts": [],
        "reports_created": [],
        "worker_self_verdict": "PENDING — fill in after sprint execution",
        "worker_self_grade": "PASS",
        "next_recommended_work": [],
        # Optional but commonly used
        "known_limitations": [],
        "external_gates": [],
    }

    declaration_path = evidence_dir / "evidence-declaration.yaml"
    _atomic_write(declaration_path, yaml.dump(skeleton, default_flow_style=False, sort_keys=False))

    abs_path = declaration_path.resolve()
    print(f"Skeleton declaration created: {abs_path}")
    print(f"Run ID: {run_id}")
    print(f"Evidence root: {evidence_dir.resolve()}")
    print()
    print("Next steps:")
    print("  1. Execute the sprint tasks from reports/supervisor/next-sprint.md")
    print("  2. Edit the declaration to record what you did")
    print(f"  3. Run: python tools/supervisor/autonomous_cycle.py --declaration {abs_path}")
    return declaration_path


# ---------------------------------------------------------------------------
# build-review-package
# ---------------------------------------------------------------------------

def cmd_build_review_package(declaration_path: Path, repo_root: Path) -> int:
    """Wrapper around build_declaration_review_package.py. Prints abs path + SHA-256."""
    builder = repo_root / "tools" / "supervisor" / "build_declaration_review_package.py"
    if not builder.exists():
        print(f"ERROR: build_declaration_review_package.py not found at {builder}", file=sys.stderr)
        return 9

    result = subprocess.run(
        [sys.executable, str(builder), "--declaration", str(declaration_path.resolve()),
         "--repo-root", str(repo_root)],
        capture_output=False,  # let stdout/stderr pass through
        timeout=120,
    )

    # Compute SHA-256 of the output ZIP if we can find it
    try:
        with open(declaration_path, encoding="utf-8") as f:
            decl = yaml.safe_load(f)
        run_id = decl.get("run_id", "unknown")
        zip_path = repo_root / ".local" / "supervisor" / "reviews" / run_id / "declaration-review-package.zip"
        if zip_path.exists():
            sha = _sha256(zip_path)
            abs_zip = zip_path.resolve()
            print(f"\nAbsolute path: {abs_zip}")
            print(f"SHA-256: {sha}")
    except Exception:
        pass

    return result.returncode


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

def cmd_status(repo_root: Path) -> int:
    signal = _load_continuation_signal(repo_root)
    if signal is None:
        print(json.dumps({"error": "continuation-signal.json not found"}, indent=2))
        return 1

    # Enrich with check_continuation verdict
    cont = _check_continuation(repo_root)
    output = {
        "continuation_signal": signal,
        "check_continuation": cont,
        "verdict": cont.get("verdict", "UNKNOWN"),
    }
    print(json.dumps(output, indent=2))
    return 0 if cont.get("verdict") == "CONTINUE" else 1


# ---------------------------------------------------------------------------
# run-sprint (headless)
# ---------------------------------------------------------------------------

def cmd_run_sprint(sprint_id: str, repo_root: Path, *, dry_run: bool = False) -> dict:
    """
    Invoke `claude --print --dangerously-skip-permissions` with next-sprint.md as the prompt.
    Captures output to evidence dir.

    Returns dict with keys: exit_code, declaration_path, output_path
    """
    # 1. Inject skeleton declaration
    declaration_path = cmd_inject_declaration(sprint_id, repo_root)

    # 2. Read next-sprint.md
    next_sprint_path = repo_root / "reports" / "supervisor" / "next-sprint.md"
    if not next_sprint_path.exists():
        print(f"ERROR: next-sprint.md not found at {next_sprint_path}", file=sys.stderr)
        return {"exit_code": 9, "declaration_path": str(declaration_path)}

    prompt_text = next_sprint_path.read_text(encoding="utf-8")

    # 3. Append declaration path hint to prompt so Claude knows where to write evidence
    abs_decl = declaration_path.resolve()
    prompt_text += (
        f"\n\n---\n"
        f"DECLARATION SKELETON PRE-CREATED: {abs_decl}\n"
        f"Fill this file in after executing the sprint. "
        f"Then run: python tools/supervisor/autonomous_cycle.py --declaration {abs_decl}\n"
    )

    # Write prompt to temp file so we can pass it via @file syntax
    with open(declaration_path.parent / "sprint-prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt_text)

    output_path = declaration_path.parent / "sprint-output.txt"

    if dry_run:
        print("[DRY RUN] Would invoke: claude --print --dangerously-skip-permissions -p <next-sprint.md>")
        print(f"Declaration skeleton: {abs_decl}")
        print(f"Output would be written to: {output_path.resolve()}")
        return {"exit_code": 0, "declaration_path": str(abs_decl), "dry_run": True}

    # 4. Invoke claude
    print(f"Invoking claude CLI for sprint: {sprint_id}")
    print(f"Output: {output_path.resolve()}")
    try:
        result = subprocess.run(
            ["claude", "--print", "--dangerously-skip-permissions", "-p", prompt_text],
            capture_output=True,
            text=True,
            timeout=1800,  # 30 min max per sprint
            cwd=str(repo_root),
        )
    except FileNotFoundError:
        print(
            "ERROR: 'claude' CLI not found in PATH.\n"
            "Install it with: npm install -g @anthropic-ai/claude-code\n"
            "Or run /autonomous-loop in VSCode instead.",
            file=sys.stderr,
        )
        return {"exit_code": 2, "declaration_path": str(abs_decl)}
    except subprocess.TimeoutExpired:
        print("ERROR: claude CLI timed out after 30 minutes", file=sys.stderr)
        return {"exit_code": 9, "declaration_path": str(abs_decl)}

    # 5. Save output
    _atomic_write(output_path, result.stdout + "\n\n--- STDERR ---\n" + result.stderr)
    print(f"Claude exit code: {result.returncode}")
    print(f"Output saved to: {output_path.resolve()}")

    return {
        "exit_code": result.returncode,
        "declaration_path": str(abs_decl),
        "output_path": str(output_path.resolve()),
    }


# ---------------------------------------------------------------------------
# run-loop
# ---------------------------------------------------------------------------

def cmd_run_loop(repo_root: Path, *, max_cycles: int = 12, dry_run: bool = False) -> int:
    """
    Full autonomous loop:
      1. check_continuation → if STOP & external gate → exit 1
      2. inject-declaration
      3. run-sprint (claude --print) — skipped if dry_run
      4. run autonomous_cycle.py closeout
      5. Repeat until STOP or max_cycles

    CLAUDE.md Supreme Directive: max_cycles is NOT a hard stop —
    when reached, log it and continue (governed rollover, matching autonomous_cycle.py behaviour).
    """
    cycle = 0
    autonomous_cycle = repo_root / "tools" / "supervisor" / "autonomous_cycle.py"

    while True:
        cycle += 1
        print(f"\n{'='*60}")
        print(f"AUTONOMOUS LOOP — Cycle {cycle}")
        print(f"{'='*60}")

        # --- Step 1: Check continuation ---
        print("\n[Step 1] Checking continuation signal...")
        cont = _check_continuation(repo_root)
        verdict = cont.get("verdict", "STOP")
        print(json.dumps(cont, indent=2))

        if verdict == "STOP":
            reason = cont.get("reason", "")
            if _is_external_gate(reason):
                print(f"\nHARD STOP: TRUE_EXTERNAL_GATE — {reason}")
                print("This requires human action. Stopping.")
                return 1
            else:
                # Supreme Directive: non-external-gate stops are overridden
                print(f"\nNOTE: check_continuation returned STOP ({reason}) — not an external gate.")
                print("Supreme Directive: overriding, reading next-sprint.md directly.")
                next_sprint_path = repo_root / "reports" / "supervisor" / "next-sprint.md"
                if not next_sprint_path.exists():
                    print("ERROR: next-sprint.md not found and no continuation signal. Cannot proceed.")
                    return 1

        # Max cycles: governed rollover (not a hard stop)
        iteration = cont.get("iteration", 0)
        max_iterations = cont.get("max_iterations", 12)
        if cycle > max_cycles:
            print(f"\nNOTE: cycle {cycle} > max_cycles {max_cycles} — governed rollover, continuing.")
            # Reset signal iteration if possible
            sig_path = repo_root / ".local" / "supervisor" / "continuation-signal.json"
            if sig_path.exists():
                try:
                    sig = json.loads(sig_path.read_text(encoding="utf-8"))
                    sig["iteration"] = 0
                    _atomic_write(sig_path, json.dumps(sig, indent=2))
                    print("Iteration counter reset to 0.")
                except Exception as e:
                    print(f"Could not reset iteration: {e}")

        # --- Step 2+3: Run sprint ---
        now = datetime.now(timezone.utc)
        sprint_id = f"autonomous-loop-{now.strftime('%Y%m%d-%H%M%S')}"
        print(f"\n[Step 2+3] Running sprint: {sprint_id}")
        sprint_result = cmd_run_sprint(sprint_id, repo_root, dry_run=dry_run)

        if sprint_result.get("exit_code", 9) == 2:
            print("\nClaude CLI not available. Cannot run headlessly.")
            print("Use /autonomous-loop in VSCode for interactive execution.")
            return 2

        if dry_run:
            print("\n[DRY RUN] Skipping closeout step.")
            print("Run without --dry-run to execute the full loop.")
            return 0

        # --- Step 4: Closeout via autonomous_cycle.py ---
        declaration_path = sprint_result.get("declaration_path")
        if declaration_path and Path(declaration_path).exists():
            print(f"\n[Step 4] Running closeout: autonomous_cycle.py")
            closeout = subprocess.run(
                [sys.executable, str(autonomous_cycle),
                 "--declaration", declaration_path,
                 "--repo-root", str(repo_root)],
                capture_output=False,
                timeout=300,
                cwd=str(repo_root),
            )
            closeout_exit = closeout.returncode
            print(f"Closeout exit code: {closeout_exit}")

            if closeout_exit not in (0, 3):
                print(f"NOTE: Closeout returned {closeout_exit} — logging and continuing (Supreme Directive).")

            # Build review package (best-effort)
            try:
                cmd_build_review_package(Path(declaration_path), repo_root)
            except Exception as e:
                print(f"Review package build failed (non-blocking): {e}")
        else:
            print("\nNOTE: No declaration path from run-sprint. Closeout skipped.")

        print(f"\nCycle {cycle} complete.")

    # Unreachable — loop exits via return statements above
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Autonomous loop actuator — the missing run-loop for format-factory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--repo-root", type=Path, default=_REPO,
                        help="Repository root (default: auto-detected)")

    sub = parser.add_subparsers(dest="command", required=True)

    # inject-declaration
    p_inj = sub.add_parser("inject-declaration",
                            help="Pre-create skeleton evidence-declaration.yaml")
    p_inj.add_argument("sprint_id", help="Sprint ID (e.g. product-deepening-sprint12-20260616)")

    # status
    sub.add_parser("status", help="Print current continuation signal")

    # build-review-package
    p_pkg = sub.add_parser("build-review-package",
                            help="Build declaration review ZIP (wrapper)")
    p_pkg.add_argument("--declaration", type=Path, required=True,
                       help="Path to evidence-declaration.yaml")

    # run-sprint
    p_run = sub.add_parser("run-sprint",
                            help="Invoke claude --print headlessly for one sprint")
    p_run.add_argument("sprint_id", help="Sprint ID")
    p_run.add_argument("--dry-run", action="store_true",
                       help="Show what would happen without invoking claude")

    # run-loop
    p_loop = sub.add_parser("run-loop",
                             help="Full autonomous loop (check → sprint → closeout → repeat)")
    p_loop.add_argument("--max-cycles", type=int, default=12,
                        help="Max loop cycles before governed rollover (default: 12)")
    p_loop.add_argument("--dry-run", action="store_true",
                        help="Run checks and inject-declaration without invoking claude")

    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    if args.command == "inject-declaration":
        cmd_inject_declaration(args.sprint_id, repo_root)
        return 0

    elif args.command == "status":
        return cmd_status(repo_root)

    elif args.command == "build-review-package":
        decl = args.declaration
        if not decl.is_absolute():
            decl = Path.cwd() / decl
        return cmd_build_review_package(decl, repo_root)

    elif args.command == "run-sprint":
        result = cmd_run_sprint(args.sprint_id, repo_root, dry_run=args.dry_run)
        return result.get("exit_code", 0)

    elif args.command == "run-loop":
        return cmd_run_loop(repo_root, max_cycles=args.max_cycles, dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
