"""
supervisor_loop.py — Format Factory Local Supervisor Control Plane
Orchestrates all supervisor sub-scripts in sequence.

Sub-commands:
  discover          — find latest evidence bundle
  review            — validate bundle and extract facts
  next              — generate next-sprint artifacts
  run-on-latest     — full pipeline: discover → review → next → memory-sync
  export-taskmaster — export next-sprint-taskmaster.json
  export-ruflo      — export next-ruflo-lanes.json

Exit codes:
  0 — success
  1 — no bundle found
  2 — validation failed / malformed bundle
  3 — critical contradiction (autonomous loop stopped)
  9 — unexpected error

Usage:
  python tools/supervisor/supervisor_loop.py discover
  python tools/supervisor/supervisor_loop.py review --bundle path/to/bundle.zip
  python tools/supervisor/supervisor_loop.py next --bundle path/to/bundle.zip
  python tools/supervisor/supervisor_loop.py run-on-latest
  python tools/supervisor/supervisor_loop.py run-on-latest --bundle path/to/explicit.zip
  python tools/supervisor/supervisor_loop.py export-taskmaster
  python tools/supervisor/supervisor_loop.py export-ruflo
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
STATE_DIR = REPO_ROOT / ".supervisor" / "state"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "supervisor"


def run_script(script_name: str, extra_args: list[str], repo_root: Path) -> subprocess.CompletedProcess:
    """Run a supervisor sub-script as subprocess."""
    script_path = SCRIPT_DIR / script_name
    cmd = [sys.executable, str(script_path)] + extra_args
    result = subprocess.run(
        cmd,
        capture_output=False,  # Let output stream to terminal
        text=True,
        cwd=str(repo_root),
        timeout=120,
    )
    return result


def run_script_capture(script_name: str, extra_args: list[str], repo_root: Path) -> tuple[int, str, str]:
    """Run a supervisor sub-script capturing output."""
    script_path = SCRIPT_DIR / script_name
    cmd = [sys.executable, str(script_path)] + extra_args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        timeout=120,
    )
    return result.returncode, result.stdout, result.stderr


def load_current_run() -> dict:
    """Load .supervisor/state/current-run.json if it exists."""
    state_file = STATE_DIR / "current-run.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_run_state(state: dict) -> None:
    """Save run state to .supervisor/state/current-run.json."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_file = STATE_DIR / "current-run.json"
    existing = load_current_run()
    existing.update(state)
    state_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def cmd_discover(args) -> int:
    """Discover latest evidence bundle."""
    print("=== SUPERVISOR: DISCOVER ===")
    extra = ["--repo-root", str(REPO_ROOT), "--output-dir", str(args.output_dir)]
    if args.bundle:
        extra += ["--path", str(args.bundle)]

    rc, stdout, stderr = run_script_capture(
        "discover_latest_evidence.py", extra, REPO_ROOT
    )

    print(stdout, end="")
    if stderr:
        print(stderr, end="", file=sys.stderr)

    # Read and persist discovery result
    state = load_current_run()
    if "last_discovery" in state:
        disc = state["last_discovery"]
        bundle_path = disc.get("bundle_path", "")
        sprint_id = disc.get("sprint_id", "unknown")
        save_run_state({
            "discover_exit_code": rc,
            "bundle_path": bundle_path,
            "sprint_id": sprint_id,
            "discover_timestamp": datetime.now().isoformat(),
        })
        if rc == 0:
            print("  -> Bundle path saved to .supervisor/state/current-run.json")

    return rc


def cmd_review(args) -> int:
    """Validate bundle and extract facts."""
    print("=== SUPERVISOR: REVIEW ===")

    bundle = args.bundle
    if not bundle:
        # Try to get from state
        state = load_current_run()
        bundle = state.get("bundle_path")
        if not bundle:
            print("ERROR: No bundle path. Run 'discover' first or provide --bundle.", file=sys.stderr)
            return 1

    extra = [
        "--bundle", str(bundle),
        "--output-dir", str(args.output_dir),
        "--repo-root", str(REPO_ROOT),
    ]
    rc = run_script("validate_evidence_for_supervisor.py", extra, REPO_ROOT).returncode

    if rc != 0:
        print(f"ERROR: Evidence validation failed (exit {rc})")
        return rc

    # Run contradiction detection
    print()
    print("=== SUPERVISOR: CONTRADICTION DETECTION ===")
    review_json = args.output_dir / "evidence-review.json"
    if review_json.exists():
        extra2 = [
            "--review", str(review_json),
            "--output-dir", str(args.output_dir),
            "--repo-root", str(REPO_ROOT),
        ]
        rc2 = run_script("compare_goal_to_evidence.py", extra2, REPO_ROOT).returncode

        # Check if critical contradictions were found
        contradictions_json = args.output_dir / "contradictions.json"
        if contradictions_json.exists():
            try:
                contra = json.loads(contradictions_json.read_text(encoding="utf-8"))
                save_run_state({
                    "review_exit_code": rc,
                    "contradiction_exit_code": rc2,
                    "critical_contradictions": contra.get("critical_count", 0),
                    "autonomous_continue": contra.get("autonomous_continue", True),
                    "review_timestamp": datetime.now().isoformat(),
                })
                if contra.get("critical_count", 0) > 0:
                    print(f"\n⚠ CRITICAL CONTRADICTIONS: {contra['critical_count']} — autonomous loop paused")
                    return 3
            except Exception:
                pass

    return rc


def cmd_next(args) -> int:
    """Generate next-sprint artifacts."""
    print("=== SUPERVISOR: NEXT SPRINT GENERATION ===")
    extra = [
        "--review", str(args.output_dir / "evidence-review.json"),
        "--contradictions", str(args.output_dir / "contradictions.json"),
        "--output-dir", str(args.output_dir),
        "--repo-root", str(REPO_ROOT),
    ]
    rc = run_script("generate_supervisor_packet.py", extra, REPO_ROOT).returncode

    save_run_state({
        "next_exit_code": rc,
        "next_timestamp": datetime.now().isoformat(),
    })
    return rc


def cmd_memory_sync(args) -> int:
    """Sync memory."""
    print("=== SUPERVISOR: MEMORY SYNC ===")
    extra = [
        "--review", str(args.output_dir / "evidence-review.json"),
        "--output-dir", str(args.output_dir),
        "--repo-root", str(REPO_ROOT),
    ]
    rc = run_script("sync_local_memory.py", extra, REPO_ROOT).returncode
    save_run_state({
        "memory_sync_exit_code": rc,
        "memory_sync_timestamp": datetime.now().isoformat(),
    })
    return rc


def cmd_run_on_latest(args) -> int:
    """Full pipeline: discover → review → next → export → memory-sync."""
    print("=" * 60)
    print("SUPERVISOR LOOP: RUN-ON-LATEST")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    save_run_state({"run_start": datetime.now().isoformat(), "sprint_id": "in-progress"})

    # Step 1: Discover
    rc = cmd_discover(args)
    if rc == 1:
        print("\nSUPERVISOR RESULT: NO_BUNDLE_FOUND")
        print("  Run with a real evidence bundle in .local/evidence/")
        save_run_state({"final_exit_code": 1, "run_end": datetime.now().isoformat()})
        return 1
    if rc == 2:
        print("\nSUPERVISOR RESULT: MALFORMED_BUNDLE")
        save_run_state({"final_exit_code": 2, "run_end": datetime.now().isoformat()})
        return 2

    # Update args.bundle from state if not set
    if not args.bundle:
        state = load_current_run()
        bundle_path = state.get("bundle_path")
        if bundle_path:
            args.bundle = Path(bundle_path)

    # Step 2: Review + contradiction detection
    print()
    rc = cmd_review(args)
    if rc == 3:
        print("\nSUPERVISOR RESULT: CRITICAL_CONTRADICTIONS — human review required")
        # Still generate next-sprint (focused on repair)
        cmd_next(args)
        cmd_memory_sync(args)
        save_run_state({"final_exit_code": 3, "run_end": datetime.now().isoformat()})
        return 3
    if rc not in (0, 2):
        # Partial failures allowed — continue
        pass

    # Step 3: Generate next-sprint artifacts
    print()
    rc_next = cmd_next(args)

    # Step 4: Memory sync
    print()
    cmd_memory_sync(args)

    # Final state
    final_rc = rc_next if rc_next != 0 else 0
    save_run_state({
        "final_exit_code": final_rc,
        "run_end": datetime.now().isoformat(),
    })

    print()
    print("=" * 60)
    print(f"SUPERVISOR LOOP: COMPLETE (exit {final_rc})")
    print(f"Ended: {datetime.now().isoformat()}")
    print(f"Outputs: {args.output_dir}")
    print("=" * 60)

    return final_rc


def cmd_export_taskmaster(args) -> int:
    """Export next-sprint-taskmaster.json."""
    tm_path = args.output_dir / "next-sprint-taskmaster.json"
    if tm_path.exists():
        print(f"EXPORT_TASKMASTER: {tm_path}")
        print(f"  Size: {tm_path.stat().st_size} bytes")
        return 0
    print("ERROR: next-sprint-taskmaster.json not found. Run 'run-on-latest' first.", file=sys.stderr)
    return 1


def cmd_export_ruflo(args) -> int:
    """Export next-ruflo-lanes.json."""
    ruflo_path = args.output_dir / "next-ruflo-lanes.json"
    if ruflo_path.exists():
        print(f"EXPORT_RUFLO: {ruflo_path}")
        print(f"  Size: {ruflo_path.stat().st_size} bytes")
        return 0
    print("ERROR: next-ruflo-lanes.json not found. Run 'run-on-latest' first.", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Format Factory Local Supervisor Control Plane — Orchestrator"
    )
    parser.add_argument(
        "command",
        choices=["discover", "review", "next", "run-on-latest", "export-taskmaster", "export-ruflo"],
        help="Sub-command to run",
    )
    parser.add_argument("--bundle", type=Path, help="Explicit evidence bundle path")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for supervisor artifacts",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (default: auto-detected)",
    )
    parser.add_argument("--json", action="store_true", help="JSON output mode")

    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    command_map = {
        "discover": cmd_discover,
        "review": cmd_review,
        "next": cmd_next,
        "run-on-latest": cmd_run_on_latest,
        "export-taskmaster": cmd_export_taskmaster,
        "export-ruflo": cmd_export_ruflo,
    }

    try:
        return command_map[args.command](args)
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        return 9
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 9


if __name__ == "__main__":
    sys.exit(main())
